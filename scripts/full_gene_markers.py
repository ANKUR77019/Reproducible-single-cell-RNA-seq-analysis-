from pathlib import Path
import scanpy as sc

out = Path("results/analysis")
data = "data/processed/filtered_feature_bc_matrix"

# Load original full-gene count matrix
full = sc.read_10x_mtx(
    data, var_names="gene_symbols", make_unique=True
)

# Get QC-passing cells and their cluster labels
clustered = sc.read_h5ad(out / "pbmc_clustered.h5ad")
common = full.obs_names.intersection(clustered.obs_names)

full = full[common].copy()
full.obs["leiden"] = clustered.obs.loc[common, "leiden"].astype("category")

# Normalize original counts and log-transform once
sc.pp.normalize_total(full, target_sum=10000)
sc.pp.log1p(full)

# Rank marker genes across the full gene set
sc.tl.rank_genes_groups(
    full,
    groupby="leiden",
    method="wilcoxon",
    use_raw=False
)

markers = sc.get.rank_genes_groups_df(full, group=None)
markers.to_csv(out / "cluster_marker_genes_full.csv", index=False)

print("Cells:", full.n_obs)
print("Genes tested:", full.n_vars)
print("Marker rows:", len(markers))
print("Saved:", out / "cluster_marker_genes_full.csv")
