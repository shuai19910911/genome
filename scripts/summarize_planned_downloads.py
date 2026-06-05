#!/usr/bin/env python3
"""Summarize a planned crop genome download manifest before execution.

This script is read-only: it parses `planned_downloads.tsv` and reports planned
row counts, skipped row counts, estimated bytes, source distribution, annotation
format distribution, and skip reasons.
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter
from pathlib import Path


REQUIRED_COLUMNS = {
    "species",
    "common_name",
    "source",
    "genome_size_bytes",
    "annotation_size_bytes",
    "annotation_format",
    "status",
    "skip_reason",
}


def parse_int(value: str) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def human_bytes(size: int) -> str:
    units = ["B", "KiB", "MiB", "GiB", "TiB"]
    value = float(size)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.2f} {unit}" if unit != "B" else f"{int(value)} B"
        value /= 1024
    return f"{size} B"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        missing = REQUIRED_COLUMNS.difference(reader.fieldnames or [])
        if missing:
            raise ValueError(f"{path} missing required columns: {', '.join(sorted(missing))}")
        return [dict(row) for row in reader]


def summarize(rows: list[dict[str, str]]) -> dict[str, object]:
    planned = [row for row in rows if row.get("status") == "planned"]
    skipped = [row for row in rows if row.get("status") != "planned"]
    genome_bytes = sum(parse_int(row.get("genome_size_bytes", "")) for row in planned)
    annotation_bytes = sum(parse_int(row.get("annotation_size_bytes", "")) for row in planned)
    skip_reasons: Counter[str] = Counter()
    for row in skipped:
        reasons = [item for item in row.get("skip_reason", "").split(";") if item]
        skip_reasons.update(reasons or ["unspecified"])

    return {
        "total_rows": len(rows),
        "planned_rows": len(planned),
        "skipped_rows": len(skipped),
        "genome_bytes": genome_bytes,
        "annotation_bytes": annotation_bytes,
        "total_bytes": genome_bytes + annotation_bytes,
        "sources": Counter(row.get("source", "unspecified") or "unspecified" for row in planned),
        "annotation_formats": Counter(row.get("annotation_format", "unspecified") or "unspecified" for row in planned),
        "skip_reasons": skip_reasons,
        "planned_species": [row.get("species", "") for row in planned],
    }


def print_counter(title: str, counter: Counter[str]) -> None:
    print(title)
    if not counter:
        print("  none")
        return
    for key, count in counter.most_common():
        print(f"  {key}\t{count}")


def print_summary(summary: dict[str, object]) -> None:
    print("Planned Download Summary")
    print(f"  total rows\t{summary['total_rows']}")
    print(f"  planned rows\t{summary['planned_rows']}")
    print(f"  skipped rows\t{summary['skipped_rows']}")
    print(f"  genome bytes\t{summary['genome_bytes']} ({human_bytes(int(summary['genome_bytes']))})")
    print(f"  annotation bytes\t{summary['annotation_bytes']} ({human_bytes(int(summary['annotation_bytes']))})")
    print(f"  total bytes\t{summary['total_bytes']} ({human_bytes(int(summary['total_bytes']))})")
    print_counter("Sources", summary["sources"])  # type: ignore[arg-type]
    print_counter("Annotation formats", summary["annotation_formats"])  # type: ignore[arg-type]
    print_counter("Skip reasons", summary["skip_reasons"])  # type: ignore[arg-type]


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=Path("planned_downloads.tsv"))
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    rows = read_rows(args.manifest)
    print_summary(summarize(rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
