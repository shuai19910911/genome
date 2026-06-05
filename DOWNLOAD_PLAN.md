# Crop Genome Download Plan

This document defines the pre-download rules for building a local crop genome
and annotation collection. No downloads should be started until the candidate
manifest has been reviewed and approved.

## Goal

Download genome FASTA files and matching GFF/GTF annotation files for crop
species that have both file types available. Each selected species or assembly
will have its own directory and a README describing provenance, file sizes, and
basic assembly metadata.

## Recommended Sources

Use stable public sources in this priority order:

1. Ensembl Plants
2. NCBI Datasets / RefSeq
3. NCBI GenBank, only when RefSeq is unavailable
4. Other crop-specific sources, only if explicitly approved

Phytozome is useful but should not be assumed as a default source because some
downloads require authentication or usage restrictions.

## Scope Decisions To Confirm

Before generating the download manifest, confirm the following:

1. Crop definition:
   - Strict crop list only, such as rice, maize, wheat, soybean, cotton, tomato,
     potato, rapeseed, barley, sorghum, millet, sugarcane, banana, grape, apple,
     and major legumes.
   - Broader cultivated plants, including fruit trees, vegetables, forage crops,
     medicinal plants, and horticultural species.
   - All plant assemblies with usable GFF/GTF annotations, regardless of crop
     status.

2. Assembly granularity:
   - One representative assembly per species.
   - One directory per assembly accession or cultivar.
   - Keep multiple versions only for major crops with important cultivars.

3. Source conflict rule:
   - Prefer Ensembl Plants when a species exists there.
   - Prefer NCBI RefSeq when a curated RefSeq assembly exists.
   - Keep both Ensembl and NCBI versions when they differ materially.

4. Annotation format:
   - Prefer GFF3 and download GTF only when GFF3 is unavailable.
   - Download both GFF3 and GTF when both are available.

5. Compression:
   - Keep original compressed `.gz` files by default.
   - Do not decompress unless downstream tools require it.

## Candidate Manifest

The first executable phase should generate a candidate manifest without
downloading genome data. Suggested file:

`planned_downloads.tsv`

Current helper files:

- `config/crop_scope.tsv`: editable crop scope table.
- `scripts/build_planned_downloads.py`: candidate manifest builder. It inspects
  source directory listings and writes `planned_downloads.tsv`; it does not
  download genome or annotation payloads.
- `scripts/summarize_planned_downloads.py`: read-only review helper. It
  summarizes planned/skipped rows, source distribution, annotation formats, skip
  reasons, and estimated bytes from `planned_downloads.tsv`.
- `scripts/validate_planned_downloads.py`: read-only manifest validator. It
  checks required fields, duplicate output directories, file suffixes,
  annotation formats, and non-positive size fields before dry-run/download.
- `scripts/download_from_manifest.py`: approved-manifest executor. It is dry-run
  by default. It only downloads files and creates species directories when
  `--execute` is passed.

Example review-only command after scope approval:

```bash
python3 scripts/build_planned_downloads.py --crop-scope config/crop_scope.tsv --out planned_downloads.tsv
```

To include rows marked `review` in the scope table:

```bash
python3 scripts/build_planned_downloads.py --include-review --out planned_downloads.tsv
```

Summarize the candidate manifest before approval:

```bash
python3 scripts/summarize_planned_downloads.py --manifest planned_downloads.tsv
```

Validate the candidate manifest before dry-run/download:

```bash
python3 scripts/validate_planned_downloads.py --manifest planned_downloads.tsv
```

Dry-run the approved manifest before downloading:

```bash
python3 scripts/download_from_manifest.py --manifest planned_downloads.tsv
```

Execute downloads only after approval:

```bash
python3 scripts/download_from_manifest.py \
  --manifest planned_downloads.tsv \
  --final-manifest download_manifest.tsv \
  --failed-downloads failed_downloads.tsv \
  --execute
```

Required columns:

