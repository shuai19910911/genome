#!/usr/bin/env python3
"""Build Ensembl Plants GFF3/GTF candidate maps for genome-only crop directories."""

from __future__ import annotations

import argparse
import csv
import html.parser
import re
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin


ROOT = Path(__file__).resolve().parents[1]
BASE = "https://ftp.ebi.ac.uk/ensemblgenomes/pub/plants/current/"
DEFAULT_INPUT = ROOT / "docs" / "incomplete-genome-index.tsv"
DEFAULT_CACHE = ROOT / "ensembl_plants_cache"
DEFAULT_EXACT = ROOT / "docs" / "2026-06-07-ensembl-plants-exact-matches.tsv"
DEFAULT_SPECIES = ROOT / "docs" / "2026-06-07-ensembl-plants-species-candidates.tsv"
DEFAULT_MD = ROOT / "docs" / "2026-06-07-ensembl-plants-candidate-map.md"
ACCESSION_RE = re.compile(r"(GC[AF])[_-]?(\d{3})[_-]?(\d{3})[_-]?(\d{3})(?:\.(\d+))?", re.I)


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


def write_tsv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def display_path(path: Path) -> str:
    path = path.resolve()
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def slug_species(species: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", species.lower()).strip("_")


def normalize_text(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def normalize_accession(value: str) -> str:
    match = ACCESSION_RE.search(value)
    if not match:
        return ""
    prefix = match.group(1).upper()
    digits = "".join(match.group(i) for i in range(2, 5))
    version = match.group(5)
    return f"{prefix}_{digits}.{version}" if version else f"{prefix}_{digits}"


def cache_name(url: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", url.strip("/")) + ".html"


def fetch_links(url: str, cache_dir: Path, timeout: int) -> tuple[list[str], str]:
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / cache_name(url)
    if cache_path.exists():
        text = cache_path.read_text(errors="replace")
        status = "cached"
    else:
        request = urllib.request.Request(url, headers={"User-Agent": "genome-annotation-candidate-map/1.0"})
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                text = response.read().decode("utf-8", errors="replace")
            cache_path.write_text(text)
            status = "fetched"
        except urllib.error.URLError as exc:
            return [], f"error: {exc}"
    parser = LinkParser()
    parser.feed(text)
    return parser.links, status


def directory_links(links: list[str]) -> list[str]:
    return sorted(
        link.strip("/")
        for link in links
        if link.endswith("/") and not link.startswith("?") and link not in {"../", "/"}
    )


def file_links(links: list[str]) -> list[str]:
    return sorted(link for link in links if not link.endswith("/") and not link.startswith("?"))


def likely_species_dirs(all_dirs: list[str], species_slugs: set[str]) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for slug in sorted(species_slugs):
        result[slug] = [
            directory
            for directory in all_dirs
            if directory == slug or directory.startswith(slug + "_")
        ]
    return result


def first_annotation_file(files: list[str], suffix: str) -> str:
    preferred = [name for name in files if name.endswith(suffix)]
    if not preferred:
        return ""
    primary = [name for name in preferred if "abinitio" not in name.lower()]
    complete = [name for name in primary if ".chromosome." not in name.lower()]
    return sorted(complete or primary or preferred)[0]


def accession_hits(text: str) -> set[str]:
    hits = set()
    for match in ACCESSION_RE.finditer(text):
        hits.add(normalize_accession(match.group(0)))
    return hits


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE)
    parser.add_argument("--output-exact", type=Path, default=DEFAULT_EXACT)
    parser.add_argument("--output-species", type=Path, default=DEFAULT_SPECIES)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_MD)
    parser.add_argument("--base-url", default=BASE)
    parser.add_argument("--source-name", default="Ensembl Plants")
    parser.add_argument("--timeout", type=int, default=45)
    parser.add_argument("--top-species", type=int, default=12)
    parser.add_argument("--max-dirs-per-species", type=int, default=25)
    args = parser.parse_args()
    base_url = args.base_url.rstrip("/") + "/"
    gff3_base = urljoin(base_url, "gff3/")
    gtf_base = urljoin(base_url, "gtf/")

    incomplete = read_tsv(args.input)
    species_counts = Counter(row["species"] for row in incomplete)
    selected_species = [species for species, _ in species_counts.most_common(args.top_species)]
    species_slugs = {slug_species(species) for species in selected_species}
    rows_by_species = defaultdict(list)
    rows_by_accession: dict[str, dict[str, str]] = {}
    for row in incomplete:
        rows_by_species[slug_species(row["species"])].append(row)
        rows_by_accession[row["assembly_accession"]] = row

    gff_root_links, gff_root_status = fetch_links(gff3_base, args.cache_dir, args.timeout)
    gtf_root_links, gtf_root_status = fetch_links(gtf_base, args.cache_dir, args.timeout)
    gff_dirs = directory_links(gff_root_links)
    gtf_dirs = directory_links(gtf_root_links)
    all_candidate_dirs = sorted(set(gff_dirs) | set(gtf_dirs))
    dirs_by_species = likely_species_dirs(all_candidate_dirs, species_slugs)

    species_rows: list[dict[str, object]] = []
    exact_rows: list[dict[str, object]] = []
    seen_exact: set[tuple[str, str]] = set()

    for slug, directories in sorted(dirs_by_species.items()):
        if not directories:
            continue
        if args.max_dirs_per_species > 0:
            directories = directories[: args.max_dirs_per_species]
        local_rows = rows_by_species.get(slug, [])
        local_accessions = {row["assembly_accession"] for row in local_rows}
        local_accession_roots = {accession.split(".")[0]: accession for accession in local_accessions}
        local_assembly_tokens = {
            normalize_text(row.get("assembly_name", "")): row
            for row in local_rows
            if normalize_text(row.get("assembly_name", ""))
        }
        species = local_rows[0]["species"] if local_rows else slug.replace("_", " ")

        for directory in directories:
            gff_url = urljoin(gff3_base, directory + "/")
            gtf_url = urljoin(gtf_base, directory + "/")
            gff_links, gff_status = fetch_links(gff_url, args.cache_dir, args.timeout) if directory in gff_dirs else ([], "missing_dir")
            gtf_links, gtf_status = fetch_links(gtf_url, args.cache_dir, args.timeout) if directory in gtf_dirs else ([], "missing_dir")
            gff_files = file_links(gff_links)
            gtf_files = file_links(gtf_links)
            gff_file = first_annotation_file(gff_files, ".gff3.gz")
            gtf_file = first_annotation_file(gtf_files, ".gtf.gz")
            combined_text = " ".join([directory, *gff_files, *gtf_files])
            accession_candidates = accession_hits(combined_text)

            exact_accessions = sorted(
                accession
                for accession in local_accessions
                if accession in accession_candidates or accession.split(".")[0] in accession_candidates
            )
            for candidate in accession_candidates:
                if candidate in local_accessions:
                    continue
                if candidate in local_accession_roots:
                    exact_accessions.append(local_accession_roots[candidate])

            assembly_matches = []
            normalized_combined = normalize_text(combined_text)
            for token, row in local_assembly_tokens.items():
                if token and token in normalized_combined:
                    assembly_matches.append(row["assembly_accession"])

            exact_accessions = sorted(set(exact_accessions))
            assembly_matches = sorted(set(assembly_matches) - set(exact_accessions))
            match_type = "exact_accession" if exact_accessions else "assembly_name" if assembly_matches else "species_only"

            species_rows.append(
                {
                    "species": species,
                    "local_incomplete_count": len(local_rows),
                    "ensembl_dir": directory,
                    "match_type": match_type,
                    "exact_accession_count": len(exact_accessions),
                    "assembly_name_match_count": len(assembly_matches),
                    "has_gff3": "yes" if gff_file else "no",
                    "has_gtf": "yes" if gtf_file else "no",
                    "gff3_url": urljoin(gff_url, gff_file) if gff_file else "",
                    "gtf_url": urljoin(gtf_url, gtf_file) if gtf_file else "",
                    "gff3_listing_status": gff_status,
                    "gtf_listing_status": gtf_status,
                    "observed_accessions": ";".join(sorted(accession_candidates)),
                    "exact_accessions": ";".join(exact_accessions),
                    "assembly_name_matches": ";".join(assembly_matches),
                }
            )

            for accession in exact_accessions:
                key = (accession, directory)
                if key in seen_exact:
                    continue
                seen_exact.add(key)
                local = rows_by_accession[accession]
                exact_rows.append(
                    {
                        "species": local["species"],
                        "assembly_accession": accession,
                        "assembly_name": local.get("assembly_name", ""),
                        "cultivar": local.get("cultivar", ""),
                        "species_dir": local.get("species_dir", ""),
                        "ensembl_dir": directory,
                        "has_gff3": "yes" if gff_file else "no",
                        "has_gtf": "yes" if gtf_file else "no",
                        "gff3_url": urljoin(gff_url, gff_file) if gff_file else "",
                        "gtf_url": urljoin(gtf_url, gtf_file) if gtf_file else "",
                        "match_evidence": "accession appears in Ensembl directory or filenames",
                    }
                )

    species_fields = [
        "species",
        "local_incomplete_count",
        "ensembl_dir",
        "match_type",
        "exact_accession_count",
        "assembly_name_match_count",
        "has_gff3",
        "has_gtf",
        "gff3_url",
        "gtf_url",
        "gff3_listing_status",
        "gtf_listing_status",
        "observed_accessions",
        "exact_accessions",
        "assembly_name_matches",
    ]
    exact_fields = [
        "species",
        "assembly_accession",
        "assembly_name",
        "cultivar",
        "species_dir",
        "ensembl_dir",
        "has_gff3",
        "has_gtf",
        "gff3_url",
        "gtf_url",
        "match_evidence",
    ]
    write_tsv(args.output_species, species_fields, species_rows)
    write_tsv(args.output_exact, exact_fields, exact_rows)

    candidate_species = {row["species"] for row in species_rows}
    exact_species = {row["species"] for row in exact_rows}
    species_only_rows = [row for row in species_rows if row["match_type"] == "species_only"]
    assembly_rows = [row for row in species_rows if row["match_type"] == "assembly_name"]
    exact_candidate_rows = [row for row in species_rows if row["match_type"] == "exact_accession"]

    lines = [
        f"# {args.source_name} 注释候选匹配报告",
        "",
        f"- 检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"- {args.source_name} FTP 根目录: `{base_url}`",
        f"- GFF3 根目录状态: {gff_root_status}",
        f"- GTF 根目录状态: {gtf_root_status}",
        f"- 本地 genome-only 条目数: {len(incomplete)}",
        f"- 本地涉及物种数: {len(species_counts)}",
        f"- 本次扫描物种数: {len(selected_species)}",
        f"- 每个物种最多扫描目录数: {args.max_dirs_per_species}",
        f"- {args.source_name} 中找到同物种目录的物种数: {len(candidate_species)}",
        f"- 找到精确 accession 匹配的本地条目数: {len(exact_rows)}",
        f"- 找到精确 accession 匹配的物种数: {len(exact_species)}",
        "",
        "## 分类统计",
        "",
        f"- 精确 accession 候选目录数: {len(exact_candidate_rows)}",
        f"- assembly 名称候选目录数: {len(assembly_rows)}",
        f"- 只有同物种候选目录数: {len(species_only_rows)}",
        "",
        "## 主要结论",
        "",
    ]
    if exact_rows:
        lines.append("- 有 accession 级别匹配，可以优先对这些条目做小样本下载和坐标验证。")
    else:
        lines.append(f"- 这轮没有发现 accession 级别精确匹配；{args.source_name} 主要只能作为同物种参考注释来源。")
    lines.extend(
        [
            "- 同物种候选不能直接标记为完成，必须核对 assembly、cultivar、染色体命名和 FASTA 序列长度。",
            "- 如果只能找到同物种参考注释，应单独建参考目录或在 README 中明确“注释来源与 genome 来源不同”。",
            "",
            "## 输出文件",
            "",
            f"- 精确匹配表: `{display_path(args.output_exact)}`",
            f"- 物种候选表: `{display_path(args.output_species)}`",
            "",
            "## 精确匹配样例",
            "",
        ]
    )
    if exact_rows:
        for row in exact_rows[:20]:
            lines.append(f"- {row['assembly_accession']} ({row['species']}): {row['ensembl_dir']}")
    else:
        lines.append("- 暂无。")

    lines.extend(["", "## 同物种候选 Top 20", ""])
    top_species_dirs = sorted(
        species_rows,
        key=lambda row: (-int(row["local_incomplete_count"]), str(row["species"]), str(row["ensembl_dir"])),
    )
    for row in top_species_dirs[:20]:
        lines.append(
            f"- {row['species']} / {row['ensembl_dir']}: "
            f"GFF3={row['has_gff3']}, GTF={row['has_gtf']}, 本地未完整 {row['local_incomplete_count']}"
        )
    args.output_md.write_text("\n".join(lines))

    print(f"species candidates: {len(species_rows)}")
    print(f"exact matches: {len(exact_rows)}")
    print(f"wrote {display_path(args.output_md)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
