from pathlib import Path
import scanpy as sc
import matplotlib.pyplot as plt

out = Path("results/analysis")
adata = sc.read_h5ad(out / "pbmc_clustered.h5ad")

labels = {
    "0": "T cells",
    "1": "Inflammatory monocytes",
    "2": "S100A8/A9-high monocytes",
    "3": "B cells",
    "4": "Cytotoxic lymphocytes",
    "5": "NK-like cells",
    "6": "FCGR3A+ monocytes",
}

adata.obs["cell_type"] = (
    adata.obs["leiden"].astype(str).map(labels).fillna("Unassigned")
)

sc.pl.umap(
    adata,
    color="cell_type",
    legend_loc="right margin",
    legend_fontsize=9,
    size=28,
    alpha=0.9,
    frameon=False,
    title="PBMC Cell-Type Annotations",
    show=False,
)

fig = plt.gcf()
fig.set_size_inches(9, 5.8)
plt.savefig(out / "umap_cell_types.png", dpi=300, bbox_inches="tight")
plt.close()

adata.obs[["leiden", "cell_type"]].to_csv(
    out / "cell_type_annotations.csv"
)

print("Saved final candidate UMAP and annotation table.")
