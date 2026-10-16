# CellScope Technical Report
## Methods, outputs, interpretation and known limitations

## 1. Project scope

CellScope is an educational and portfolio implementation of an scRNA-seq processing workflow. The data are public human PBMCs from one healthy donor. The project demonstrates workflow engineering and analysis practice; it is not a case-control experiment and does not establish new biological findings.

## 2. Dataset

Source: 10x Genomics, *1k PBMCs from a Healthy Donor (v3 chemistry)*  
https://www.10xgenomics.com/datasets/1-k-pbm-cs-from-a-healthy-donor-v-3-chemistry-3-standard-3-0-0

The source describes human PBMCs generated with 10x Chromium Single Cell 3′ v3 chemistry. Read 1 carries a 16-base cell barcode and 12-base UMI; Read 2 carries transcript sequence. The official reference analysis reports 1,222 detected cells. The source analysis and the project subset/reanalysis are distinct.

The sample sheet lists one sample (`PBMC_1K`) across two sequencing lanes, with R1/R2 pairs for each lane. Recorded FASTQ total: 7,685,925 read pairs. Lanes are technical partitions, not biological replicates.

## 3. Methods and purpose

### 3.1 Input validation
The workflow checks expected sample metadata and FASTQ paths before downstream work. This reduces errors caused by missing or mismatched input files.

### 3.2 Read-level QC
FastQC was run on the four lane pairs (eight FASTQ files). MultiQC consolidated individual reports into `results/fastqc/multiqc/multiqc_report.html`. QC flags should be interpreted in the context of 10x read structure; indiscriminate trimming of barcode/UMI-bearing Read 1 is not appropriate.

### 3.3 Quantification
`kb-python` was run with `technology: 10XV3`, a transcriptome index and a transcript-to-gene mapping. The recorded filtered output had 263 barcodes, 39,546 gene rows and 514,014 non-zero entries. Approximate pseudoalignment was 58.0%; unique pseudoalignment was 14.6%.

Pseudoalignment estimates transcript compatibility rather than conventional base-by-base genomic alignment. Cell barcodes associate reads with cell partitions, while UMIs help distinguish original captured molecules from PCR copies.

### 3.4 FASTQ-derived Scanpy branch
Recorded results: 263 input barcodes, 262 retained cells, median 1,785 detected genes per cell, median 5,493 counts/UMIs per cell, median mitochondrial fraction 10.73%, 2,000 HVGs and five clusters.

The branch outputs include QC tables, an AnnData object, marker tables and a UMAP. Exact QC thresholds, normalization, PCA dimensions, neighbourhood settings, clustering resolution and marker-test details must be read from `scripts/downstream_fastq.py` before being specified in a methods section.

### 3.5 Separate matrix-based branch
The earlier matrix-based branch reported 713 cells before filtering, 567 retained cells, 33,538 genes in filtered AnnData, 2,000 HVGs and seven clusters of 165, 139, 91, 79, 39, 30 and 24 cells. Its full marker table had 234,766 rows and its pathway output had 1,873 rows.

The pathway row count is not necessarily the number of unique pathways. The enrichment test, gene universe, annotation source, multiple-testing correction and significance threshold must be verified in the corresponding scripts.

## 4. Results interpretation

- The 262 retained cells are the FASTQ-derived downstream result, not the official source dataset's total.
- The five-cluster FASTQ result and seven-cluster matrix result belong to different branches. Clustering can change with input, QC, feature selection, graph construction and resolution.
- UMAP is a visualisation of neighbourhood structure; it is not a statistical test.
- Marker genes help characterise clusters but should be validated using multiple canonical markers.
- Pathway enrichment is dependent on the gene list and background universe; row counts alone do not establish biological significance.
- A single donor does not support donor-level population inference.

## 5. Workflow orchestration

Snakemake workflow: `workflow/snakemake/Snakefile`; config: `config/config.yaml` and `config/samples.tsv`. A recorded dry run reported requested targets up to date, with a provenance-metadata warning for some tool steps.

Nextflow workflow: `workflow/nextflow/main.nf`. A recorded run on 16 October 2026 completed `VALIDATE_FASTQ`, `FASTQC`, `MULTIQC`, `QUANTIFY` and `DOWNSTREAM_SCANPY` in 14 minutes 18 seconds, with three processes succeeding and two cached. Since `QUANTIFY` appeared as completed, do not claim that the reuse flag skipped quantification without trace evidence.

## 6. Troubleshooting record

### MultiQC process/channel issue
An earlier Nextflow version had an input/channel arrangement that did not supply the intended report inputs. The process was changed to run MultiQC against the FastQC report directory. The subsequent full workflow completed.

### GitHub image paths
README image references displayed as broken links because the image files were not reliably present at the committed paths. Image links must be added only after confirming the files exist, are tracked and have matching case-sensitive paths.

### Reproducibility metadata
The repository should record the exact reference/index release, package versions, parameters, and run commands. A successful workflow exit alone does not prove scientific correctness; inspect outputs, dimensions, logs and execution traces.

## 7. Further validation before publication

1. Record exact reference/index source and release.
2. Capture package/tool versions.
3. Record QC and normalization settings from the actual scripts.
4. Record the marker-gene statistical test and multiple-testing correction.
5. Record the pathway enrichment method, background and adjusted-p-value cutoff.
6. Verify the `--reuse_quant` behaviour using Nextflow trace/task outputs.
7. Ensure README figures exist in Git and are reproducibly generated.
