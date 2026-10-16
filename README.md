# CellScope: Reproducible Single-Cell RNA-seq Analysis

CellScope is a bioinformatics portfolio project for processing and analysing single-cell RNA sequencing (scRNA-seq) data. It combines sequencing quality control, transcript quantification, cell-level quality assessment, clustering, marker-gene analysis, cell-type annotation, and pathway enrichment with workflow automation using Snakemake and Nextflow.

## Project Objectives

- Build reproducible and automated RNA-seq analysis workflows.
- Assess raw sequencing quality using FastQC and MultiQC.
- Quantify transcript abundance using kallisto|bustools (`kb`).
- Analyse cell-level expression profiles using Scanpy.
- Identify cell clusters and candidate marker genes.
- Explore cell-type identities and biological pathways.
- Organise analysis outputs for reproducibility and interpretation.

## Technologies

- **Workflow automation:** Snakemake, Nextflow
- **Sequencing QC:** FastQC, MultiQC
- **Quantification:** kb-python (kallisto|bustools)
- **Single-cell analysis:** Scanpy, AnnData
- **Programming:** Python
- **Data formats:** FASTQ, Matrix Market, CSV, H5AD
- **Environment:** Ubuntu, Python virtual environments

## Workflow Overview

```text
FASTQ files from multiple sequencing lanes
                 |
                 v
        FASTQ validation
                 |
                 v
       FastQC quality checks
                 |
                 v
       MultiQC quality report
                 |
                 v
     Transcript quantification
           using kb
                 |
                 v
     Gene-by-cell count matrix
                 |
                 v
      Scanpy downstream analysis
                 |
                 v
       Cell-level QC and filtering
                 |
                 v
       Normalisation and HVGs
                 |
                 v
          Clustering and UMAP
                 |
                 v
       Marker-gene identification
```

The project also contains a separate matrix-based analysis branch for cell-type annotation, canonical marker validation, and pathway enrichment.

## Data

The project uses PBMC single-cell RNA-seq data and includes FASTQ files split across two sequencing lanes. The sample sheet is stored at `config/samples.tsv`.

The configuration in `config/config.yaml` specifies the FASTQ directory, reference index, transcript-to-gene mapping, sequencing technology, threads, and memory settings.

Reference files and dataset provenance should be documented alongside any public repository release.

## Quality Control

FastQC was run on the four lane-level FASTQ files, with results combined using MultiQC.

Key outputs:

- `results/fastqc/` — FastQC HTML and ZIP reports
- `results/fastqc/multiqc/multiqc_report.html` — combined quality-control report

The 10x Genomics 3' v3 library configuration was used for quantification. Read structure and barcode/UMI handling were considered when configuring the workflow.

## Quantification

Transcript quantification was performed using `kb` with a human reference index and transcript-to-gene mapping.

Key output:

- `results/quantification/PBMC_1K/counts_filtered/` — filtered count matrix and associated cell/gene files

The count matrix is the input to the FASTQ-derived downstream analysis.

## Single-Cell Analysis

Scanpy was used to process the quantified expression matrix, calculate cell-level quality metrics, select highly variable genes, perform dimensionality reduction, cluster cells, and identify candidate marker genes.

The completed FASTQ-derived analysis includes:

- `results/fastq_analysis/PBMC_1K/pbmc_fastq_clustered.h5ad` — processed AnnData object
- `results/fastq_analysis/PBMC_1K/cell_qc_metrics.csv` — cell-level QC metrics
- `results/fastq_analysis/PBMC_1K/cluster_marker_genes.csv` — cluster marker results
- `results/fastq_analysis/PBMC_1K/top_markers_per_cluster.csv` — selected top markers
- `results/fastq_analysis/PBMC_1K/gene_annotations.csv` — gene annotation table
- `results/fastq_analysis/PBMC_1K/umap_clusters.png` — UMAP visualisation
- `results/fastq_analysis/PBMC_1K/analysis_summary.txt` — analysis summary

The current FASTQ-derived analysis retained 262 cells, selected 2,000 highly variable genes, and identified five clusters. These are dataset- and parameter-specific results, not universal biological conclusions.

## Cell-Type Annotation and Pathway Analysis

A separate analysis branch contains additional exploratory analyses, including cluster marker analysis, canonical marker validation, cell-type annotation, and pathway enrichment.

Relevant outputs under `results/analysis/` include:

- `cell_type_annotations.csv`
- `canonical_marker_validation.csv`
- `cluster_marker_genes.csv`
- `cluster_marker_genes_full.csv`
- `significant_pathways.csv`
- `pathway_summary.txt`
- `umap_cell_types.png`
- `umap_clusters.png`
- `marker_genes.png`
- `pathways_cluster_*.csv`

