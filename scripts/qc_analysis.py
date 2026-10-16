from pathlib import Path
import os
import scanpy as sc
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

data_dir = Path(os.environ.get("CELLSCOPE_DATA_DIR", "data/processed/filtered_feature_bc_matrix"))
out_dir = Path("results/qc")
out_dir.mkdir(parents=True, exist_ok=True)

adata = sc.read_10x_mtx(
    data_dir,
    var_names="gene_symbols",
    make_unique=True
)

# Identify mitochondrial genes
adata.var["mt"] = adata.var_names.str.upper().str.startswith("MT-")

# Calculate cell-level QC metrics
sc.pp.calculate_qc_metrics(
    adata,
    qc_vars=["mt"],
    percent_top=None,
    log1p=False,
    inplace=True
)

# Save QC metrics before filtering
adata.obs.to_csv(out_dir / "cell_qc_metrics.csv")

# Plot basic QC distributions
fig, axes = plt.subplots(1, 3, figsize=(13, 4))
for ax, column, label in zip(
    axes,
    ["total_counts", "n_genes_by_counts", "pct_counts_mt"],
    ["Total counts per cell", "Genes detected per cell", "Mitochondrial counts (%)"]
):
    adata.obs[column].plot.hist(bins=30, ax=ax)
    ax.set_title(label)
    ax.set_xlabel(label)

fig.tight_layout()
fig.savefig(out_dir / "qc_distributions.png", dpi=150)
plt.close(fig)

with open(out_dir / "qc_summary.txt", "w") as f:
    f.write("CellScope: Single-cell QC summary\n")
    f.write(f"Cells assessed: {adata.n_obs}\n")
    f.write(f"Gene features: {adata.n_vars}\n")
    f.write(f"Median genes per cell: {adata.obs['n_genes_by_counts'].median():.1f}\n")
    f.write(f"Median counts per cell: {adata.obs['total_counts'].median():.1f}\n")
    f.write(f"Median mitochondrial percentage: {adata.obs['pct_counts_mt'].median():.2f}%\n")

print((out_dir / "qc_summary.txt").read_text())
print(f"QC outputs saved in {out_dir}")
