nextflow.enable.dsl=2

params.samplesheet = "${projectDir}/../../config/samples.tsv"
params.fastq_dir = "${projectDir}/../../data/raw/fastq_small"
params.index = "${projectDir}/../../data/reference/kb/human.idx"
params.t2g = "${projectDir}/../../data/reference/kb/transcripts_to_genes.txt"
params.project = "${projectDir}/../.."
params.outdir = "${projectDir}/../../results"

process VALIDATE_FASTQ {
    tag "$sample"
    input:
    tuple val(sample), path(fastqs)

    output:
    tuple val(sample), path("fastq_integrity.ok"), emit: checked

    script:
    """
    gzip -t ${fastqs}
    touch fastq_integrity.ok
    """
}

process FASTQC {
    tag "$sample"
    publishDir "${params.outdir}/fastqc", mode: 'copy', overwrite: true

    input:
    tuple val(sample), path(fastqs)
    tuple val(checked_sample), path(integrity)

    output:
    tuple val(sample), path("*_fastqc.html"), path("*_fastqc.zip"), emit: reports

    script:
    """
    test "${sample}" = "${checked_sample}"
    /usr/bin/fastqc --threads 2 --outdir . ${fastqs}
    """
}

process MULTIQC {
    output:
    path "multiqc_report.html"

    script:
    """
    ${params.project}/.venv-sc/bin/multiqc ${params.project}/results/fastqc --force --filename multiqc_report.html --outdir .
    """
}

process QUANTIFY {
    tag "$sample"
    publishDir "${params.outdir}/quantification", mode: 'copy', overwrite: true

    input:
    tuple val(sample), path(fastqs)
    path index
    path t2g

    output:
    tuple val(sample), path("quant_out/counts_filtered"), emit: filtered
    path "quant_out"

    script:
    """
    ${params.project}/.venv-sc/bin/kb count -i ${index} -g ${t2g} -x 10XV3 -t 2 -m 2G \
      --filter bustools -o quant_out ${fastqs}
    """
}

process DOWNSTREAM_SCANPY {
    tag "$sample"
    publishDir "${params.outdir}/fastq_analysis", mode: 'copy', overwrite: true

    input:
    tuple val(sample), path(counts)
    path script

    output:
    path "analysis_summary.json"
    path "analysis_summary.txt"
    path "cell_qc_metrics.csv"
    path "gene_annotations.csv"
    path "pbmc_fastq_clustered.h5ad"
    path "cluster_marker_genes.csv"
    path "top_markers_per_cluster.csv"
    path "umap_clusters.png"

    script:
    """
    CELLSCOPE_MATRIX_DIR="${counts}" \
    CELLSCOPE_OUTPUT_DIR="\$PWD" \
    ${params.project}/.venv-sc/bin/python ${script}
    """
}

workflow {
    samples = Channel
        .fromPath(params.samplesheet, checkIfExists: true)
        .splitCsv(header: true, sep: '\t')
        .map { row ->
            def files = [
                "${params.fastq_dir}/${row.r1_l001}",
                "${params.fastq_dir}/${row.r2_l001}",
                "${params.fastq_dir}/${row.r1_l002}",
                "${params.fastq_dir}/${row.r2_l002}"
            ]
            files.each { f ->
                if (!file(f).exists()) error "Missing FASTQ: ${f}"
            }
            tuple(row.sample, files)
        }

    VALIDATE_FASTQ(samples)
    FASTQC(samples, VALIDATE_FASTQ.out.checked)

    MULTIQC()

    index_ch = Channel.value(file(params.index, checkIfExists: true))
    t2g_ch = Channel.value(file(params.t2g, checkIfExists: true))
    script_ch = Channel.value(file("${params.project}/scripts/downstream_fastq.py", checkIfExists: true))

    QUANTIFY(samples, index_ch, t2g_ch)
    DOWNSTREAM_SCANPY(QUANTIFY.out.filtered.map { sample, counts -> tuple(sample, counts) }, script_ch)
}
