#!/usr/bin/env python3
"""Classify downloaded crop genome directories and write Chinese reports."""

from __future__ import annotations

import csv
import re
from collections import Counter
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
LOCAL_REPORTS = ROOT / "local_reports"
SUMMARY = LOCAL_REPORTS / "2026-06-07-download-state-classification.md"
COMPLETE_INDEX = LOCAL_REPORTS / "completed-genome-index.tsv"
INCOMPLETE_INDEX = LOCAL_REPORTS / "incomplete-genome-index.tsv"
ACCESSION_RE = re.compile(r"(GC[AF]_\d+\.\d+)")


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle, delimiter="\t")]


def write_tsv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row.get(name, "") for name in fieldnames})


def file_size(path: Path) -> int:
    return path.stat().st_size if path.exists() and path.is_file() else 0


def sum_files(directory: Path) -> int:
    return sum(path.stat().st_size for path in directory.rglob("*") if path.is_file())


def first_existing(paths: list[Path]) -> Path | None:
    for path in paths:
        if path.exists() and path.is_file() and path.stat().st_size > 0:
            return path
    return None


def glob_one(directory: Path, patterns: list[str]) -> Path | None:
    matches: list[Path] = []
    for pattern in patterns:
        matches.extend(path for path in directory.rglob(pattern) if path.is_file() and path.stat().st_size > 0)
    return sorted(matches)[0] if matches else None


def classify_dir(directory: Path, planned: dict[str, str], completed_accessions: set[str]) -> dict[str, object]:
    accession = planned.get("assembly_accession", "")
    expected_genome = ROOT / planned.get("genome_path", "") if planned.get("genome_path") else None
    expected_gff3 = ROOT / planned.get("gff3_path", "") if planned.get("gff3_path") else None
    expected_gtf = ROOT / planned.get("gtf_path", "") if planned.get("gtf_path") else None

    genome = first_existing([p for p in [expected_genome] if p]) or glob_one(
        directory, ["*.fna.gz", "*.fa.gz", "*.fasta.gz"]
    )
    gff3 = first_existing([p for p in [expected_gff3] if p]) or glob_one(
        directory, ["*.gff.gz", "*.gff3.gz"]
    )
    gtf = first_existing([p for p in [expected_gtf] if p]) or glob_one(directory, ["*.gtf.gz"])
    part_count = len(list(directory.rglob("*.part"))) + len(list(directory.rglob("*.aria2")))
    readme_zh = directory / "README.zh.md"
    readme_en = directory / "README.md"

    has_genome = genome is not None
    has_gff3 = gff3 is not None
    has_gtf = gtf is not None
    has_annotation = has_gff3 or has_gtf

    if accession in completed_accessions and has_genome and has_annotation and readme_zh.exists():
        status = "完整：清单、文件、中文 README 都存在"
    elif has_genome and has_annotation:
        status = "基本完整：文件存在，但清单或 README 需要复核"
    elif has_genome:
        status = "只有基因组：缺少 GFF3/GTF 注释"
    elif part_count:
        status = "未完成：只有临时下载文件"
    else:
        status = "空目录或仅元数据：没有 genome/annotation 数据文件"

    return {
        "status": status,
        "species": planned.get("species", ""),
        "common_name": planned.get("common_name", ""),
        "assembly_accession": accession,
        "assembly_name": planned.get("assembly_name", ""),
        "assembly_level": planned.get("assembly_level", ""),
        "source": planned.get("source", ""),
        "cultivar": planned.get("cultivar", ""),
        "bioproject": planned.get("bioproject", ""),
        "species_dir": str(directory.relative_to(ROOT)),
        "has_genome": "yes" if has_genome else "no",
        "has_gff3": "yes" if has_gff3 else "no",
        "has_gtf": "yes" if has_gtf else "no",
        "has_readme_zh": "yes" if readme_zh.exists() else "no",
        "has_readme_en": "yes" if readme_en.exists() else "no",
        "part_or_aria2_files": part_count,
        "genome_size_bytes": file_size(genome) if genome else 0,
        "gff3_size_bytes": file_size(gff3) if gff3 else 0,
        "gtf_size_bytes": file_size(gtf) if gtf else 0,
        "directory_size_bytes": sum_files(directory),
        "genome_path": str(genome.relative_to(ROOT)) if genome else "",
        "gff3_path": str(gff3.relative_to(ROOT)) if gff3 else "",
        "gtf_path": str(gtf.relative_to(ROOT)) if gtf else "",
        "genome_url": planned.get("genome_url", ""),
        "gff3_url": planned.get("gff3_url", ""),
        "gtf_url": planned.get("gtf_url", ""),
        "phytozome_note": planned.get("phytozome_note", ""),
    }


