#!/usr/bin/env python3
"""Find RefSeq GCF annotation candidates paired to local GenBank GCA assemblies."""

from __future__ import annotations

import argparse
import csv
import re
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
DEFAULT_INPUT = DOCS / "incomplete-genome-index.tsv"
DEFAULT_CACHE = ROOT / "ncbi_summary_cache"
DEFAULT_OUTPUT = DOCS / "2026-06-07-refseq-paired-annotation-candidates.tsv"
DEFAULT_MD = DOCS / "2026-06-07-refseq-paired-annotation-candidate-map.md"
GENBANK_SUMMARY = "https://ftp.ncbi.nlm.nih.gov/genomes/genbank/plant/assembly_summary.txt"
REFSEQ_SUMMARY = "https://ftp.ncbi.nlm.nih.gov/genomes/refseq/plant/assembly_summary.txt"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle, delimiter="\t")]


def write_tsv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def cache_name(url: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", url.strip("/")) + ".txt"


def read_url_cached(url: str, cache_dir: Path, timeout: int) -> str:
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / cache_name(url)
    if cache_path.exists():
        return cache_path.read_text(errors="replace")
    request = urllib.request.Request(url, headers={"User-Agent": "refseq-paired-annotation-map/1.0"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        text = response.read().decode("utf-8", errors="replace")
    cache_path.write_text(text)
    return text


def read_ncbi_summary(url: str, cache_dir: Path, timeout: int) -> list[dict[str, str]]:
    body = read_url_cached(url, cache_dir, timeout)
    header: list[str] | None = None
    rows: list[dict[str, str]] = []
    for line in body.splitlines():
        if not line:
            continue
        if line.startswith("#assembly_accession") or line.startswith("# assembly_accession"):
            header = line.lstrip("# ").split("\t")
            continue
        if line.startswith("#") or header is None:
            continue
        fields = line.split("\t")
        if len(fields) < len(header):
            fields.extend([""] * (len(header) - len(fields)))
        rows.append(dict(zip(header, fields)))
    return rows


def ncbi_file_urls(ftp_path: str) -> tuple[str, str, str]:
    if not ftp_path or ftp_path == "na":
        return "", "", ""
    base = ftp_path.rstrip("/")
    prefix = base.rsplit("/", 1)[-1]
    return (
        f"{base}/{prefix}_genomic.fna.gz",
        f"{base}/{prefix}_genomic.gff.gz",
        f"{base}/{prefix}_genomic.gtf.gz",
    )


def remote_size_if_exists(url: str, timeout: int) -> tuple[bool, str]:
    if not url:
        return False, ""
    request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "refseq-paired-annotation-map/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return True, response.headers.get("Content-Length", "")
    except urllib.error.HTTPError as exc:
        if exc.code != 405:
            return False, ""
    except urllib.error.URLError:
        return False, ""
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "refseq-paired-annotation-map/1.0"})
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return True, response.headers.get("Content-Length", "")
    except urllib.error.URLError:
        return False, ""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_MD)
    parser.add_argument("--timeout", type=int, default=60)
    args = parser.parse_args()

    incomplete = read_tsv(args.input)
    incomplete_by_accession = {row["assembly_accession"]: row for row in incomplete}
    genbank_rows = read_ncbi_summary(GENBANK_SUMMARY, args.cache_dir, 180)
    refseq_rows = read_ncbi_summary(REFSEQ_SUMMARY, args.cache_dir, 180)
    genbank_by_accession = {row["assembly_accession"]: row for row in genbank_rows}
    refseq_by_accession = {row["assembly_accession"]: row for row in refseq_rows}

    rows: list[dict[str, str]] = []
    paired_count = 0
    for accession, local in incomplete_by_accession.items():
        gb = genbank_by_accession.get(accession)
        if not gb:
            continue
        paired = gb.get("gbrs_paired_asm", "")
        if not paired or paired == "na":
            continue
        paired_count += 1
        refseq = refseq_by_accession.get(paired)
        if not refseq or refseq.get("version_status") not in {"latest", ""}:
            continue
        genome_url, gff3_url, gtf_url = ncbi_file_urls(refseq.get("ftp_path", ""))
        genome_ok, genome_size = remote_size_if_exists(genome_url, args.timeout)
        gff3_ok, gff3_size = remote_size_if_exists(gff3_url, args.timeout)
        gtf_ok, gtf_size = remote_size_if_exists(gtf_url, args.timeout)
        if not genome_ok or not (gff3_ok or gtf_ok):
            continue
        rows.append(
            {
                "species": local["species"],
                "assembly_accession": accession,
                "assembly_name": local.get("assembly_name", ""),
                "species_dir": local["species_dir"],
                "paired_refseq_accession": paired,
                "paired_refseq_assembly_name": refseq.get("asm_name", ""),
                "paired_asm_comp": gb.get("paired_asm_comp", ""),
                "has_gff3": "yes" if gff3_ok else "no",
                "has_gtf": "yes" if gtf_ok else "no",
                "refseq_genome_url": genome_url,
                "refseq_gff3_url": gff3_url if gff3_ok else "",
                "refseq_gtf_url": gtf_url if gtf_ok else "",
                "refseq_genome_size_bytes": genome_size,
                "refseq_gff3_size_bytes": gff3_size,
                "refseq_gtf_size_bytes": gtf_size,
                "match_evidence": "NCBI GenBank assembly_summary gbrs_paired_asm maps local GCA to RefSeq GCF",
            }
        )

    fields = [
        "species",
        "assembly_accession",
        "assembly_name",
        "species_dir",
        "paired_refseq_accession",
        "paired_refseq_assembly_name",
        "paired_asm_comp",
        "has_gff3",
        "has_gtf",
        "refseq_genome_url",
        "refseq_gff3_url",
        "refseq_gtf_url",
        "refseq_genome_size_bytes",
        "refseq_gff3_size_bytes",
        "refseq_gtf_size_bytes",
        "match_evidence",
    ]
    write_tsv(args.output, fields, rows)

    lines = [
        "# RefSeq paired annotation 候选匹配报告",
        "",
        f"- 检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"- 本地未完整条目数: {len(incomplete)}",
        f"- 在 GenBank summary 中有 paired RefSeq 的条目数: {paired_count}",
        f"- paired RefSeq 端有 genome 且有 GFF3/GTF 的候选数: {len(rows)}",
        f"- 候选表: `{args.output.relative_to(ROOT)}`",
        "",
        "## 候选",
        "",
    ]
    if rows:
        for row in rows[:120]:
            lines.append(
                f"- {row['assembly_accession']} -> {row['paired_refseq_accession']} / "
                f"{row['species']} / {row['paired_refseq_assembly_name']}: "
                f"GFF3={row['has_gff3']}, GTF={row['has_gtf']}"
            )
    else:
        lines.append("- 暂无。")
    args.output_md.write_text("\n".join(lines) + "\n")
    print(f"paired: {paired_count}")
    print(f"candidates: {len(rows)}")
    print(f"wrote {args.output.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
