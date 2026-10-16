# CellScope — Workflow Review Notes
## Snakemake and Nextflow implementation handoff

**Purpose:** A concise, technically honest summary for a senior review of the workflow automation work in CellScope.

## 1. What the workflow is intended to do

CellScope takes a sample sheet and FASTQ inputs through validation, per-file QC, a combined QC report, transcript quantification and Scanpy downstream analysis. The workflow definitions are intended to encode dependencies so that stages execute in the correct order and completed tasks can be reused when the workflow engine determines their inputs are unchanged.

## 2. Snakemake

**Workflow file:** `workflow/snakemake/Snakefile`  
**Configuration:** `config/config.yaml` and `config/samples.tsv`

The Snakefile is sample-sheet-driven. The sample sheet records `PBMC_1K` and its R1/R2 files across two sequencing lanes. The configuration records the FASTQ directory, `kb-python` index, transcript-to-gene map, `technology: 10XV3`, thread count and memory setting.

**Recorded check:**  
`snakemake -s workflow/snakemake/Snakefile --cores 2 -n`

The dry run reported that the requested outputs were already up to date at the time it was run. The workflow also emitted a provenance-metadata warning for some tools/steps (`fastqc`, `multiqc`, `validate_fastq`). That warning should be addressed or explicitly documented; it is not evidence of a failed analysis by itself.

**What to review with a senior**
- Are all dependencies explicit and all outputs declared correctly?
- Do rules use the sample sheet rather than hard-coded sample names wherever possible?
- Are threads and memory settings used consistently?
- Are conda/software environments or versions captured reproducibly?
- Are the FastQC/MultiQC and quantification outputs unambiguous?
- Does the dry-run DAG match the intended dependency graph?
- Are logs and error messages available per rule?

## 3. Nextflow

**Workflow file:** `workflow/nextflow/main.nf`

Recorded process stages:
1. `VALIDATE_FASTQ`
2. `FASTQC`
3. `MULTIQC`
4. `QUANTIFY`
5. `DOWNSTREAM_SCANPY`

**Successful run recorded on 16 October 2026**
- All five stages reached 100% completion.
- Duration: 14 minutes 18 seconds.
- Summary: three processes succeeded and two were cached.

A previous issue involved the MultiQC process/channel arrangement. The workflow was changed so MultiQC ran against the FastQC report directory rather than relying on the problematic report-channel input. A later end-to-end run completed.

**Important point to verify:** `--reuse_quant true` was passed on a recorded run, but `QUANTIFY` still appeared in the completed process list. Do not describe this as successful quantification reuse until the trace and process inputs confirm that the intended cached result was reused. The safe statement is that the full workflow completed successfully.

**What to review with a senior**
- Does each process declare the correct `input`, `output`, and `publishDir`?
- Are channels shaped as expected, especially where multiple FASTQ files or reports are passed?
- Is the MultiQC input design robust if the number of FASTQ files changes?
- Is the quantification-reuse flag implemented and tested, or is it only a parameter?
- Are the output directories consistent between Snakemake, Nextflow and the README?
- Are `-resume`, trace, report and timeline used to validate caching and execution?
- Are process resources and software versions explicit?

## 4. Data and output evidence

### FASTQ-derived branch
- 7,685,925 read pairs across lane FASTQs.
- `kb-python`: 263 barcodes, 39,546 gene rows, 514,014 non-zero entries.
- Approximate pseudoalignment 58.0%; unique pseudoalignment 14.6%.
- Scanpy output: 262 retained cells, median 1,785 genes/cell, median 5,493 counts/UMIs per cell, median mitochondrial fraction 10.73%, 2,000 HVGs, five clusters.
- Key outputs: MultiQC HTML; `analysis_summary.txt/json`; `cell_qc_metrics.csv`; `pbmc_fastq_clustered.h5ad`; marker tables; `umap_clusters.png`.

### Separate matrix-based branch
- 713 cells before filtering; 567 retained.
- 33,538 genes in filtered AnnData; 2,000 HVGs.
- Seven clusters: 165, 139, 91, 79, 39, 30 and 24 cells.
- Full marker output: 234,766 rows; pathway output: 1,873 rows.

These are separate analysis branches with different input/processing histories. They should not be presented as the same run or as direct replication of each other.

## 5. Known challenge and resolution

**Challenge:** MultiQC did not receive/handle the intended report inputs in an earlier Nextflow iteration.

**Resolution:** The MultiQC process was adjusted to run directly against the FastQC report directory; the later full run completed all stages.

**Lesson:** A process can be syntactically valid but still be connected to the wrong channel shape or input files. Inspect `.command.sh`, task work directories, logs, published outputs and the trace.

**Second documentation issue:** GitHub README images were broken because referenced image paths were not reliably present as committed files. Only embed images after checking that the file exists and is tracked in Git.

## 6. Suggested review agenda

1. Walk through the Snakefile DAG and sample-sheet mapping.
2. Walk through Nextflow channels and process inputs/outputs.
3. Verify that both workflow engines use consistent config and output paths.
4. Inspect the MultiQC fix and discuss a channel-based alternative if appropriate.
5. Test whether quantification reuse truly skips or caches the quantification task.
6. Add a reproducibility manifest: software versions, reference release, parameters and run date.
7. Add a small clean-run test or validation target that checks expected outputs and dimensions.

## 7. How to describe the work accurately

“I implemented a sample-sheet-driven Snakemake workflow and a Nextflow process workflow for FASTQ validation, FastQC, MultiQC, quantification and Scanpy downstream analysis. I debugged a MultiQC input/channel issue and verified a successful end-to-end Nextflow run. I also checked the Snakemake dry-run state. I want to review the caching behaviour, resource declarations and reproducibility metadata with a senior before claiming the workflow is fully production-ready.”
