# CellScope: Reproducible Single-Cell RNA-seq Analysis

CellScope is a portfolio and learning project using public 10x Genomics
healthy-donor PBMC single-cell RNA-seq data. It combines raw-read QC,
barcode/UMI-aware quantification, Scanpy analysis and workflow
automation with Snakemake and Nextflow.

**Dataset:** [10x Genomics --- 1k PBMCs from a Healthy Donor (v3
chemistry)](https://www.10xgenomics.com/datasets/1-k-pbm-cs-from-a-healthy-donor-v-3-chemistry-3-standard-3-0-0).
The source reference analysis reports 1,222 detected cells; the smaller
counts below are results of our reanalysis, not the original
dataset-wide result.

## Workflow

1.  Validate sample metadata and expected FASTQs.
2.  Run FastQC and aggregate reports with MultiQC.
3.  Quantify with `kb-python` using the `10XV3` technology setting and
    transcript-to-gene mapping.
4.  Use Scanpy for cell-level QC, HVG selection, dimensionality
    reduction, clustering and marker analysis.
5.  Automate tasks with Snakemake and Nextflow.

## Dataset details

Human PBMCs from one healthy donor, 10x Chromium Single Cell 3′ v3. Read
1 contains a 16-base cell barcode and 12-base UMI; Read 2 contains
transcript sequence. The FASTQ sample sheet represents one sample split
across two sequencing lanes. Lanes are not biological replicates.

## Results

### FASTQ-derived branch

-   7,685,925 read pairs recorded across lane FASTQs.
-   `kb-python` matrix: 263 barcodes, 39,546 gene rows, 514,014 non-zero
    entries.
-   Approximately 58.0% pseudoaligned and 14.6% uniquely pseudoaligned.
-   262 cells retained after downstream QC.
-   Median genes/cell: 1,785; median counts/UMIs per cell: 5,493; median
    mitochondrial fraction: 10.73%.
-   2,000 HVGs and 5 clusters.

Outputs are under `results/fastq_analysis/PBMC_1K/`; FastQC/MultiQC
outputs are under `results/fastqc/`.

### Separate matrix-based branch

An earlier branch used a pre-existing matrix and has a different
processing history: 713 cells before filtering, 567 retained cells,
33,538 genes in filtered AnnData, 2,000 HVGs and 7 clusters (165, 139,
91, 79, 39, 30 and 24 cells). The full marker table contained 234,766
rows and the pathway output contained 1,873 rows.

**Do not merge these branches into one result.** Pathway row count does
not establish the number of unique pathways; verify the enrichment
method, gene background and multiple-testing cutoff before
interpretation.

## Figures

Place generated figures in `docs/images/`, commit them to Git, and
ensure these paths match actual filenames before embedding images.
Example:

``` markdown
![FASTQ-derived clusters](docs/images/fastq_umap_clusters.png)
```

A README image path will be broken on GitHub if the corresponding file
is not committed at that path.

## Workflow automation

The recorded Nextflow run on 16 October 2026 completed `VALIDATE_FASTQ`,
`FASTQC`, `MULTIQC`, `QUANTIFY` and `DOWNSTREAM_SCANPY` in 14 minutes 18
seconds; three processes succeeded and two were cached. Do not claim
quantification was skipped by `--reuse_quant true`, because `QUANTIFY`
appeared as completed in the run.

## Limitations and reproducibility

-   One healthy donor: no biological replication for population-level
    inference.
-   The FASTQ branch is a subset/reanalysis; it retained 262 cells,
    whereas the official reference analysis reports 1,222.
-   Clustering depends on input, filtering, features and
    graph/clustering parameters; UMAP is visualisation, not a
    statistical test.
-   Exact reference/index release, software versions, QC cutoffs, marker
    tests and pathway-enrichment parameters should be documented from
    the actual project files before claiming full reproducibility.
-   Raw data and large generated outputs may be excluded from Git;
    document how to obtain inputs and regenerate outputs.

## Detailed revision guide

See [`docs/INTERVIEW_GUIDE.md`](docs/INTERVIEW_GUIDE.md) for the
step-by-step explanation, statistics, troubleshooting, limitations and
28 likely interview questions with model answers.

## Source and license

10x Genomics, [1k PBMCs from a Healthy Donor (v3
chemistry)](https://www.10xgenomics.com/datasets/1-k-pbm-cs-from-a-healthy-donor-v-3-chemistry-3-standard-3-0-0).
The source page lists CC BY 4.0; retain attribution.
