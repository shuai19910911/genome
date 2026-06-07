#!/usr/bin/env python3
"""Download, validate, and archive LegumeInfo GFF3 annotation candidates."""

from __future__ import annotations

import argparse
import csv
import gzip
import re
import subprocess
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
LOCAL_REPORTS = ROOT / "local_reports"
DEFAULT_CANDIDATES = LOCAL_REPORTS / "2026-06-07-legumeinfo-candidates.tsv"
DEFAULT_INCOMPLETE = LOCAL_REPORTS / "incomplete-genome-index.tsv"
VALIDATION_DIR = ROOT / "legumeinfo_validation"
REPORT_DIR = ROOT / "validation_reports"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle, delimiter="\t")]


def url_name(url: str) -> str:
    return Path(urlparse(url).path).name


def safe_slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-").lower()


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, cwd=ROOT, check=True)


def download(url: str, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists() and out.stat().st_size > 0:
        return
    run(["curl", "-L", "--fail", "--retry", "5", "--retry-delay", "2", "-C", "-", "-o", str(out), url])


def gzip_ok(path: Path) -> None:
    with gzip.open(path, "rb") as handle:
        while handle.read(1024 * 1024):
            pass


def validation_passed(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    return "验证结论: 通过，可作为同坐标注释候选" in text


def validation_summary(path: Path) -> str:
    metrics: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("- ") and ": " in line:
            key, value = line[2:].split(": ", 1)
            metrics[key] = value
    region_count = metrics.get("GFF3 sequence-region 数", "未知")
    feature_count = metrics.get("GFF3 feature seqid 数", "未知")
    used_feature_bounds = metrics.get("使用 feature 最大 end 坐标兜底验证", "否")
    normalized = metrics.get("归一化 seqid+length 匹配数", "0")
    exact = metrics.get("exact seqid+length 匹配数", "0")
    unique = metrics.get("唯一长度匹配数", "0")
    mismatch = metrics.get("长度不一致数", "未知")
    missing = metrics.get("genome 缺失 region 数", "未知")
    if used_feature_bounds == "是":
        target_note = f"{feature_count} 个 feature seqid 最大 end 坐标不越界"
    else:
        target_note = f"{region_count} 个 sequence-region 长度验证通过"
    return (
        f"通过：{target_note}；exact {exact}，归一化 {normalized}，"
        f"唯一长度 {unique}，长度不一致 {mismatch}，缺失 region {missing}"
    )


def report_prefix(accession: str, annotation_dir: str) -> Path:
    slug = safe_slug(annotation_dir.replace("_", "-"))
    return REPORT_DIR / f"2026-06-07-{accession}-legumeinfo-{slug}"


def source_dir(url: str) -> str:
    return re.sub(r"/[^/]+$", "/", url)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", type=Path, default=DEFAULT_CANDIDATES)
    parser.add_argument("--incomplete", type=Path, default=DEFAULT_INCOMPLETE)
    parser.add_argument("--max-count", type=int, default=8)
    parser.add_argument("--species", action="append", default=[])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    incomplete = {row["assembly_accession"]: row for row in read_tsv(args.incomplete)}
    selected_species = {item.lower() for item in args.species}
    jobs: list[tuple[dict[str, str], dict[str, str]]] = []
    for row in read_tsv(args.candidates):
        if row["has_gff3"] != "yes":
            continue
        if selected_species and row["species"].lower() not in selected_species:
            continue
        local = incomplete.get(row["assembly_accession"])
        if not local:
            continue
        report = Path(str(report_prefix(row["assembly_accession"], row["legumeinfo_annotation_dir"])) + ".validation.md")
        if not report.exists():
            jobs.append((local, row))

    jobs = jobs[: args.max_count]
    for local, candidate in jobs:
        accession = candidate["assembly_accession"]
        print(f"candidate\t{accession}\t{local['species']}\t{candidate['legumeinfo_annotation_dir']}", flush=True)
        if args.dry_run:
            continue

        validation_dir = VALIDATION_DIR / accession
        gff3 = validation_dir / url_name(candidate["gff3_url"])
        download(candidate["gff3_url"], gff3)
        gzip_ok(gff3)

        prefix = report_prefix(accession, candidate["legumeinfo_annotation_dir"])
        prefix.parent.mkdir(parents=True, exist_ok=True)
        run(
            [
                "python3",
                "scripts/validate_annotation_candidate.py",
                "--accession",
                accession,
                "--genome",
                local["genome_path"],
                "--gff3",
                str(gff3.relative_to(ROOT)),
                "--output-prefix",
                str(prefix.relative_to(ROOT)),
            ]
        )
        report = Path(str(prefix) + ".validation.md")
        if not validation_passed(report):
            print(f"skip_failed_validation\t{accession}\t{report.relative_to(ROOT)}", flush=True)
            continue

        run(
            [
                "python3",
                "scripts/finalize_external_annotation.py",
                "--species-dir",
                local["species_dir"],
                "--metadata",
                f"{local['species_dir']}/metadata/source_metadata.json",
                "--genome",
                local["genome_path"],
                "--gff3",
                str(gff3.relative_to(ROOT)),
                "--validation-report",
                str(report.relative_to(ROOT)),
                "--source-name",
                "LegumeInfo FTP",
                "--source-dir",
                source_dir(candidate["gff3_url"]),
                "--gff3-url",
                candidate["gff3_url"],
                "--gtf-url",
                candidate["gtf_url"] or "未提供",
                "--gtf-build-accession",
                "未提供",
                "--gtf-genome-version",
                "未提供",
                "--validation-summary",
                validation_summary(report),
            ]
        )
        print(f"archived\t{accession}\t{local['species_dir']}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
