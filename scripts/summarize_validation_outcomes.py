#!/usr/bin/env python3
"""Summarize external annotation validation outcomes."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "docs" / "2026-06-07-validation-outcome-table.tsv"
OUT_DIR = ROOT / "docs"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_rows(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def summarize_by(rows: list[dict[str, str]], key: str) -> list[dict[str, object]]:
    grouped: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        grouped[row.get(key, "") or "unknown"][row.get("verdict", "") or "unknown"] += 1

    summary = []
    for value, counts in sorted(grouped.items(), key=lambda item: (-sum(item[1].values()), item[0])):
        total = sum(counts.values())
        passed = counts.get("pass", 0)
        failed = counts.get("fail", 0)
        summary.append(
            {
                key: value,
                "total": total,
                "pass": passed,
                "fail": failed,
                "unknown": counts.get("unknown", 0),
                "pass_rate": f"{passed / total:.6f}" if total else "0.000000",
            }
        )
    return summary


def summarize_failure_class(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    counts = Counter(row.get("failure_class", "") or "none" for row in rows)
    return [
        {"failure_class": key, "count": value}
        for key, value in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    ]


def main() -> int:
    rows = read_rows(INPUT)
    write_rows(
        OUT_DIR / "2026-06-07-validation-summary-by-route.tsv",
        ["source_route", "total", "pass", "fail", "unknown", "pass_rate"],
        summarize_by(rows, "source_route"),
    )
    write_rows(
        OUT_DIR / "2026-06-07-validation-summary-by-species.tsv",
        ["species", "total", "pass", "fail", "unknown", "pass_rate"],
        summarize_by(rows, "species"),
    )
    write_rows(
        OUT_DIR / "2026-06-07-validation-summary-by-assembly-level.tsv",
        ["assembly_level", "total", "pass", "fail", "unknown", "pass_rate"],
        summarize_by(rows, "assembly_level"),
    )
    write_rows(
        OUT_DIR / "2026-06-07-validation-summary-by-failure-class.tsv",
        ["failure_class", "count"],
        summarize_failure_class(rows),
    )
    print(f"summarized {len(rows)} validation rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
