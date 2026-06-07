#!/usr/bin/env python3
"""Download, validate, and archive Ensembl Plants assembly-name candidates."""

from __future__ import annotations

import argparse
import csv
import gzip
import re
import subprocess
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
DEFAULT_CANDIDATES = DOCS / "2026-06-07-ensembl-plants-species-candidates.tsv"
DEFAULT_INCOMPLETE = DOCS / "incomplete-genome-index.tsv"
VALIDATION_DIR = ROOT / "ensembl_validation"


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


def gtf_metadata(path: Path) -> dict[str, str]:
    meta: dict[str, str] = {}
    with gzip.open(path, "rt", errors="replace") as handle:
        for line in handle:
            if not line.startswith("#!"):
                break
            if " " in line:
                key, value = line[2:].strip().split(" ", 1)
                meta[key] = value
    return meta


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
    normalized = metrics.get("归一化 seqid+length 匹配数", "0")
    exact = metrics.get("exact seqid+length 匹配数", "0")
    unique = metrics.get("唯一长度匹配数", "0")
    mismatch = metrics.get("长度不一致数", "未知")
    missing = metrics.get("genome 缺失 region 数", "未知")
    return (
        f"通过：{region_count} 个 region 坐标验证通过；"
        f"exact {exact}，归一化 {normalized}，唯一长度 {unique}，"
        f"长度不一致 {mismatch}，缺失 region {missing}"
    )


def single_file_annotation(row: dict[str, str]) -> bool:
    gff3 = url_name(row["gff3_url"]).lower()
    gtf = url_name(row["gtf_url"]).lower()
    split_markers = ["chromosome.1.", "chromosome.1a.", ".1.gff3.gz"]
    return gff3.endswith(".gff3.gz") and gtf.endswith(".gtf.gz") and not any(marker in gff3 for marker in split_markers)


def report_prefix(accession: str, ensembl_dir: str) -> Path:
    slug = safe_slug(ensembl_dir.replace("_", "-"))
    return DOCS / f"2026-06-07-{accession}-ensembl-{slug}"


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
    jobs: list[tuple[dict[str, str], dict[str, str], str]] = []
    for row in read_tsv(args.candidates):
        if row["match_type"] != "assembly_name" or row["has_gff3"] != "yes" or row["has_gtf"] != "yes":
            continue
        if selected_species and row["species"].lower() not in selected_species:
            continue
        if not single_file_annotation(row):
            continue
        for accession in filter(None, row["assembly_name_matches"].split(";")):
            local = incomplete.get(accession)
            if local and not Path(str(report_prefix(accession, row["ensembl_dir"])) + ".validation.md").exists():
                jobs.append((local, row, accession))

    jobs = jobs[: args.max_count]
    for local, candidate, accession in jobs:
        print(f"candidate\t{accession}\t{local['species']}\t{candidate['ensembl_dir']}", flush=True)
        if args.dry_run:
            continue

        validation_dir = VALIDATION_DIR / accession
        gff3 = validation_dir / url_name(candidate["gff3_url"])
        gtf = validation_dir / url_name(candidate["gtf_url"])
        download(candidate["gff3_url"], gff3)
        download(candidate["gtf_url"], gtf)
        gzip_ok(gff3)
        gzip_ok(gtf)

        prefix = report_prefix(accession, candidate["ensembl_dir"])
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
                "--gtf",
                str(gtf.relative_to(ROOT)),
                "--output-prefix",
                str(prefix.relative_to(ROOT)),
            ]
        )
        report = Path(str(prefix) + ".validation.md")
        if not validation_passed(report):
            print(f"skip_failed_validation\t{accession}\t{report.relative_to(ROOT)}", flush=True)
            continue

        meta = gtf_metadata(gtf)
        source_dir = re.sub(r"/[^/]+$", "/", candidate["gff3_url"])
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
                "--gtf",
                str(gtf.relative_to(ROOT)),
                "--validation-report",
                str(report.relative_to(ROOT)),
                "--source-name",
                "Ensembl Plants FTP",
                "--source-dir",
                source_dir,
                "--gff3-url",
                candidate["gff3_url"],
                "--gtf-url",
                candidate["gtf_url"],
                "--gtf-build-accession",
                meta.get("genome-build-accession", "未记录"),
                "--gtf-genome-version",
                meta.get("genome-version", "未记录"),
                "--validation-summary",
                validation_summary(report),
            ]
        )
        print(f"archived\t{accession}\t{local['species_dir']}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
