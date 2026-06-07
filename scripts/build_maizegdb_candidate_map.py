#!/usr/bin/env python3
"""Build MaizeGDB GFF3 candidates for local Zea mays genome-only directories."""

from __future__ import annotations

import argparse
import csv
import html.parser
import re
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
DEFAULT_INPUT = DOCS / "incomplete-genome-index.tsv"
DEFAULT_CACHE = ROOT / "maizegdb_cache"
DEFAULT_OUTPUT = DOCS / "2026-06-07-maizegdb-candidates.tsv"
DEFAULT_MD = DOCS / "2026-06-07-maizegdb-candidate-map.md"
BASE = "https://download.maizegdb.org/"
GFF_DIR = "All_gene_model_GFF/"


class LinkParser(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        for key, value in attrs:
            if key.lower() == "href" and value:
                self.links.append(value)


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
    return re.sub(r"[^A-Za-z0-9._-]+", "_", url.strip("/")) + ".html"


def fetch_links(url: str, cache_dir: Path, timeout: int) -> tuple[list[str], str]:
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / cache_name(url)
    if cache_path.exists():
        text = cache_path.read_text(errors="replace")
        status = "cached"
    else:
        request = urllib.request.Request(url, headers={"User-Agent": "maizegdb-candidate-map/1.0"})
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                text = response.read().decode("utf-8", errors="replace")
        except urllib.error.URLError as exc:
            return [], f"error: {exc}"
        cache_path.write_text(text)
        status = "fetched"
    parser = LinkParser()
    parser.feed(text)
    return parser.links, status


def directory_names(links: list[str]) -> list[str]:
    return sorted(
        link.strip("/")
        for link in links
        if link.endswith("/") and not link.startswith("?") and link not in {"/", "../"}
    )


def file_names(links: list[str]) -> list[str]:
    return sorted(link for link in links if not link.endswith("/") and not link.startswith("?"))


def normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def strip_annotation_suffix(file_name: str) -> str:
    return re.sub(r"_[A-Za-z]{1,3}\d+[A-Za-z]{0,2}\.\d+.*$", "", file_name.removesuffix(".gz").removesuffix(".gff3"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_MD)
    parser.add_argument("--timeout", type=int, default=45)
    args = parser.parse_args()

    incomplete = read_tsv(args.input)
    maize_rows = [row for row in incomplete if row.get("species") == "Zea mays"]
    root_links, root_status = fetch_links(BASE, args.cache_dir, args.timeout)
    gff_links, gff_status = fetch_links(urljoin(BASE, GFF_DIR), args.cache_dir, args.timeout)
    root_dirs = [name for name in directory_names(root_links) if name.startswith(("Zm-", "B73_"))]
    gff_files = [name for name in file_names(gff_links) if name.endswith(".gff3.gz")]

    gff_by_dir: dict[str, list[str]] = {}
    for file_name in gff_files:
        prefix = strip_annotation_suffix(file_name)
        gff_by_dir.setdefault(normalize(prefix), []).append(file_name)

    rows: list[dict[str, str]] = []
    for local in maize_rows:
        local_assembly = local.get("assembly_name", "")
        local_norm = normalize(local_assembly)
        if not local_norm:
            continue
        matches = [directory for directory in root_dirs if normalize(directory) == local_norm]
        if not matches:
            matches = [directory for directory in root_dirs if local_norm in normalize(directory)]
        if len(matches) != 1:
            continue
        maize_dir = matches[0]
        gff_candidates = sorted(gff_by_dir.get(normalize(maize_dir), []))
        if not gff_candidates:
            continue
        gff_file = gff_candidates[-1]
        rows.append(
            {
                "species": "Zea mays",
                "assembly_accession": local["assembly_accession"],
                "assembly_name": local_assembly,
                "cultivar": local.get("cultivar", ""),
                "species_dir": local["species_dir"],
                "maizegdb_dir": maize_dir,
                "has_gff3": "yes",
                "has_gtf": "no",
                "gff3_url": urljoin(urljoin(BASE, GFF_DIR), gff_file),
                "gtf_url": "",
                "root_listing_status": root_status,
                "gff_listing_status": gff_status,
                "match_evidence": "MaizeGDB assembly directory matches local assembly_name after normalization",
            }
        )

    fields = [
        "species",
        "assembly_accession",
        "assembly_name",
        "cultivar",
        "species_dir",
        "maizegdb_dir",
        "has_gff3",
        "has_gtf",
        "gff3_url",
        "gtf_url",
        "root_listing_status",
        "gff_listing_status",
        "match_evidence",
    ]
    write_tsv(args.output, fields, rows)

    lines = [
        "# MaizeGDB 注释候选匹配报告",
        "",
        f"- 检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"- 本地 Zea mays 未完整条目数: {len(maize_rows)}",
        f"- MaizeGDB 根目录 Zm/B73 候选目录数: {len(root_dirs)}",
        f"- MaizeGDB 汇总 GFF3 文件数: {len(gff_files)}",
        f"- 找到 assembly 名称匹配候选数: {len(rows)}",
        f"- 候选表: `{args.output.relative_to(ROOT)}`",
        "",
        "## 候选",
        "",
    ]
    if rows:
        for row in rows[:80]:
            lines.append(
                f"- {row['assembly_accession']} / {row['assembly_name']} / "
                f"{row['maizegdb_dir']}: GFF3=yes, GTF=no"
            )
    else:
        lines.append("- 暂无。")
    args.output_md.write_text("\n".join(lines) + "\n")
    print(f"candidates: {len(rows)}")
    print(f"wrote {args.output.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