- `species`
- `common_name`
- `taxon_id`
- `assembly_accession`
- `assembly_name`
- `assembly_level`
- `source`
- `source_release`
- `genome_url`
- `annotation_url`
- `annotation_format`
- `genome_size_bytes`
- `annotation_size_bytes`
- `md5_url`
- `selection_reason`
- `status`
- `skip_reason`

Rows must be marked as downloadable only when both genome and annotation URLs
are present and reachable.

## Directory Layout

Recommended layout after approval:

```text
genome/
  DOWNLOAD_PLAN.md
  planned_downloads.tsv
  download_manifest.tsv
  download.log
  failed_downloads.tsv
  scripts/
  Species_name_ASSEMBLY_ACCESSION/
    README.md
    README.zh.md
    genome/
      *.fa.gz
    annotation/
      *.gff3.gz or *.gtf.gz
    checksums/
      md5checksums.txt
      sha256sums.txt
    metadata/
      source_metadata.json
```

If only one representative assembly is kept per species, the directory can be
`Species_name/`. If multiple assemblies are allowed, include the accession to
avoid ambiguity.

## Per-Species README Fields

Each species directory should include an English `README.md` and a Chinese
`README.zh.md`. Both files should describe the same provenance and file
metadata.

Each README should include:

- Scientific name
- Common crop name
- Taxonomy ID
- Assembly accession
- Assembly name and version
- Assembly level
- Data source
- Source release or access date
- Original genome URL
- Original annotation URL
- Genome file name and size
- Annotation file name and size
- Annotation format
- Checksum method and values
- Download date
- Selection reason
- Notes about cultivar, subspecies, ploidy, or special handling

## Validation Rules

Before a row enters `download_manifest.tsv`:

1. Genome URL exists and points to a FASTA-like file.
2. Annotation URL exists and points to GFF, GFF3, or GTF.
3. File sizes are non-zero.
4. Checksums are available or local SHA256 checksums will be generated.
5. Species/assembly directory name is unique.

After download:

1. Verify file size against remote metadata when available.
2. Verify MD5 when a source checksum is available.
3. Generate SHA256 for every downloaded file.
4. Confirm compressed files pass `gzip -t`.
5. Confirm genome FASTA has at least one sequence record.
6. Confirm annotation has recognizable feature rows and a valid format marker
   when present.

Local pre-download checks:

```bash
python3 -B -m unittest tests/test_manifest_workflow.py
python3 -B -m unittest tests/test_summarize_planned_downloads.py
python3 -B -m unittest tests/test_validate_planned_downloads.py
python3 -B -m py_compile scripts/build_planned_downloads.py scripts/summarize_planned_downloads.py scripts/validate_planned_downloads.py scripts/download_from_manifest.py tests/test_manifest_workflow.py tests/test_summarize_planned_downloads.py tests/test_validate_planned_downloads.py
```

These checks use temporary files and fake URLs. They do not contact remote
genome sources and do not download genome or annotation payloads.

## Failure Handling

Failures should be recorded in `failed_downloads.tsv` with:

- `species`
- `assembly_accession`
- `source`
- `failed_step`
- `url`
- `error`
- `retry_count`
- `timestamp`

The downloader should be resumable and should avoid re-downloading files that
already pass checksum validation.

## Execution Phases

1. Generate candidate source inventory.
2. Filter to assemblies with both genome FASTA and GFF/GTF annotation.
3. Estimate total download size.
4. Summarize `planned_downloads.tsv`.
5. Validate `planned_downloads.tsv`.
6. Review `planned_downloads.tsv`.
7. Dry-run `scripts/download_from_manifest.py` against approved rows.
8. Download approved rows only with `--execute`.
9. Validate checksums and compressed file integrity.
10. Generate per-species English `README.md` and Chinese `README.zh.md` files.
11. Generate final `download_manifest.tsv` and failure report.

## Current Status

Planning only. No genome or annotation files have been downloaded.
