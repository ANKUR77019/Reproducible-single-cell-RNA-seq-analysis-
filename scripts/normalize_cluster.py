from pathlib import Path
import scanpy as sc

out = Path("results/analysis")
out.mkdir(parents=True, exist_ok=True)

adata = sc.read_h5ad("results/qc/pbmc_filtered.h5ad")

# Preserve raw counts before normalization
adata.layers["counts"] = adata.X.copy()

# Normalize each cell to 10,000 total counts and log-transform
sc.pp.normalize_total(adata, target_sum=10000)
sc.pp.log1p(adata)

# Identify highly variable genes
sc.pp.highly_variable_genes(
    adata,
    n_top_genes=2000,
    flavor="seurat"
)

# Scale, reduce dimensions, build graph and cluster
adata = adata[:, adata.var["highly_variable"]].copy()
sc.pp.scale(adata, max_value=10)
sc.tl.pca(adata)
sc.pp.neighbors(adata, n_neighbors=10, n_pcs=30)
sc.tl.umap(adata, random_state=42)
sc.tl.leiden(adata, resolution=0.5, random_state=42)

# Save processed data and plots
adata.write_h5ad(out / "pbmc_clustered.h5ad")
sc.pl.umap(adata, color="leiden", show=False, save=None)
import matplotlib.pyplot as plt
plt.savefig(out / "umap_clusters.png", dpi=150, bbox_inches="tight")
plt.close()

adata.obs[["leiden"]].to_csv(out / "cell_clusters.csv")

print(f"Cells analyzed: {adata.n_obs}")
print(f"Highly variable genes: {adata.n_vars}")
print(f"Clusters found: {adata.obs['leiden'].nunique()}")
print(f"Outputs saved in {out}")