Cell-type assignments and enriched pathways should be interpreted as computational predictions that require biological validation. The matrix-based and FASTQ-derived branches have separate outputs and should not be assumed to represent identical processing runs.

## Workflow Automation

### Snakemake

The Snakemake workflow is located at `workflow/snakemake/Snakefile`.

Preview the workflow without executing jobs:

```bash
snakemake -s workflow/snakemake/Snakefile --cores 2 -n
```

Run the workflow:

```bash
snakemake -s workflow/snakemake/Snakefile --cores 2
```

### Nextflow

The Nextflow workflow is located at `workflow/nextflow/main.nf`.

Preview the workflow:

```bash
./nextflow run workflow/nextflow/main.nf -preview
```

Run the workflow with the existing configuration:

```bash
./nextflow run workflow/nextflow/main.nf --reuse_quant true -resume
```

The `-resume` option allows Nextflow to reuse eligible cached tasks. The reuse-quantification option is intended to use the existing quantification output; verify the workflow configuration before applying it to a new dataset.

## Reproducibility and Limitations

- Run commands from the project root, `~/CellScope`.
- Keep the sample sheet, configuration, reference index, and transcript-to-gene mapping consistent.
- Record software versions and reference provenance when preparing a public release.
- Large FASTQ files, reference indexes, virtual environments, temporary work directories, and generated reports may be unsuitable for direct Git commits.
- Cluster identities and pathway enrichments depend on quality filtering, normalisation, clustering parameters, marker selection, and reference annotations.
- A successful workflow run demonstrates computational execution; it does not by itself establish biological validity.

## Future Improvements

- Add automated workflow tests and input validation.
- Improve logging and structured run summaries.
- Document reference genome and annotation versions.
- Add environment lock files or container definitions.
- Add a reproducible comparison of cell-type annotations and pathway results.
- Publish selected figures and a concise interpretation of biological findings.

## Author

Ankur Kumar

Bioinformatics | Single-Cell Genomics | NGS Workflow Automation


---

## Results at a glance

These figures are taken from the analyses in this repository. The matrix-based
analysis and the FASTQ-derived analysis are shown separately because they are
distinct processing branches.

### Cell-type annotations

![Cell-type annotations](docs/images/results/umap-cell-types.png)

*UMAP from the matrix-based analysis, coloured by predicted cell type.*

### Cluster structure

![Cluster structure](docs/images/results/umap-clusters.png)

*Cluster-level UMAP from the matrix-based analysis.*

### Marker-gene analysis

![Marker-gene analysis](docs/images/results/marker-genes.png)

*Marker-gene visualisation generated during the analysis.*

### Cell quality control

![Cell quality control](docs/images/results/qc-distributions.png)

*Quality-control distributions used to inspect cell-level metrics.*

### FASTQ-derived analysis

![FASTQ-derived analysis](docs/images/results/fastq-derived-umap.png)

*UMAP produced by the FASTQ-to-count-matrix analysis branch.*


## Workflow evidence

The screenshots below are terminal captures from the project setup and analysis.
They are included as development evidence; the scripts and workflow files remain
the source of truth for reproducing the work.

<details>
<summary>View terminal screenshots</summary>

### Terminal capture — 08:07:32

<img src="docs/images/terminal/terminal-01-080732.png" alt="Terminal screenshot captured on 16 October 2026 at 08-07-32" width="900" />

### Terminal capture — 08:16:01

<img src="docs/images/terminal/terminal-02-081601.png" alt="Terminal screenshot captured on 16 October 2026 at 08-16-01" width="900" />

### Terminal capture — 08:17:30

<img src="docs/images/terminal/terminal-03-081730.png" alt="Terminal screenshot captured on 16 October 2026 at 08-17-30" width="900" />

### Terminal capture — 08:19:51

<img src="docs/images/terminal/terminal-04-081951.png" alt="Terminal screenshot captured on 16 October 2026 at 08-19-51" width="900" />

### Terminal capture — 08:21:59

<img src="docs/images/terminal/terminal-05-082159.png" alt="Terminal screenshot captured on 16 October 2026 at 08-21-59" width="900" />

### Terminal capture — 08:22:20

<img src="docs/images/terminal/terminal-06-082220.png" alt="Terminal screenshot captured on 16 October 2026 at 08-22-20" width="900" />

### Terminal capture — 09:51:30

