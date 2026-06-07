#!/usr/bin/env python3
"""Build a tabular index of external annotation validation reports."""

from __future__ import annotations

import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
LOCAL_REPORTS = ROOT / "local_reports"
REPORT_DIR = ROOT / "validation_reports"
COMPLETE_INDEX = LOCAL_REPORTS / "completed-genome-index.tsv"
INCOMPLETE_INDEX = LOCAL_REPORTS / "incomplete-genome-index.tsv"
OUT = LOCAL_REPORTS / "2026-06-07-validation-outcome-table.tsv"

ROUTES = ["refseq-paired", "legumeinfo", "maizegdb", "ensembl", "gramene"]
FIELDS = [
    "report_path",
    "source_route",
    "species",
    "common_name",
    "assembly_accession",
    "assembly_name",
    "assembly_level",
    "candidate_label",
    "genome_path",
    "gff3_path",
    "gtf_path",
    "gtf_genome_build_accession",
    "gtf_genome_version",
    "genome_sequence_count",
    "gff3_sequence_region_count",
    "gff3_feature_seqid_count",
    "used_feature_max_end_fallback",
    "sampled_feature_seqid_region_count",
    "exact_seqid_length_matches",
    "normalized_seqid_length_matches",
    "unique_length_matches",
    "length_mismatch_count",
    "missing_region_count",
    "metadata_accession_match",
    "verdict",
    "failure_class",
]


def read_index(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def value(pattern: str, text: str) -> str:
    match = re.search(pattern, text, re.MULTILINE)
    return match.group(1).strip() if match else ""


def clean_path(text: str) -> str:
    return text.strip("`")


def route_from_name(name: str) -> str:
    for route in ROUTES:
        if f"-{route}-" in name:
            return route
    return "unknown"


def failure_class(verdict: str, metadata_match: str, exact: str, missing: str, mismatch: str) -> str:
    if verdict != "fail":
        return ""
    if missing and int(missing) > 0:
        return "missing_seqid_or_region"
    if mismatch and int(mismatch) > 0:
        return "length_mismatch"
    if metadata_match == "no" and (not exact or int(exact) == 0):
        return "metadata_accession_mismatch_no_coordinate_match"
    return "validation_failed_other"


def build_rows() -> list[dict[str, str]]:
    index_rows = read_index(COMPLETE_INDEX) + read_index(INCOMPLETE_INDEX)
    index = {row["assembly_accession"]: row for row in index_rows}
    rows = []
    report_paths = list(REPORT_DIR.glob("2026-06-07-GCA_*.validation.md"))
    # Backward-compatible local fallback while old reports are being migrated.
    report_paths.extend(DOCS.glob("2026-06-07-GCA_*.validation.md"))
    for report in sorted(set(report_paths)):
        text = report.read_text(errors="replace")
        accession = value(r"^- accession:\s*(.+)$", text)
        indexed = index.get(accession, {})
        route = route_from_name(report.name)
        candidate_label = report.name
        if route != "unknown":
            candidate_label = report.name.split(f"-{route}-", 1)[1].removesuffix(".validation.md")
        gtf_accession = value(r"^- GTF genome-build-accession:\s*(.+)$", text)
        conclusion = value(r"^- 验证结论:\s*(.+)$", text)
        if conclusion.startswith("通过"):
            verdict = "pass"
        elif conclusion.startswith("未通过"):
            verdict = "fail"
        else:
            verdict = "unknown"
        exact = value(r"^- exact seqid\+length 匹配数:\s*(\d+)$", text)
        missing = value(r"^- genome 缺失 region 数:\s*(\d+)$", text)
        mismatch = value(r"^- 长度不一致数:\s*(\d+)$", text)
        metadata_match = "unknown"
        if gtf_accession and accession:
            metadata_match = "yes" if gtf_accession == accession else "no"
        rows.append(
            {
                "report_path": str(report.relative_to(ROOT)),
                "source_route": route,
                "species": indexed.get("species", ""),
                "common_name": indexed.get("common_name", ""),
                "assembly_accession": accession,
                "assembly_name": indexed.get("assembly_name", ""),
                "assembly_level": indexed.get("assembly_level", ""),
                "candidate_label": candidate_label,
                "genome_path": clean_path(value(r"^- genome:\s*(.+)$", text)),
                "gff3_path": clean_path(value(r"^- GFF3:\s*(.+)$", text)),
                "gtf_path": clean_path(value(r"^- GTF:\s*(.+)$", text)),
                "gtf_genome_build_accession": gtf_accession,
                "gtf_genome_version": value(r"^- GTF genome-version:\s*(.+)$", text),
                "genome_sequence_count": value(r"^- genome 序列数:\s*(\d+)$", text),
                "gff3_sequence_region_count": value(r"^- GFF3 sequence-region 数:\s*(\d+)$", text),
                "gff3_feature_seqid_count": value(r"^- GFF3 feature seqid 数:\s*(\d+)$", text),
                "used_feature_max_end_fallback": value(r"^- 使用 feature 最大 end 坐标兜底验证:\s*(.+)$", text),
                "sampled_feature_seqid_region_count": value(r"^- GFF3 已抽样 feature seqid 覆盖 region 数:\s*(\d+)$", text),
                "exact_seqid_length_matches": exact,
                "normalized_seqid_length_matches": value(r"^- 归一化 seqid\+length 匹配数:\s*(\d+)$", text),
                "unique_length_matches": value(r"^- 唯一长度匹配数:\s*(\d+)$", text),
                "length_mismatch_count": mismatch,
                "missing_region_count": missing,
                "metadata_accession_match": metadata_match,
                "verdict": verdict,
                "failure_class": failure_class(verdict, metadata_match, exact, missing, mismatch),
            }
        )
    return rows


def main() -> int:
    rows = build_rows()
    with OUT.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {OUT.relative_to(ROOT)} rows={len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
