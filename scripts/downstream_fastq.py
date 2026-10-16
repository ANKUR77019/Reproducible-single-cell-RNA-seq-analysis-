from pathlib import Path
import json
import os
import warnings

import numpy as np
import pandas as pd
import scanpy as sc
from scipy.io import mmread
from scipy import sparse

warnings.filterwarnings("ignore", category=FutureWarning)

ROOT = Path(".")
BASE = Path(os.environ.get("CELLSCOPE_MATRIX_DIR", "results/quantification/pbmc_fastq_filtered/counts_filtered"))
OUT = Path(os.environ.get("CELLSCOPE_OUTPUT_DIR", "results/fastq_analysis"))
OUT.mkdir(parents=True, exist_ok=True)

matrix_file = BASE / "cells_x_genes.mtx"
barcode_file = BASE / "cells_x_genes.barcodes.txt"
gene_file = BASE / "cells_x_genes.genes.txt"
names_file = BASE / "cells_x_genes.genes.names.txt"

for p in [matrix_file, barcode_file, gene_file, names_file]:
    if not p.exists() or p.stat().st_size == 0:
        raise FileNotFoundError(f"Missing or empty input: {p}")

# Load matrix and matching identifiers
X = mmread(matrix_file).tocsr()
barcodes = pd.read_csv(barcode_file, header=None)[0].astype(str).tolist()
gene_ids = pd.read_csv(gene_file, header=None)[0].astype(str).tolist()
gene_names = pd.read_csv(names_file, header=None)[0].astype(str).tolist()

if X.shape != (len(barcodes), len(gene_ids)):
    raise ValueError(
        f"Matrix/identifier mismatch: matrix={X.shape}, "
        f"barcodes={len(barcodes)}, genes={len(gene_ids)}"
    )

if len(gene_names) != len(gene_ids):
    raise ValueError("Gene names and gene IDs have different lengths.")

# Preserve gene IDs as unique identifiers; retain symbols as annotations.
var = pd.DataFrame(index=pd.Index(gene_ids, name="gene_id"))
var["gene_name"] = gene_names
var["gene_name_unique"] = pd.Index(gene_names).astype(str)
var["gene_name_unique"] = var["gene_name_unique"].where(
    ~var["gene_name_unique"].duplicated(),
    var["gene_name_unique"] + "_" + var.groupby("gene_name_unique").cumcount().astype(str)
)

adata = sc.AnnData(
    X=X,
    obs=pd.DataFrame(index=pd.Index(barcodes, name="barcode")),
    var=var
)
adata.var_names_make_unique()

# Basic count-based QC; avoid aggressive filtering on this small subset.
adata.var["mt"] = adata.var["gene_name"].str.upper().str.startswith("MT-")
sc.pp.calculate_qc_metrics(adata, qc_vars=["mt"], inplace=True, log1p=False)

adata.obs.to_csv(OUT / "cell_qc_metrics.csv")
adata.var.to_csv(OUT / "gene_annotations.csv")

qc = {
    "input_barcodes": int(adata.n_obs),
    "input_genes": int(adata.n_vars),
    "matrix_nonzero_entries": int(adata.X.nnz if sparse.issparse(adata.X) else np.count_nonzero(adata.X)),
    "median_genes_per_barcode": float(adata.obs["n_genes_by_counts"].median()),
    "median_UMIs_per_barcode": float(adata.obs["total_counts"].median()),
    "median_mitochondrial_percent": float(adata.obs["pct_counts_mt"].median()),
}

# Filter very low-quality barcodes and rarely detected genes.
sc.pp.filter_cells(adata, min_genes=200)
sc.pp.filter_genes(adata, min_cells=3)

if adata.n_obs < 5 or adata.n_vars < 100:
    raise ValueError(
        f"Too few observations/features after filtering: {adata.shape}. "
        "Inspect QC thresholds and input matrix."
    )

# Keep raw counts before normalization.
adata.layers["counts"] = adata.X.copy()
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
adata.raw = adata

n_top = min(2000, max(200, adata.n_vars - 1))
sc.pp.highly_variable_genes(
    adata, n_top_genes=n_top, flavor="seurat"
)
hvg = adata[:, adata.var["highly_variable"]].copy()

sc.pp.scale(hvg, max_value=10)
sc.tl.pca(hvg, svd_solver="arpack")
n_pcs = min(20, hvg.n_vars - 1, hvg.n_obs - 1)
if n_pcs < 2:
    raise ValueError("Not enough cells/features for PCA and clustering.")

sc.pp.neighbors(hvg, n_neighbors=min(10, hvg.n_obs - 1), n_pcs=n_pcs)
sc.tl.umap(hvg, random_state=42)
sc.tl.leiden(hvg, resolution=0.5, random_state=42, key_added="leiden")

# Save the processed object and basic visualizations.
hvg.write_h5ad(OUT / "pbmc_fastq_clustered.h5ad")

sc.pl.umap(
    hvg, color="leiden", show=False,
    save=None
)
import matplotlib.pyplot as plt
plt.savefig(OUT / "umap_clusters.png", dpi=180, bbox_inches="tight")
plt.close("all")

# Find cluster marker genes.
sc.tl.rank_genes_groups(
    hvg, groupby="leiden", method="wilcoxon",
    use_raw=True, pts=True
)
markers = sc.get.rank_genes_groups_df(hvg, group=None)
markers.to_csv(OUT / "cluster_marker_genes.csv", index=False)

# Export top markers per cluster for easier interpretation.
top = (
    markers.sort_values("scores", ascending=False)
    .groupby("group", sort=False)
    .head(20)
)
top.to_csv(OUT / "top_markers_per_cluster.csv", index=False)

# Summary report and machine-readable metadata.
qc.update({
    "cells_after_filtering": int(hvg.n_obs),
    "genes_after_filtering": int(hvg.n_vars),
    "highly_variable_genes": int(hvg.var["highly_variable"].sum()),
    "clusters": int(hvg.obs["leiden"].nunique()),
    "note": (
        "This analysis uses the FASTQ-derived filtered matrix. "
        "Clusters and cell identities require biological validation; "
        "barcode filtering is not proof that every barcode is a true cell."
    )
})
(OUT / "analysis_summary.json").write_text(json.dumps(qc, indent=2))

with open(OUT / "analysis_summary.txt", "w") as f:
    f.write("CellScope FASTQ-derived downstream analysis\n")
    f.write("=" * 45 + "\n")
    for key, value in qc.items():
        f.write(f"{key}: {value}\n")

print(json.dumps(qc, indent=2))
print(f"\nDownstream results saved to: {OUT}")
