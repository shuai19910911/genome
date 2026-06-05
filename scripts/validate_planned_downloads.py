#!/usr/bin/env python3
"""Validate a planned crop genome download manifest before dry-run/download.

The validator is local and read-only. It does not contact remote sources and
does not download genome or annotation files.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
import urllib.parse
from collections import Counter
from pathlib import Path


REQUIRED_COLUMNS = {
    "species",
    "common_name",
    "taxon_id",
    "assembly_accession",
    "assembly_name",
    "assembly_level",
    "source",
    "source_release",
    "genome_url",
    "annotation_url",
    "annotation_format",
    "genome_size_bytes",
    "annotation_size_bytes",
    "md5_url",
    "selection_reason",
    "status",
    "skip_reason",
}

GENOME_SUFFIXES = (".fa", ".fa.gz", ".fasta", ".fasta.gz", ".fna", ".fna.gz")
ANNOTATION_SUFFIXES = (".gff", ".gff.gz", ".gff3", ".gff3.gz", ".gtf", ".gtf.gz")
ANNOTATION_FORMATS = {"GFF", "GFF3", "GTF"}


def read_manifest(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        missing = REQUIRED_COLUMNS.difference(reader.fieldnames or [])
        if missing:
            raise ValueError(f"{path} missing required columns: {', '.join(sorted(missing))}")
        return [dict(row) for row in reader]


def safe_name(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", value.strip())
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    return cleaned or "unknown"


def species_dir_name(row: dict[str, str]) -> str:
    species = safe_name(row.get("species", ""))
    accession = safe_name(row.get("assembly_accession", ""))
    return f"{species}_{accession}" if accession else species


def url_basename(url: str) -> str:
    return Path(urllib.parse.urlparse(url).path).name


def positive_int(value: str) -> bool:
    try:
        return int(value) > 0
    except ValueError:
        return False


def valid_annotation_format(value: str) -> bool:
    formats = [item for item in value.split(";") if item]
    return bool(formats) and all(item in ANNOTATION_FORMATS for item in formats)


def validate_rows(rows: list[dict[str, str]], allow_unknown_size: bool = False) -> list[str]:
    problems: list[str] = []
    planned = [row for row in rows if row.get("status") == "planned"]
    dir_counts = Counter(species_dir_name(row) for row in planned)
    for dirname, count in sorted(dir_counts.items()):
        if count > 1:
            problems.append(f"duplicate_species_dir\t{dirname}\t{count}")

    for index, row in enumerate(rows, start=2):
        status = row.get("status", "")
        species = row.get("species", "")
        if status not in {"planned", "skipped"}:
            problems.append(f"line_{index}\t{species}\tinvalid_status\t{status}")
        if status != "planned":
            continue

        genome_url = row.get("genome_url", "")
        annotation_url = row.get("annotation_url", "")
        annotation_format = row.get("annotation_format", "")
        if not genome_url:
            problems.append(f"line_{index}\t{species}\tmissing_genome_url")
        if not annotation_url:
            problems.append(f"line_{index}\t{species}\tmissing_annotation_url")
        if not valid_annotation_format(annotation_format):
            problems.append(f"line_{index}\t{species}\tinvalid_annotation_format\t{annotation_format}")
        if genome_url and not url_basename(genome_url).endswith(GENOME_SUFFIXES):
            problems.append(f"line_{index}\t{species}\tunexpected_genome_suffix\t{url_basename(genome_url)}")
        if annotation_url and not url_basename(annotation_url).endswith(ANNOTATION_SUFFIXES):
            problems.append(f"line_{index}\t{species}\tunexpected_annotation_suffix\t{url_basename(annotation_url)}")
        if not allow_unknown_size and not positive_int(row.get("genome_size_bytes", "")):
            problems.append(f"line_{index}\t{species}\tmissing_or_nonpositive_genome_size")
        if not allow_unknown_size and not positive_int(row.get("annotation_size_bytes", "")):
            problems.append(f"line_{index}\t{species}\tmissing_or_nonpositive_annotation_size")

    return problems


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=Path("planned_downloads.tsv"))
    parser.add_argument("--allow-unknown-size", action="store_true", help="允许快速候选清单中的大小字段为空")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    rows = read_manifest(args.manifest)
    problems = validate_rows(rows, allow_unknown_size=args.allow_unknown_size)
    if problems:
        print("Manifest validation failed:", file=sys.stderr)
        for problem in problems:
            print(problem, file=sys.stderr)
        return 1
    print(f"Manifest validation passed: {len(rows)} rows checked.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
