# CellScope Interview Revision Notes

## 60-second summary

“CellScope is an end-to-end single-cell RNA-seq workflow using public 10x Genomics healthy-donor PBMC data. I validated the FASTQ inputs, ran FastQC and MultiQC, quantified expression using `kb-python` with the 10x v3 barcode/UMI structure, and used Scanpy for cell QC, HVG selection, dimensionality reduction, clustering and marker analysis. I implemented workflow automation with Snakemake and Nextflow, debugged a MultiQC process/input issue, and verified an end-to-end Nextflow run. I report the FASTQ-derived and earlier matrix-based results separately because they came from different inputs and processing histories.”

## Key numbers to remember

### FASTQ-derived branch
- 7,685,925 read pairs
- 263 barcodes from `kb-python`
- 39,546 gene rows; 514,014 non-zero entries
- ~58.0% pseudoalignment; ~14.6% unique pseudoalignment
- 262 cells retained
- Median genes/cell 1,785
- Median counts/UMIs per cell 5,493
- Median mitochondrial fraction 10.73%
- 2,000 HVGs; 5 clusters

### Separate matrix-based branch
- 713 cells before filtering; 567 retained
- 33,538 genes; 2,000 HVGs
- 7 clusters: 165, 139, 91, 79, 39, 30, 24
- 234,766 rows in full marker table
- 1,873 rows in pathway output (not necessarily unique pathways)

## Questions and model answers

**1. What is single-cell RNA-seq?**  
It measures expression at individual-cell resolution, revealing cell-to-cell heterogeneity that bulk RNA-seq averages together.

**2. Why PBMCs?**  
They contain several immune-cell populations and are commonly used as a single-cell benchmark.

**3. Cell barcode versus UMI?**  
The barcode associates reads with a cell partition; the UMI helps distinguish original captured molecules from PCR copies.

**4. Why is Read 1 important in 10x 3′ v3?**  
It contains the 16-base barcode and 12-base UMI. Read 2 contains transcript sequence. The read structure is chemistry-specific.

**5. Why FastQC and MultiQC?**  
FastQC reports per-file read-quality signals; MultiQC aggregates reports so lanes and files can be compared together.

**6. Did you trim the reads?**  
Trimming was not part of the recorded pipeline. I would not indiscriminately trim barcode/UMI-bearing Read 1 because that could damage the 10x structure.

**7. What is pseudoalignment?**  
It identifies transcripts compatible with a read without conventional base-by-base genome alignment, then summarises counts using transcript-to-gene mapping.

**8. Why do we use UMIs?**  
PCR amplification can create many copies of the same original molecule. UMIs help reduce amplification-related overcounting.

**9. Why filter cells?**  
Low-quality barcodes can have few detected genes/UMIs or unusual mitochondrial fractions. Filtering aims to reduce technical noise, but thresholds must be justified and sample-specific.

**10. Why not use a universal mitochondrial cutoff?**  
Tissue and experiment affect mitochondrial fractions; a fixed threshold can remove valid cells or retain poor-quality cells.

**11. What are HVGs?**  
Genes with substantial cell-to-cell variation under the selected feature-selection method; they help focus downstream dimensionality reduction.

**12. What is PCA?**  
A dimensionality-reduction method that captures major expression variation in fewer components.

**13. What is UMAP?**  
A low-dimensional visualisation of neighbourhood structure. It is not a statistical test and does not prove cell identity.

**14. What is clustering?**  
Grouping cells by expression similarity, usually using a neighbourhood graph and a community-detection algorithm.

**15. Why five clusters in one branch and seven in the other?**  
They are separate branches with different inputs/processing histories. Feature selection, graph construction and clustering parameters can also change the number of clusters.

**16. How do you assign cell types?**  
Use multiple marker genes per cluster, compare with canonical markers, and assess the overall expression pattern rather than relying on one gene.

**17. What is marker-gene testing?**  
It tests whether genes are associated with a cluster relative to a defined comparison. The exact test and multiple-testing correction must be confirmed from the code.

**18. Why correct for multiple testing?**  
Thousands of genes or pathways may be tested; correction reduces false discoveries compared with using raw p-values alone.

**19. What is pathway enrichment?**  
It asks whether a gene list overlaps a pathway more than expected relative to a defined background. It depends on the gene list, background, database and correction method.

**20. Does 1,873 pathway rows mean 1,873 unique pathways?**  
Not necessarily. Rows can repeat pathways across clusters or include multiple records. I would check unique pathway IDs and the enrichment settings before making that claim.

**21. What is AnnData?**  
A structured object for expression data, cell and gene metadata, embeddings, cluster labels and analysis results.

**22. Why Snakemake?**  
It expresses dependencies as rules, supports sample-sheet-driven workflows and avoids rerunning outputs that are already up to date when dependencies are unchanged.

**23. Why Nextflow?**  
It expresses computation as processes connected by channels and supports resumable, portable workflow execution.

**24. What did you debug in Nextflow?**  
A MultiQC process/input-channel arrangement did not deliver the intended report inputs. I adjusted it to run against the FastQC report directory and then verified a complete run.

**25. Did `--reuse_quant true` skip quantification?**  
I would not claim that. In the recorded successful run, `QUANTIFY` appeared as completed. I need to verify the trace and task inputs before claiming the reuse flag skipped that stage.

**26. How did you validate workflow success?**  
I checked the process completion summary and expected output files. A stronger check also inspects file readability, matrix dimensions, logs and the execution trace.

**27. What are the main limitations?**  
One healthy donor, a subset/reanalysis, parameter-dependent clusters, and a separate provenance for the earlier matrix-based branch. It is a workflow demonstration, not a population-level or disease study.

**28. What would you improve?**  
Record the reference release and software versions; document QC, normalization, marker and pathway parameters; verify quantification caching; add automated output checks; and ensure all figures are committed at valid README paths.

## Avoid overclaiming

- Do not call 262 the original dataset cell count; it is the retained count in the FASTQ-derived branch.
- Do not merge the five-cluster FASTQ output with the seven-cluster matrix output.
- Do not claim 1,873 unique pathways without checking the table and enrichment method.
- Do not claim quantification was skipped unless the Nextflow trace confirms it.
- Do not quote exact thresholds or tests until you verify the corresponding scripts.
