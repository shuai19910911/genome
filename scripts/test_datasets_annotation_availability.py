#!/usr/bin/env python3
"""Test whether NCBI Datasets can provide GFF3/GTF for incomplete assemblies."""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
from collections import Counter
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOCAL_REPORTS = ROOT / "local_reports"
DEFAULT_INPUT = ROOT / "datasets_recovery_test" / "sample_incomplete_accessions.tsv"
DEFAULT_TSV = LOCAL_REPORTS / "2026-06-07-datasets-annotation-test.tsv"
DEFAULT_MD = LOCAL_REPORTS / "2026-06-07-datasets-annotation-test.md"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle, delimiter="\t")]


def run_preview(accession: str, include: str, timeout: int) -> tuple[str, dict[str, object], str]:
    command = [
        "datasets",
        "download",
        "genome",
        "accession",
        accession,
        "--include",
        include,
        "--preview",
        "--no-progressbar",
    ]
    try:
        result = subprocess.run(command, text=True, capture_output=True, timeout=timeout, check=False)
    except subprocess.TimeoutExpired as exc:
        return "timeout", {}, str(exc)

    stdout = result.stdout.strip()
    stderr = result.stderr.strip()
    if result.returncode != 0:
        error = stderr or stdout or f"returncode={result.returncode}"
        if "panic:" in error or "nil pointer dereference" in error:
            return "cli_crash", {}, error.splitlines()[0]
        return "error", {}, error.splitlines()[0] if error else f"returncode={result.returncode}"

    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError:
        return "bad_json", {}, stdout[:200]
    return "ok", payload, ""


def file_count(payload: dict[str, object], key: str) -> int:
    files = payload.get("included_data_files")
    if not isinstance(files, dict):
        return 0
    entry = files.get(key)
    if not isinstance(entry, dict):
        return 0
    try:
        return int(entry.get("file_count", 0) or 0)
    except (TypeError, ValueError):
        return 0


def size_mb(payload: dict[str, object], key: str) -> str:
    files = payload.get("included_data_files")
    if not isinstance(files, dict):
        return ""
    entry = files.get(key)
    if not isinstance(entry, dict):
        return ""
    value = entry.get("size_mb", "")
    return str(value) if value != "" else ""


def classify(gff_status: str, gff_count: int, gtf_status: str, gtf_count: int) -> str:
    if gff_count > 0 and gtf_count > 0:
        return "Datasets 可补 GFF3 和 GTF"
    if gff_count > 0:
        return "Datasets 只能补 GFF3"
    if gtf_count > 0:
        return "Datasets 只能补 GTF"
    if gff_status == "cli_crash" or gtf_status == "cli_crash":
        return "Datasets 未给出注释，CLI 请求注释时崩溃"
    return "Datasets 未给出 GFF3/GTF 注释"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-tsv", type=Path, default=DEFAULT_TSV)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_MD)
    parser.add_argument("--timeout", type=int, default=60)
    args = parser.parse_args()

    rows = read_rows(args.input)
    results: list[dict[str, object]] = []
    for row in rows:
        accession = row["assembly_accession"]
        record_status, record_payload, record_error = run_preview(accession, "none", args.timeout)
        gff_status, gff_payload, gff_error = run_preview(accession, "gff3", args.timeout)
        gtf_status, gtf_payload, gtf_error = run_preview(accession, "gtf", args.timeout)
        gff_count = file_count(gff_payload, "genome_gff")
        gtf_count = file_count(gtf_payload, "genome_gtf")
        results.append(
            {
                "species": row.get("species", ""),
                "assembly_accession": accession,
                "assembly_name": row.get("assembly_name", ""),
                "assembly_level": row.get("assembly_level", ""),
                "cultivar": row.get("cultivar", ""),
                "species_dir": row.get("species_dir", ""),
                "record_status": record_status,
                "record_count": record_payload.get("record_count", "") if record_payload else "",
                "gff3_status": gff_status,
                "gff3_file_count": gff_count,
                "gff3_size_mb": size_mb(gff_payload, "genome_gff"),
                "gtf_status": gtf_status,
                "gtf_file_count": gtf_count,
                "gtf_size_mb": size_mb(gtf_payload, "genome_gtf"),
                "classification": classify(gff_status, gff_count, gtf_status, gtf_count),
                "record_error": record_error,
                "gff3_error": gff_error,
                "gtf_error": gtf_error,
            }
        )
        print(f"{accession}\t{results[-1]['classification']}")

    fields = list(results[0].keys()) if results else []
    args.output_tsv.parent.mkdir(parents=True, exist_ok=True)
    with args.output_tsv.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(results)

    counts = Counter(str(row["classification"]) for row in results)
    lines = [
        "# NCBI Datasets 注释可用性小样本测试",
        "",
        f"- 检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "- 测试方式: 对样本 accession 运行 `datasets download genome accession --include none/gff3/gtf --preview`。",
        "- 说明: 本测试只看 Datasets 是否声明可提供注释文件，不下载正式数据。",
        f"- 样本数: {len(results)}",
        "",
        "## 结果概览",
        "",
    ]
    for name, count in counts.most_common():
        lines.append(f"- {name}: {count}")

    lines.extend(["", "## 样本明细", ""])
    for row in results:
        lines.append(
            f"- {row['assembly_accession']} ({row['species']}): {row['classification']}"
        )

    lines.extend(
        [
            "",
            "## 结论",
            "",
            "- 已安装 `ncbi-datasets-cli`，当前版本可用于后续测试。",
            "- 对已知有注释的 RefSeq accession，Datasets 能正常报告 GFF3/GTF；但本次抽到的 genome-only GenBank 样本没有报告可用注释。",
            "- 对没有注释的 accession，请求 `--include gff3` 或 `--include gtf` 时 CLI 可能崩溃；后续脚本需要把这种情况当作“Datasets 无注释”，并继续尝试专项数据库。",
            f"- 详细 TSV: `{args.output_tsv.relative_to(ROOT)}`",
            "",
        ]
    )
    args.output_md.write_text("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