def main() -> int:
    planned_rows = read_tsv(ROOT / "planned_downloads.tsv")
    manifest_rows = read_tsv(ROOT / "download_manifest.merged.tsv")
    failed_rows = read_tsv(ROOT / "failed_downloads.merged.tsv")

    planned_by_accession = {row.get("assembly_accession", ""): row for row in planned_rows}
    completed_accessions = {row.get("assembly_accession", "") for row in manifest_rows}
    failed_accessions = {row.get("assembly_accession", "") for row in failed_rows}

    rows: list[dict[str, object]] = []
    for directory in sorted(path for path in ROOT.glob("*_GC[AF]_*") if path.is_dir()):
        match = ACCESSION_RE.search(directory.name)
        accession = match.group(1) if match else directory.name.rsplit("_", 1)[-1]
        planned = planned_by_accession.get(accession, {"assembly_accession": accession, "species_dir": directory.name})
        rows.append(classify_dir(directory, planned, completed_accessions))

    complete_rows = [
        row for row in rows if str(row["status"]).startswith("完整") or str(row["status"]).startswith("基本完整")
    ]
    incomplete_rows = [row for row in rows if row not in complete_rows]

    fieldnames = [
        "status",
        "species",
        "common_name",
        "assembly_accession",
        "assembly_name",
        "assembly_level",
        "source",
        "cultivar",
        "bioproject",
        "species_dir",
        "has_genome",
        "has_gff3",
        "has_gtf",
        "has_readme_zh",
        "has_readme_en",
        "part_or_aria2_files",
        "genome_size_bytes",
        "gff3_size_bytes",
        "gtf_size_bytes",
        "directory_size_bytes",
        "genome_path",
        "gff3_path",
        "gtf_path",
        "genome_url",
        "gff3_url",
        "gtf_url",
        "phytozome_note",
    ]
    write_tsv(COMPLETE_INDEX, fieldnames, complete_rows)
    write_tsv(INCOMPLETE_INDEX, fieldnames, incomplete_rows)

    status_counts = Counter(str(row["status"]) for row in rows)
    failed_species = Counter(row.get("species", "") for row in incomplete_rows)
    complete_species = Counter(row.get("species", "") for row in complete_rows)
    incomplete_with_genome = sum(1 for row in incomplete_rows if row["has_genome"] == "yes")
    incomplete_without_genome = len(incomplete_rows) - incomplete_with_genome
    total_bytes = sum(int(row["directory_size_bytes"]) for row in rows)

    content = [
        "# 作物基因组下载状态分类",
        "",
        f"- 检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"- 计划条目: {len(planned_rows)}",
        f"- 完成清单条目: {len(manifest_rows)}",
        f"- 失败清单条目: {len(failed_rows)}",
        f"- 实际 assembly 目录: {len(rows)}",
        f"- 完整或基本完整目录: {len(complete_rows)}",
        f"- 未完整目录: {len(incomplete_rows)}",
        f"- 未完整但已有 genome 文件的目录: {incomplete_with_genome}",
        f"- 未完整且没有 genome 文件的目录: {incomplete_without_genome}",
        f"- 本地目录总大小: {total_bytes} bytes ({total_bytes / 1024 / 1024 / 1024:.2f} GiB)",
        "",
        "## 分类结果",
        "",
    ]
    for status, count in status_counts.most_common():
        content.append(f"- {status}: {count}")

    content.extend(
        [
            "",
            "## 生成的索引",
            "",
            f"- 完整索引: `{COMPLETE_INDEX.relative_to(ROOT)}`",
            f"- 未完整索引: `{INCOMPLETE_INDEX.relative_to(ROOT)}`",
            "",
            "## 怎么理解这些结果",
            "",
            "- “完整”表示 genome 文件、GFF3/GTF 注释文件、中文 README 都存在，并且该 assembly 在完成清单中。",
            "- “基本完整”表示 genome 和至少一种注释文件存在，但清单或 README 需要再复核。",
            "- “只有基因组”表示已经留下 `.fna.gz` 等 genome 文件，但没有找到 `.gff.gz`、`.gff3.gz` 或 `.gtf.gz`。",
            "- “空目录或仅元数据”表示目前没有可用 genome/annotation 数据文件，通常是因为注释 URL 不存在后快速跳过。",
            "- 本次没有删除任何目录；这些分类表只是帮助后续决定保留、补注释或清理。",
            "",
            "## 完整目录物种 Top 20",
            "",
        ]
    )
    for species, count in complete_species.most_common(20):
        content.append(f"- {species or '未知物种'}: {count}")

    content.extend(["", "## 未完整目录物种 Top 20", ""])
    for species, count in failed_species.most_common(20):
        content.append(f"- {species or '未知物种'}: {count}")

    missing_from_dirs = (completed_accessions | failed_accessions) - {
        str(row["assembly_accession"]) for row in rows
    }
    content.extend(
        [
            "",
            "## 下一步建议",
            "",
            "1. 保留本地 `local_reports/completed-genome-index.tsv` 作为当前可直接使用的数据索引。",
            "2. 对本地 `local_reports/incomplete-genome-index.tsv` 中“只有基因组”的条目，优先从 NCBI Datasets、Ensembl Plants 和作物专项数据库补注释。",
            "3. 对“空目录或仅元数据”的条目，后续如果不再补源，可以统一清理，但清理前应先按索引确认。",
            "4. Phytozome 仍按原决定暂不下载，只在计划清单和报告中保留说明。",
            "",
        ]
    )
    if missing_from_dirs:
        content.extend(
            [
                "## 需要复核",
                "",
                f"- 有 {len(missing_from_dirs)} 个清单 accession 没有对应目录；请后续单独核查。",
                "",
            ]
        )

    SUMMARY.write_text("\n".join(content))
    print(f"classified {len(rows)} directories")
    print(f"complete rows: {len(complete_rows)}")
    print(f"incomplete rows: {len(incomplete_rows)}")
    print(f"wrote {SUMMARY.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
