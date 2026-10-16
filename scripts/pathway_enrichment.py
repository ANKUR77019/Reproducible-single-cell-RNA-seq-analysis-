from pathlib import Path
import pandas as pd
import gseapy as gp

out = Path("results/analysis")
df = pd.read_csv(out / "cluster_marker_genes_full.csv")

# Keep significant, positively enriched marker genes
df["pvals_adj"] = pd.to_numeric(df["pvals_adj"], errors="coerce")
df["logfoldchanges"] = pd.to_numeric(df["logfoldchanges"], errors="coerce")

for cluster in sorted(df["group"].dropna().unique(), key=str):
    sub = df[
        (df["group"].astype(str) == str(cluster)) &
        (df["pvals_adj"] < 0.05) &
        (df["logfoldchanges"] > 0.25)
    ]
    genes = sub["names"].dropna().astype(str).unique().tolist()

    if len(genes) < 5:
        print(f"Cluster {cluster}: too few significant markers; skipped.")
        continue

    result = gp.enrichr(
        gene_list=genes,
        gene_sets=["GO_Biological_Process_2023"],
        organism="human",
        outdir=None,
        cutoff=0.05
    )

    table = result.results
    if table is not None and not table.empty:
        table.to_csv(out / f"pathways_cluster_{cluster}.csv", index=False)
        print(f"Cluster {cluster}: tested {len(genes)} markers; saved pathway results.")
    else:
        print(f"Cluster {cluster}: no enriched pathways returned.")

print("Pathway enrichment finished.")