<img src="docs/images/terminal/terminal-07-095130.png" alt="Terminal screenshot captured on 16 October 2026 at 09-51-30" width="900" />

### Terminal capture — 10:12:07

<img src="docs/images/terminal/terminal-08-101207.png" alt="Terminal screenshot captured on 16 October 2026 at 10-12-07" width="900" />

### Terminal capture — 12:17:58

<img src="docs/images/terminal/terminal-09-121758.png" alt="Terminal screenshot captured on 16 October 2026 at 12-17-58" width="900" />

### Terminal capture — 12:19:23

<img src="docs/images/terminal/terminal-10-121923.png" alt="Terminal screenshot captured on 16 October 2026 at 12-19-23" width="900" />

### Terminal capture — 12:39:21

<img src="docs/images/terminal/terminal-11-123921.png" alt="Terminal screenshot captured on 16 October 2026 at 12-39-21" width="900" />

### Terminal capture — 13:00:58

<img src="docs/images/terminal/terminal-12-130058.png" alt="Terminal screenshot captured on 16 October 2026 at 13-00-58" width="900" />

</details>

---

## Visual results

These are figures generated by the project. The matrix-based analysis and
FASTQ-derived analysis are separate branches, so their outputs are labelled
separately.

### Cell-type UMAP

![Cell-type UMAP](docs/images/results/umap-cell-types.png)

*Cell-type annotations from the matrix-based analysis.*

### Cluster UMAP

![Cluster UMAP](docs/images/results/umap-clusters.png)

*Cluster structure from the matrix-based analysis.*

### Marker genes

![Marker genes](docs/images/results/marker-genes.png)

*Marker-gene visualisation.*

### Quality control

![Quality control](docs/images/results/qc-distributions.png)

*Cell-level QC distributions.*

### FASTQ-derived UMAP

![FASTQ-derived UMAP](docs/images/results/fastq-derived-umap.png)

*UMAP generated from the FASTQ quantification branch.*


## Terminal proof and workflow evidence

The following screenshots document the project work in the terminal. They are
supporting evidence; the committed scripts and workflow definitions are the
reproducible source of truth.

### Terminal screenshot 1

![Terminal screenshot 1 — Screenshot From 2026-10-16 08-07-32.png](docs/images/terminal/Screenshot-From-2026-10-16-08-07-32.png)

### Terminal screenshot 2

![Terminal screenshot 2 — Screenshot From 2026-10-16 08-16-01.png](docs/images/terminal/Screenshot-From-2026-10-16-08-16-01.png)

### Terminal screenshot 3

![Terminal screenshot 3 — Screenshot From 2026-10-16 08-17-30.png](docs/images/terminal/Screenshot-From-2026-10-16-08-17-30.png)

### Terminal screenshot 4

![Terminal screenshot 4 — Screenshot From 2026-10-16 08-19-51.png](docs/images/terminal/Screenshot-From-2026-10-16-08-19-51.png)

### Terminal screenshot 5

![Terminal screenshot 5 — Screenshot From 2026-10-16 08-21-59.png](docs/images/terminal/Screenshot-From-2026-10-16-08-21-59.png)

### Terminal screenshot 6

![Terminal screenshot 6 — Screenshot From 2026-10-16 08-22-20.png](docs/images/terminal/Screenshot-From-2026-10-16-08-22-20.png)

### Terminal screenshot 7

![Terminal screenshot 7 — Screenshot From 2026-10-16 09-51-30.png](docs/images/terminal/Screenshot-From-2026-10-16-09-51-30.png)

### Terminal screenshot 8

![Terminal screenshot 8 — Screenshot From 2026-10-16 10-12-07.png](docs/images/terminal/Screenshot-From-2026-10-16-10-12-07.png)

### Terminal screenshot 9

![Terminal screenshot 9 — Screenshot From 2026-10-16 12-17-58.png](docs/images/terminal/Screenshot-From-2026-10-16-12-17-58.png)

### Terminal screenshot 10

![Terminal screenshot 10 — Screenshot From 2026-10-16 12-19-23.png](docs/images/terminal/Screenshot-From-2026-10-16-12-19-23.png)

### Terminal screenshot 11

![Terminal screenshot 11 — Screenshot From 2026-10-16 12-39-21.png](docs/images/terminal/Screenshot-From-2026-10-16-12-39-21.png)

### Terminal screenshot 12

![Terminal screenshot 12 — Screenshot From 2026-10-16 13-00-58.png](docs/images/terminal/Screenshot-From-2026-10-16-13-00-58.png)

<!-- CELLSCOPE_VISUAL_GALLERY -->
