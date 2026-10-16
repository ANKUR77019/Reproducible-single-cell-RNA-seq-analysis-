from pathlib import Path
import scanpy as sc

out = Path("results/analysis")
adata = sc.read_h5ad(out / "pbmc_clustered.h5ad")

# Restore unscaled counts and normalize for marker testing
adata.X = adata.layers["counts"].copy()
sc.pp.normalize_total(adata, target_sum=10000)
sc.pp.log1p(adata)

# Rank marker genes by cluster
sc.tl.rank_genes_groups(
    adata,
    groupby="leiden",
    method="wilcoxon",
    use_raw=False
)

markers = sc.get.rank_genes_groups_df(adata, group=None)
markers.to_csv(out / "cluster_marker_genes.csv", index=False)

print("Marker analysis complete.")
for cluster in sorted(markers["group"].unique(), key=str):
    top = markers[markers["group"] == cluster].head(5)
    print(f"\nCluster {cluster}:")
    print(top[["names", "logfoldchanges", "pvals_adj"]].to_string(index=False))

print("\nSaved results/analysis/cluster_marker_genes.csv")
