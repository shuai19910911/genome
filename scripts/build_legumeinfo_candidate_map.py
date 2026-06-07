#!/usr/bin/env python3
"""Build LegumeInfo genome/annotation candidates by cultivar-like assembly names."""

from __future__ import annotations

import argparse
import csv
import html.parser
import re
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urljoin


ROOT = Path(__file__).resolve().parents[1]
LOCAL_REPORTS = ROOT / "local_reports"
DEFAULT_INPUT = LOCAL_REPORTS / "incomplete-genome-index.tsv"
DEFAULT_CACHE = ROOT / "legumeinfo_cache"
DEFAULT_OUTPUT = LOCAL_REPORTS / "2026-06-07-legumeinfo-candidates.tsv"
DEFAULT_MD = LOCAL_REPORTS / "2026-06-07-legumeinfo-candidate-map.md"
BASE = "https://data.legumeinfo.org/"

SPECIES_PATHS = {
    "Arachis hypogaea": "Arachis/hypogaea/",
    "Glycine max": "Glycine/max/",
    "Phaseolus vulgaris": "Phaseolus/vulgaris/",
    "Vigna radiata": "Vigna/radiata/",
    "Cicer arietinum": "Cicer/arietinum/",
}


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


def fetch_links(url: str, cache_dir: Path, timeout: int) -> list[str]:
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / cache_name(url)
    if cache_path.exists():
        text = cache_path.read_text(errors="replace")
    else:
        request = urllib.request.Request(url, headers={"User-Agent": "legumeinfo-candidate-map/1.0"})
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                text = response.read().decode("utf-8", errors="replace")
        except urllib.error.URLError:
            return []
        cache_path.write_text(text)
    parser = LinkParser()
    parser.feed(text)
    return parser.links


def directory_names(links: list[str], prefix: str) -> list[str]:
    result = []
    for link in links:
        if not link.startswith(prefix) or not link.endswith("/"):
            continue
        result.append(link.rstrip("/").rsplit("/", 1)[-1])
    return sorted(set(result))


def file_names(links: list[str], prefix: str) -> list[str]:
    result = []
    for link in links:
        if not link.startswith(prefix) or link.endswith("/"):
            continue
        result.append(link.rsplit("/", 1)[-1])
    return sorted(set(result))


def normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def base_token(directory: str) -> str:
    return re.sub(r"\.ann\d+\..*$", "", directory)


def first_file(files: list[str], suffixes: tuple[str, ...]) -> str:
    for suffix in suffixes:
        matches = [name for name in files if name.endswith(suffix)]
        if matches:
            return sorted(matches)[0]
    return ""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_MD)
    parser.add_argument("--timeout", type=int, default=45)
    args = parser.parse_args()

    incomplete = read_tsv(args.input)
    by_species: dict[str, list[dict[str, str]]] = {}
    for row in incomplete:
        by_species.setdefault(row["species"], []).append(row)

    rows: list[dict[str, str]] = []
    for species, species_path in SPECIES_PATHS.items():
        local_rows = by_species.get(species, [])
        if not local_rows:
            continue
        genome_root = urljoin(BASE, species_path + "genomes/")
        annotation_root = urljoin(BASE, species_path + "annotations/")
        genome_dirs = directory_names(fetch_links(genome_root, args.cache_dir, args.timeout), f"/{species_path}genomes/")
        annotation_dirs = directory_names(
            fetch_links(annotation_root, args.cache_dir, args.timeout), f"/{species_path}annotations/"
        )
        annotations_by_token = {normalize(base_token(directory)): directory for directory in annotation_dirs}
        for genome_dir in genome_dirs:
            token = normalize(genome_dir.rsplit(".", 1)[0])
            local_matches = [
                row
                for row in local_rows
                if token and token in normalize(row.get("assembly_name", ""))
            ]
            if len(local_matches) != 1:
                continue
            local = local_matches[0]
            annotation_dir = annotations_by_token.get(token)
            if not local or not annotation_dir:
                continue
            ann_url = urljoin(annotation_root, annotation_dir + "/")
            files = file_names(fetch_links(ann_url, args.cache_dir, args.timeout), f"/{species_path}annotations/{annotation_dir}/")
            gff3 = first_file(files, (".gene_models_main.gff3.gz", ".gff3.gz", ".gff.gz"))
            gtf = first_file(files, (".gtf.gz",))
            rows.append(
                {
                    "species": species,
                    "assembly_accession": local["assembly_accession"],
                    "assembly_name": local["assembly_name"],
                    "species_dir": local["species_dir"],
                    "legumeinfo_genome_dir": genome_dir,
                    "legumeinfo_annotation_dir": annotation_dir,
                    "has_gff3": "yes" if gff3 else "no",
                    "has_gtf": "yes" if gtf else "no",
                    "gff3_url": urljoin(ann_url, gff3) if gff3 else "",
                    "gtf_url": urljoin(ann_url, gtf) if gtf else "",
                    "match_evidence": "LegumeInfo genome/annotation token is uniquely contained in local assembly_name",
                }
            )

    fields = [
        "species",
        "assembly_accession",
        "assembly_name",
        "species_dir",
        "legumeinfo_genome_dir",
        "legumeinfo_annotation_dir",
        "has_gff3",
        "has_gtf",
        "gff3_url",
        "gtf_url",
        "match_evidence",
    ]
    write_tsv(args.output, fields, rows)
    lines = [
        "# LegumeInfo 注释候选匹配报告",
        "",
        f"- 本地未完整条目数: {len(incomplete)}",
        f"- 扫描物种数: {len(SPECIES_PATHS)}",
        f"- 找到 assembly 名称匹配候选数: {len(rows)}",
        f"- 候选表: `{args.output.relative_to(ROOT)}`",
        "",
        "## 候选",
        "",
    ]
    if rows:
        for row in rows[:50]:
            lines.append(
                f"- {row['assembly_accession']} / {row['species']} / {row['assembly_name']}: "
                f"GFF3={row['has_gff3']}, GTF={row['has_gtf']}"
            )
    else:
        lines.append("- 暂无。")
    args.output_md.write_text("\n".join(lines))
    print(f"candidates: {len(rows)}")
    print(f"wrote {args.output.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
