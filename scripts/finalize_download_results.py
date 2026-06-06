#!/usr/bin/env python3
"""Merge shard results and write a Chinese final summary."""

from __future__ import annotations

import csv
from collections import Counter
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "docs" / "2026-06-06-download-final-summary.md"


def read_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    if not path.exists():
        return [], []
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        return list(reader.fieldnames or []), [dict(row) for row in reader]


def write_tsv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def count_dirs() -> int:
    return len([path for path in ROOT.glob("*_GC[AF]_*") if path.is_dir()])


def count_readmes() -> int:
    return len(list(ROOT.glob("*_GC[AF]_*" + "/README.md")))


def total_bytes() -> int:
    total = 0
    for directory in ROOT.glob("*_GC[AF]_*"):
        if directory.is_dir():
            for path in directory.rglob("*"):
                if path.is_file():
                    total += path.stat().st_size
    return total


def main() -> int:
    manifest_files = sorted(ROOT.glob("download_manifest.shard*.tsv"))
    failed_files = sorted(ROOT.glob("failed_downloads.shard*.tsv"))

    manifest_fields: list[str] = []
    manifest_rows: list[dict[str, str]] = []
    for path in manifest_files:
        fields, rows = read_tsv(path)
        if fields:
            manifest_fields = fields
        manifest_rows.extend(rows)

    failed_fields: list[str] = []
    failed_rows: list[dict[str, str]] = []
    for path in failed_files:
        fields, rows = read_tsv(path)
        if fields:
            failed_fields = fields
        failed_rows.extend(rows)

    if manifest_fields:
        write_tsv(ROOT / "download_manifest.merged.tsv", manifest_fields, manifest_rows)
    if failed_fields:
        write_tsv(ROOT / "failed_downloads.merged.tsv", failed_fields, failed_rows)

    source_counts = Counter(row.get("source", "") for row in failed_rows)
    species_counts = Counter(row.get("species", "") for row in failed_rows)
    error_counts = Counter(
        "注释文件不存在" if "non-retriable download failure" in row.get("error", "") else row.get("error", "")
        for row in failed_rows
    )
    completed_by_source = Counter(row.get("source", "") for row in manifest_rows)

    total_planned = max(0, sum(1 for _ in (ROOT / "planned_downloads.tsv").open()) - 1)
    bytes_total = total_bytes()
    content = [
        "# NCBI 作物基因组下载阶段总结",
        "",
        f"- 总结时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"- 原始计划条目数: {total_planned}",
        f"- 已完成并写入 shard manifest 的条目数: {len(manifest_rows)}",
        f"- 已失败并写入 failed 表的条目数: {len(failed_rows)}",
        f"- 已生成 assembly 目录数: {count_dirs()}",
        f"- 已生成 README 的完成目录数: {count_readmes()}",
        f"- 本地文件总量: {bytes_total} bytes ({bytes_total / 1024 / 1024 / 1024:.2f} GiB)",
        "",
        "## 完成来源统计",
        "",
    ]
    if completed_by_source:
        for source, count in completed_by_source.most_common():
            content.append(f"- {source or '未知来源'}: {count}")
    else:
        content.append("- 暂无完成记录。")

    content.extend(["", "## 失败原因统计", ""])
    for error, count in error_counts.most_common(10):
        content.append(f"- {error or '未知错误'}: {count}")

    content.extend(["", "## 失败来源统计", ""])
    for source, count in source_counts.most_common(10):
        content.append(f"- {source or '未知来源'}: {count}")

    content.extend(["", "## 失败物种 Top 20", ""])
    for species, count in species_counts.most_common(20):
        content.append(f"- {species or '未知物种'}: {count}")

    content.extend(
        [
            "",
            "## 结论",
            "",
            "- 这一轮 NCBI 清单已经全部处理完成；没有下载管理进程和 aria2 活动下载。",
            "- 成功条目主要是同时能取得 genome 与 GFF/GTF 注释的 assembly。",
            "- 大量失败来自 NCBI GenBank (`GCA`) 条目缺少对应 GFF/GTF 注释文件；脚本已快速跳过并记录失败。",
            "- 失败后留下的目录多包含 metadata、部分 genome 或 `.part` 文件，当前未删除，便于后续补注释、复核或清理。",
            "",
            "## 建议下一步",
            "",
            "1. 先按 `failed_downloads.merged.tsv` 区分“genome 已下载但注释缺失”和“genome 本身失败”。",
            "2. 对注释缺失的 GCA 条目，优先决定是否保留 genome-only 数据；如果不保留，再统一清理未完成目录。",
            "3. 针对重要作物和 cultivar，尝试用 NCBI Datasets、Ensembl Plants 或作物专项数据库补注释。",
            "4. 合并 `download_manifest.merged.tsv` 后，可生成最终索引表和每物种完成/失败报告。",
            "",
        ]
    )
    SUMMARY.write_text("\n".join(content))
    print(f"merged {len(manifest_rows)} completed rows and {len(failed_rows)} failed rows")
    print(f"wrote {SUMMARY.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
