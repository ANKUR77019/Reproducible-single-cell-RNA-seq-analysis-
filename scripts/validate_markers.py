from pathlib import Path
import scanpy as sc
import pandas as pd

out = Path("results/analysis")
adata = sc.read_h5ad(out / "pbmc_clustered.h5ad")

# Canonical markers for major PBMC populations
marker_sets = {
    "T cells": ["CD3D", "CD3E", "TRAC", "IL7R", "CD4", "CD8A"],
    "B cells": ["MS4A1", "CD79A", "CD79B", "CD74", "CD37"],
    "NK cells": ["GNLY", "NKG7", "KLRD1", "PRF1", "FCGR3A"],
    "Monocytes": ["LYZ", "LST1", "S100A8", "S100A9", "FCN1", "FCGR3A"],
    "Dendritic cells": ["FCER1A", "CD1C", "CLEC10A"],
    "Platelets": ["PPBP", "PF4"],
}

# Use normalized log-expression for visualization and summaries.
# This file contains scaled values, so use the preserved counts layer.
adata.X = adata.layers["counts"].copy()
sc.pp.normalize_total(adata, target_sum=10000)
sc.pp.log1p(adata)

available = set(adata.var_names)
rows = []

for cluster in sorted(adata.obs["leiden"].astype(str).unique(), key=int):
    cells = adata.obs["leiden"].astype(str) == cluster
    for cell_type, genes in marker_sets.items():
        present = [g for g in genes if g in available]
        if not present:
            continue
        means = adata[cells, present].X.mean(axis=0)
        if hasattr(means, "A1"):
            means = means.A1
        elif hasattr(means, "toarray"):
            means = means.toarray().ravel()
        for gene, mean_expr in zip(present, means):
            rows.append({
                "cluster": cluster,
                "marker_group": cell_type,
                "gene": gene,
                "mean_log_expression": float(mean_expr),
            })

df = pd.DataFrame(rows)
df.to_csv(out / "canonical_marker_validation.csv", index=False)

print("Mean log-expression of canonical markers by cluster")
print(df.pivot_table(
    index=["cluster", "marker_group"],
    columns="gene",
    values="mean_log_expression",
    fill_value=0
).round(2).to_string())
print("\nSaved results/analysis/canonical_marker_validation.csv")
