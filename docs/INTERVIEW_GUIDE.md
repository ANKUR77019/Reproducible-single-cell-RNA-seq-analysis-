# CellScope --- Project Revision and Interview Guide

This guide is designed to help you explain **what was done, why it was
done, what the outputs mean, what challenges occurred, and what remains
to verify**. The FASTQ-derived analysis and the earlier matrix-based
analysis are separate branches; do not merge their statistics.

## 1. One-minute project explanation

"CellScope is an end-to-end single-cell RNA-seq learning and portfolio
project using public 10x Genomics healthy-donor PBMC data. I checked raw
FASTQ quality with FastQC and MultiQC, quantified expression with
`kb-python` using the 10x v3 barcode/UMI read structure, and used Scanpy
for cell QC, highly variable gene selection, dimensionality reduction,
clustering and marker analysis. I also built Snakemake and Nextflow
workflows to make the steps easier to rerun and audit. I kept the
FASTQ-derived analysis separate from an earlier matrix-based analysis
because their inputs and processing histories differ."

## 2. Dataset and provenance

**Dataset:** 10x Genomics, [1k PBMCs from a Healthy Donor (v3
chemistry)](https://www.10xgenomics.com/datasets/1-k-pbm-cs-from-a-healthy-donor-v-3-chemistry-3-standard-3-0-0).

-   Human peripheral blood mononuclear cells (PBMCs), one healthy donor.
-   Chromium Single Cell 3′ v3 chemistry.
-   Read 1: 16-base cell barcode + 12-base UMI. Read 2: transcript
    sequence; the official source describes a 91-base Read 2. There is
    also an 8-base sample index.
-   Official 10x reference analysis reports **1,222 detected cells**.
    That is not the number retained in our smaller reanalysis.
-   Dataset source states CC BY 4.0; retain attribution.
-   FASTQ sample sheet lists one sample (`PBMC_1K`) split across two
    lanes, each with R1 and R2 files. The recorded total was **7,685,925
    read pairs**. Lanes are technical partitions, not biological
    replicates.
-   `kb-python` reference inputs included `data/reference/kb/human.idx`
    and `data/reference/kb/transcripts_to_genes.txt`. The exact
    index/reference release still needs to be recorded to make
    provenance fully reproducible.

## 3. What we did and why

### A. Sample sheet and configuration

`config/samples.tsv` lists the sample and four lane FASTQs.
`config/config.yaml` defines the FASTQ directory, reference paths,
`technology: 10XV3`, threads and memory.

**Why:** Central configuration reduces hard-coded paths and makes the
workflow easier to audit. One sample across two lanes is still one
biological sample.

### B. FastQC

FastQC was run on four paired-end lane pairs (eight FASTQ files).

**Why:** It checks per-file read quality, base composition, length
distribution, duplication and adapter-related signals before
quantification. A warning/failure is a diagnostic, not automatically a
reason to trim.

**Chemistry-specific caution:** In 10x 3′ v3, Read 1 contains the cell
barcode and UMI. Indiscriminate trimming of Read 1 could damage this
structure.

### C. MultiQC

MultiQC aggregated the FastQC reports at
`results/fastqc/multiqc/multiqc_report.html`.

**Why:** It lets you compare files and lanes in one report.

### D. `kb-python` quantification

`kb count` used the `10XV3` technology setting, a transcriptome index
and transcript-to-gene mapping.

Recorded output: - 263 barcodes - 39,546 gene rows - 514,014 non-zero
matrix entries - Approximately 58.0% pseudoaligned - Approximately 14.6%
uniquely pseudoaligned

**Pseudoalignment:** Finds transcripts compatible with reads without
conventional base-by-base genome alignment. Counts are then summarised
at gene level using transcript-to-gene mapping.

**Cell barcode:** Associates a read with a cell/droplet partition.
**UMI:** Helps distinguish original captured molecules from PCR copies.
These are essential parts of droplet-based single-cell quantification.

**Interpretation:** The 263 barcodes are the output of this
subset/configuration; they are not expected to match the source's 1,222
reference cells. Quote pseudoalignment percentages with the exact `kb`
report labels if asked.

### E. FASTQ-derived Scanpy analysis

Recorded outputs are under `results/fastq_analysis/PBMC_1K/`.

-   263 barcodes before downstream cell filtering
-   262 cells retained
-   Median genes per cell: 1,785
-   Median counts/UMIs per cell: 5,493
-   Median mitochondrial fraction: 10.73%
-   2,000 highly variable genes (HVGs)
-   5 clusters

Main files include `analysis_summary.json`, `analysis_summary.txt`,
`cell_qc_metrics.csv`, `gene_annotations.csv`,
`pbmc_fastq_clustered.h5ad`, `cluster_marker_genes.csv`,
`top_markers_per_cluster.csv`, and `umap_clusters.png`.

**Metric meanings** - Genes/cell: number of detected genes per cell;
very low values can indicate low-complexity droplets. - Counts/UMIs per
cell: a measure of captured molecules; very low values may indicate poor
capture, while unusually high values can reflect doublets or high-RNA
cells. - Mitochondrial fraction: a QC indicator; high values can be
associated with stressed/damaged cells, but there is no universal
cutoff. - HVGs: genes with substantial cell-to-cell variation under the
feature-selection method; often used for PCA and graph construction. -
PCA: reduces dimensionality to components capturing major expression
variation. - UMAP: a 2D visualisation of neighbourhood structure, not a
statistical test. - Clusters: groups based on expression similarity;
numeric cluster labels are not cell-type names.

**Verify before quoting exact parameters:** inspect
`scripts/downstream_fastq.py` for QC thresholds, normalization, PCA
dimensions, neighbourhood settings, clustering resolution and
marker-gene test. Outcomes alone do not prove which settings were used.

### F. Separate matrix-based analysis

An earlier analysis used a pre-existing matrix, not the small
FASTQ-derived matrix. Its recorded results: - 713 cells before
filtering; 567 retained - 33,538 genes in filtered AnnData - 2,000
HVGs - 7 clusters: cluster 0 = 165; 1 = 139; 2 = 91; 3 = 79; 4 = 39; 5 =
30; 6 = 24 - `cluster_marker_genes_full.csv`: 234,766 rows -
`significant_pathways.csv`: 1,873 rows

Outputs include `results/qc/cell_qc_metrics.csv`,
`filtering_report.csv`, `pbmc_filtered.h5ad`, `qc_distributions.png`,
`qc_summary.txt`, plus analysis outputs such as `cell_clusters.csv`,
`cell_type_annotations.csv`, `canonical_marker_validation.csv`, marker
tables, per-cluster pathway tables, `pathway_summary.txt`,
`significant_pathways.csv`, UMAPs and `pbmc_clustered.h5ad`.

**Never merge these branch results.** The FASTQ branch retained 262
cells/5 clusters; the matrix branch retained 567/7 clusters. Different
inputs and processing histories can produce different cell counts and
clusters.

**Pathway caution:** 1,873 rows is a row count, not proof of 1,873
unique pathways. Verify enrichment method, gene universe/background,
multiple-testing correction, adjusted-p-value threshold and whether
pathways recur across clusters before making a biological claim.

### G. Snakemake and Nextflow

The project includes a sample-sheet-driven Snakemake workflow and a
Nextflow workflow. Workflow managers encode dependencies, run tasks in
order, and can reuse cached outputs when inputs and configuration allow.

Recorded Nextflow run on 16 October 2026: - `VALIDATE_FASTQ` completed -
`FASTQC` completed - `MULTIQC` completed - `QUANTIFY` completed -
`DOWNSTREAM_SCANPY` completed - 14 minutes 18 seconds; three processes
succeeded and two were cached

Do **not** claim `--reuse_quant true` skipped quantification: the
recorded successful run listed `QUANTIFY` as completed. Verify the
execution trace before claiming reuse behaviour.

## 4. Results table

  -----------------------------------------------------------------------
  Metric                   FASTQ-derived branch      Earlier matrix-based
                                                                   branch
  ------------------- ------------------------- -------------------------
  Input                       FASTQ → kb matrix   Pre-existing expression
                                                                   matrix

  Before filtering                 263 barcodes        713 cells reported

  Retained                            262 cells                 567 cells

  Genes                  39,546 gene rows in kb  33,538 genes in filtered
                                         output                   AnnData

  HVGs                                    2,000                     2,000

  Clusters                                    5                         7

  Median genes/cell                       1,785   Verify `qc_summary.txt`

  Median                                  5,493   Verify `qc_summary.txt`
  counts/UMIs/cell                              

  Median                                 10.73%   Verify `qc_summary.txt`
  mitochondrial                                 
  fraction                                      

  Marker output           Marker CSVs available      234,766 rows in full
                                                             marker table

  Pathway output           Not established here     1,873 rows in pathway
                                                                    table
  -----------------------------------------------------------------------

## 5. Troubleshooting and lessons

### Nextflow MultiQC failure

**Issue:** The MultiQC process/channel arrangement did not provide the
intended report inputs and task behaviour was unexpected.

**Resolution recorded:** MultiQC was changed to run directly against the
FastQC report directory, and the later full Nextflow run completed all
five stages.

**Lesson:** A workflow's channel shape and declared process inputs must
match. Inspect task inputs, commands, logs and trace rather than relying
only on a green status.

### Broken README figures on GitHub

**Issue:** Markdown referenced image paths that were absent from the
committed repository or not tracked/pushed.

**Fix/check:** Confirm images exist under `docs/images/`, match
case-sensitive Markdown paths, then stage and commit them. Verify using
`git ls-tree -r --name-only HEAD docs/images/`. A local file is not
automatically tracked on GitHub.

### Different cell/cluster counts

**Issue:** FASTQ analysis produced 262 cells/5 clusters; matrix analysis
produced 567/7.

**Explanation:** Different input matrices and processing histories; cell
filtering, feature selection and graph/clustering parameters also affect
results.

**Lesson:** Record provenance and report each branch separately; do not
combine results or choose a count because it looks more impressive.

### Workflow success versus scientific correctness

A workflow may exit successfully while consuming an unintended file or
running a stage that was intended to be reused. Verify output paths,
matrix dimensions, logs, report readability and execution trace.

## 6. Interview questions and short answers

**1. What is scRNA-seq?**\
It measures gene expression at individual-cell resolution, revealing
heterogeneity that bulk RNA-seq averages together.

**2. Why PBMCs?**\
They contain multiple immune-cell populations and are a common benchmark
for learning single-cell analysis.

**3. Cell barcode versus UMI?**\
The cell barcode identifies a droplet/cell partition; the UMI identifies
an original captured molecule and helps reduce PCR-duplication bias.

**4. Why is Read 1 important in 10x 3′ v3?**\
It contains the 16-base cell barcode and 12-base UMI; Read 2 contains
the transcript sequence. This is chemistry-specific.

**5. Why FastQC?**\
To inspect raw read quality and technical signals before quantification.

**6. Why MultiQC?**\
To aggregate individual QC reports and compare lanes/files in one place.

**7. Did you trim reads?**\
Trimming was not part of the recorded workflow. I would not
indiscriminately trim barcode/UMI-bearing Read 1 because that could
damage the 10x structure. I would add chemistry-aware trimming only if
evidence and tool documentation justified it.

**8. What is pseudoalignment?**\
It identifies transcripts compatible with a read without conventional
base-by-base alignment, then uses transcript-to-gene mapping to produce
gene-level counts.

**9. What does a count matrix represent?**\
Genes by cells (or the transpose, depending on format), with entries
representing observed counts/molecules for a gene in a cell.

**10. Why not compare raw counts directly?**\
Cells have different sequencing depths and RNA capture amounts.
Normalization is useful for exploratory comparisons, while formal tests
should use appropriate statistical models. Quote the actual
normalization used in the script.

**11. Why calculate mitochondrial fraction?**\
It is a cell-quality indicator; elevated values may indicate stress or
damage, but thresholds depend on the sample.

**12. What are HVGs?**\
Genes with substantial variation across cells under a feature-selection
method, often used to focus PCA and graph construction.

**13. What is PCA?**\
A dimensionality-reduction method that captures major patterns of
expression variation in a smaller set of components.

**14. What is UMAP?**\
A 2D embedding for visualising cell neighbourhoods. It is not a formal
test and does not alone prove cell types.

**15. What is clustering?**\
Grouping cells by expression similarity, typically using a
cell-neighbourhood graph and a community-detection algorithm.

**16. Why five versus seven clusters?**\
The branches used different inputs/processing histories; clustering also
depends on features, graph construction and resolution. They are not
identical runs.

**17. How do you annotate cell types?**\
Check several marker genes per cluster, compare with canonical markers
and assess biological consistency; avoid assigning a label from one gene
alone.

**18. What is marker-gene testing?**\
A statistical comparison identifying genes associated with a cluster
under a defined test and comparison. State the exact test and correction
only after checking the script.

**19. Why multiple-testing correction?**\
Thousands of genes/pathways are tested; correction helps control false
discoveries rather than treating every raw p-value as significant.

**20. What is pathway enrichment?**\
It tests whether a gene list overlaps a pathway more than expected
against a defined background. Results depend on the gene list,
background, database and correction.

**21. What does 1,873 pathway rows mean?**\
The output file had 1,873 rows. I would check unique pathway IDs,
cluster repetition, the enrichment method and adjusted-p-value cutoff
before claiming 1,873 unique significant pathways.

**22. Why AnnData?**\
It stores expression data together with cell/gene metadata, embeddings,
cluster labels and analysis results in one structured object.

**23. Why Snakemake and Nextflow?**\
They define task dependencies and improve rerun-ability and
auditability. Snakemake uses rules; Nextflow uses processes and channels
and supports portable execution.

**24. What was a major technical challenge?**\
Fixing the Nextflow MultiQC stage so it processed the intended FastQC
report directory. I inspected the workflow's process/channel setup and
then verified a successful end-to-end run.

**25. How did you validate success?**\
I checked process completion and expected outputs. Strong validation
also checks files are readable, matrix dimensions make sense, sample
identity is correct, and logs/trace match expectations.

**26. Main limitations?**\
One healthy donor, a subset/reanalysis, parameter-dependent clustering,
and separate provenance for the matrix-based branch. This is a workflow
demonstration, not a population-level or disease study.

**27. What would you improve?**\
Document exact reference release and software versions; record
QC/normalization/clustering/marker/enrichment parameters; validate
cell-type labels using multiple markers; report adjusted p-values and
background genes; add automated output checks and ensure all README
images are committed.

**28. What did you learn?**\
How read structure and barcode/UMI processing connect to gene counts,
and how QC, feature selection, embeddings, clustering and marker
interpretation fit together. I also learned that workflow completion
must be checked against scientific outputs.

## 7. Do not overclaim

-   Do not say the source dataset has 262 cells; 262 is the
    FASTQ-derived retained count, while 10x reports 1,222 in its
    reference analysis.
-   Do not say the project has five clusters overall; the separate
    matrix branch has seven.
-   Do not call the 1,873 pathway rows 1,873 unique pathways without
    checking.
-   Do not claim quantification was skipped due to `--reuse_quant true`
    without trace evidence.
-   Do not name a marker-gene statistical test, normalization method or
    filtering cutoff until the actual script confirms it.
-   Do not claim new cell types or population-level biological
    conclusions from one healthy donor.

## 8. Final checklist before interview

-   [ ] Explain the sample sheet, paired reads and two lanes.
-   [ ] Explain `10XV3`, the reference index and transcript-to-gene
    mapping.
-   [ ] Read `scripts/downstream_fastq.py` and note exact thresholds and
    algorithm parameters.
-   [ ] Read matrix-branch QC, marker and pathway scripts; note exact
    tests, background and adjusted-p-value cutoffs.
-   [ ] Open the MultiQC report and describe the main plots/flags.
-   [ ] Open FASTQ `analysis_summary.txt` and `.json`.
-   [ ] Open matrix `qc_summary.txt` and `pathway_summary.txt`.
-   [ ] Ensure every README image exists and is tracked in Git.
-   [ ] Check `git status`,
    `git ls-tree -r --name-only HEAD docs/images/`, and the Nextflow
    trace.
-   [ ] Practise the one-minute project pitch and explain every step
    without reciting commands.

## Source

10x Genomics, [1k PBMCs from a Healthy Donor (v3
chemistry)](https://www.10xgenomics.com/datasets/1-k-pbm-cs-from-a-healthy-donor-v-3-chemistry-3-standard-3-0-0).
The source page provides the dataset description, chemistry, read
structure, reference cell count and license.
