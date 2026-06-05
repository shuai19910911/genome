#!/usr/bin/env python3
"""生成作物基因组候选下载清单，不下载基因组大文件。

脚本读取本地作物范围表，并从 Ensembl Plants 与 NCBI assembly summary
收集候选 assembly。输出 `planned_downloads.tsv` 供人工审阅。
"""

from __future__ import annotations

import argparse
import csv
import html.parser
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path


ENSEMBL_PLANTS_BASE = "https://ftp.ensemblgenomes.ebi.ac.uk/pub/plants/current"
NCBI_REFSEQ_SUMMARY = "https://ftp.ncbi.nlm.nih.gov/genomes/refseq/plant/assembly_summary.txt"
NCBI_GENBANK_SUMMARY = "https://ftp.ncbi.nlm.nih.gov/genomes/genbank/plant/assembly_summary.txt"
DEFAULT_TIMEOUT = 60

MANIFEST_COLUMNS = [
    "species",
    "common_name",
    "taxon_id",
    "assembly_accession",
    "assembly_name",
    "assembly_level",
    "source",
    "source_release",
    "genome_url",
    "annotation_url",
    "annotation_format",
    "gff3_url",
    "gtf_url",
    "genome_size_bytes",
    "annotation_size_bytes",
    "gff3_size_bytes",
    "gtf_size_bytes",
    "md5_url",
    "selection_reason",
    "cultivar",
    "bioproject",
    "phytozome_note",
    "status",
    "skip_reason",
]


class LinkParser(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        for key, value in attrs:
            if key == "href" and value:
                self.links.append(value)


@dataclass(frozen=True)
class Crop:
    species: str
    common_name: str
    scope_group: str
    include: str
    notes: str

    @property
    def ensembl_dir(self) -> str:
        return self.species.lower().replace(" ", "_")


def read_url(url: str, timeout: int = DEFAULT_TIMEOUT) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": "crop-genome-planner/0.1"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="replace")


def read_tsv_url(url: str) -> list[dict[str, str]]:
    body = read_url(url, timeout=180)
    header: list[str] | None = None
    rows: list[dict[str, str]] = []
    for line in body.splitlines():
        if not line:
            continue
        if line.startswith("#assembly_accession") or line.startswith("# assembly_accession"):
            header = line.lstrip("# ").split("\t")
            continue
        if line.startswith("#"):
            continue
        if header is None:
            continue
        fields = line.split("\t")
        if len(fields) < len(header):
            fields.extend([""] * (len(header) - len(fields)))
        rows.append(dict(zip(header, fields)))
    return rows


def list_links(url: str) -> list[str]:
    body = read_url(url)
    parser = LinkParser()
    parser.feed(body)
    links: list[str] = []
    for link in parser.links:
        if link.startswith("?") or link.startswith("/"):
            continue
        if link in {"../", "./"}:
            continue
        links.append(link)
    return links


def url_exists(url: str, timeout: int = DEFAULT_TIMEOUT) -> bool:
    request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "crop-genome-planner/0.1"})
    try:
        with urllib.request.urlopen(request, timeout=timeout):
            return True
    except urllib.error.HTTPError as exc:
        if exc.code == 405:
            try:
                read_url(url, timeout=timeout)
                return True
            except urllib.error.URLError:
                return False
        return False
    except urllib.error.URLError:
        return False


def remote_size(url: str, timeout: int = DEFAULT_TIMEOUT) -> str:
    request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "crop-genome-planner/0.1"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.headers.get("Content-Length", "")
    except urllib.error.URLError:
        return ""


def remote_size_if_exists(url: str) -> tuple[bool, str]:
    if not url:
        return False, ""
    request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "crop-genome-planner/0.1"})
    try:
        with urllib.request.urlopen(request, timeout=DEFAULT_TIMEOUT) as response:
            return True, response.headers.get("Content-Length", "")
    except urllib.error.URLError:
        return False, ""


def read_crops(path: Path, include_review: bool) -> list[Crop]:
    crops: list[Crop] = []
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        required = {"species", "common_name", "scope_group", "include", "notes"}
        missing = required.difference(reader.fieldnames or [])
        if missing:
            raise ValueError(f"{path} missing required columns: {', '.join(sorted(missing))}")
        for row in reader:
            include = row["include"].strip().lower()
            if include == "yes" or (include_review and include == "review"):
                crops.append(
                    Crop(
                        species=row["species"].strip(),
                        common_name=row["common_name"].strip(),
                        scope_group=row["scope_group"].strip(),
                        include=include,
                        notes=row["notes"].strip(),
                    )
                )
    return crops


def choose_first(files: list[str], suffixes: tuple[str, ...]) -> str:
    matches = [item for item in files if item.endswith(suffixes)]
    if not matches:
        return ""
    primary = [item for item in matches if ".dna.toplevel." in item or ".dna.primary_assembly." in item]
    return sorted(primary or matches)[0]


def annotation_format(gff3_url: str, gtf_url: str) -> str:
    formats: list[str] = []
    if gff3_url:
        formats.append("GFF3")
    if gtf_url:
        formats.append("GTF")
    return ";".join(formats)


def inventory_ensembl_species(crop: Crop, base_url: str) -> dict[str, str]:
    species_dir = crop.ensembl_dir
    fasta_dir = f"{base_url}/fasta/{species_dir}/dna/"
    gff3_dir = f"{base_url}/gff3/{species_dir}/"
    gtf_dir = f"{base_url}/gtf/{species_dir}/"

    row = {column: "" for column in MANIFEST_COLUMNS}
    row.update(
        {
            "species": crop.species,
            "common_name": crop.common_name,
            "source": "Ensembl Plants",
            "source_release": base_url.rstrip("/").split("/")[-2] if "/release-" in base_url else "current",
            "selection_reason": f"{crop.scope_group}; {crop.notes}",
        }
    )

    skip_reasons: list[str] = []

    try:
        fasta_files = list_links(fasta_dir)
    except urllib.error.URLError as exc:
        fasta_files = []
        skip_reasons.append(f"missing_genome_dir:{exc.reason}")
    genome_file = choose_first(fasta_files, (".fa.gz", ".fasta.gz", ".fna.gz"))
    if genome_file:
        row["genome_url"] = urllib.parse.urljoin(fasta_dir, genome_file)
        row["genome_size_bytes"] = remote_size(row["genome_url"])
    else:
        skip_reasons.append("missing_genome_fasta")

    annotation_file = ""
    annotation_dir = ""
    gff3_url = ""
    gtf_url = ""
    gff3_size = ""
    gtf_size = ""
    try:
        gff3_files = list_links(gff3_dir)
    except urllib.error.URLError:
        gff3_files = []
    annotation_file = choose_first(gff3_files, (".gff3.gz", ".gff.gz"))
    if annotation_file:
        annotation_dir = gff3_dir
        gff3_url = urllib.parse.urljoin(annotation_dir, annotation_file)
        gff3_size = remote_size(gff3_url)
    try:
        gtf_files = list_links(gtf_dir)
    except urllib.error.URLError:
        gtf_files = []
    gtf_file = choose_first(gtf_files, (".gtf.gz",))
    if gtf_file:
        gtf_url = urllib.parse.urljoin(gtf_dir, gtf_file)
        gtf_size = remote_size(gtf_url)

    if gff3_url or gtf_url:
        row["annotation_url"] = gff3_url or gtf_url
        row["annotation_format"] = annotation_format(gff3_url, gtf_url)
        row["gff3_url"] = gff3_url
        row["gtf_url"] = gtf_url
        row["gff3_size_bytes"] = gff3_size
        row["gtf_size_bytes"] = gtf_size
        row["annotation_size_bytes"] = remote_size(row["annotation_url"])
    else:
        skip_reasons.append("missing_gff_or_gtf")

    md5_url = f"{base_url}/CHECKSUMS"
    if url_exists(md5_url):
        row["md5_url"] = md5_url

    row["status"] = "planned" if row["genome_url"] and row["annotation_url"] else "skipped"
    row["skip_reason"] = ";".join(skip_reasons)
    return row


def species_matches(organism_name: str, species: str) -> bool:
    name = organism_name.lower()
    target = species.lower()
    return name == target or name.startswith(target + " ") or name.startswith(target + " x ")


def cultivar_from_ncbi(row: dict[str, str]) -> str:
    parts = [row.get("infraspecific_name", ""), row.get("isolate", "")]
    text = "; ".join(part for part in parts if part and part != "na")
    return text.replace("cultivar=", "").replace("ecotype=", "")


def ncbi_file_urls(ftp_path: str) -> tuple[str, str, str, str]:
    if not ftp_path or ftp_path == "na":
        return "", "", "", ""
    base = ftp_path.rstrip("/")
    prefix = base.split("/")[-1]
    genome_url = f"{base}/{prefix}_genomic.fna.gz"
    gff3_url = f"{base}/{prefix}_genomic.gff.gz"
    gtf_url = f"{base}/{prefix}_genomic.gtf.gz"
    md5_url = f"{base}/md5checksums.txt"
    return genome_url, gff3_url, gtf_url, md5_url


def inventory_ncbi(crops: list[Crop], summary_url: str, source_name: str, skip_url_check: bool) -> list[dict[str, str]]:
    summary_rows = read_tsv_url(summary_url)
    rows: list[dict[str, str]] = []
    for crop in crops:
        for item in summary_rows:
            if item.get("version_status") not in {"latest", ""}:
                continue
            if not species_matches(item.get("organism_name", ""), crop.species):
                continue
            genome_url, gff3_url, gtf_url, md5_url = ncbi_file_urls(item.get("ftp_path", ""))
            if skip_url_check:
                genome_ok, genome_size = bool(genome_url), ""
                gff3_ok, gff3_size = bool(gff3_url), ""
                gtf_ok, gtf_size = bool(gtf_url), ""
            else:
                genome_ok, genome_size = remote_size_if_exists(genome_url)
                gff3_ok, gff3_size = remote_size_if_exists(gff3_url)
                gtf_ok, gtf_size = remote_size_if_exists(gtf_url)
            row = {column: "" for column in MANIFEST_COLUMNS}
            row.update(
                {
                    "species": crop.species,
                    "common_name": crop.common_name,
                    "taxon_id": item.get("taxid", ""),
                    "assembly_accession": item.get("assembly_accession", ""),
                    "assembly_name": item.get("asm_name", ""),
                    "assembly_level": item.get("assembly_level", ""),
                    "source": source_name,
                    "source_release": "NCBI assembly_summary current",
                    "genome_url": genome_url if genome_ok else "",
                    "annotation_url": gff3_url if gff3_ok else (gtf_url if gtf_ok else ""),
                    "annotation_format": annotation_format(gff3_url if gff3_ok else "", gtf_url if gtf_ok else ""),
                    "gff3_url": gff3_url if gff3_ok else "",
                    "gtf_url": gtf_url if gtf_ok else "",
                    "genome_size_bytes": genome_size,
                    "annotation_size_bytes": gff3_size if gff3_ok else gtf_size,
                    "gff3_size_bytes": gff3_size,
                    "gtf_size_bytes": gtf_size,
                    "md5_url": md5_url,
                    "selection_reason": f"{crop.scope_group}; all available assembly/cultivar candidates; {'URL未逐个预检' if skip_url_check else 'URL已预检'}",
                    "cultivar": cultivar_from_ncbi(item),
                    "bioproject": item.get("bioproject", ""),
                    "phytozome_note": "Phytozome 暂不下载，仅后续记录可用性",
                }
            )
            skip_reasons: list[str] = []
            if not genome_ok:
                skip_reasons.append("missing_genome_fasta")
            if not (gff3_ok or gtf_ok):
                skip_reasons.append("missing_gff_or_gtf")
            row["status"] = "planned" if row["genome_url"] and row["annotation_url"] else "skipped"
            row["skip_reason"] = ";".join(skip_reasons)
            rows.append(row)
    return rows


def deduplicate_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    priority = {"NCBI RefSeq": 0, "Ensembl Plants": 1, "NCBI GenBank": 2}

    def key(row: dict[str, str]) -> tuple[str, str, str]:
        cultivar = row.get("cultivar", "").lower() or row.get("assembly_name", "").lower()
        return (row.get("species", "").lower(), cultivar, row.get("assembly_name", "").lower())

    chosen: dict[tuple[str, str, str], dict[str, str]] = {}
    for row in rows:
        row_key = key(row)
        current = chosen.get(row_key)
        if current is None or priority.get(row.get("source", ""), 9) < priority.get(current.get("source", ""), 9):
            chosen[row_key] = row
    return list(chosen.values())


def write_manifest(rows: list[dict[str, str]], path: Path) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=MANIFEST_COLUMNS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--crop-scope", type=Path, default=Path("config/crop_scope.tsv"))
    parser.add_argument("--out", type=Path, default=Path("planned_downloads.tsv"))
    parser.add_argument("--source", choices=["all", "ensembl-plants", "ncbi"], default="all")
    parser.add_argument("--ensembl-base-url", default=ENSEMBL_PLANTS_BASE)
    parser.add_argument("--ncbi-refseq-summary", default=NCBI_REFSEQ_SUMMARY)
    parser.add_argument("--ncbi-genbank-summary", default=NCBI_GENBANK_SUMMARY)
    parser.add_argument("--include-review", action="store_true", help="include rows marked review in crop_scope.tsv")
    parser.add_argument("--keep-duplicates", action="store_true", help="do not collapse duplicate source rows")
    parser.add_argument("--skip-url-check", action="store_true", help="快速生成候选 URL，不逐个 HEAD 检查文件是否存在和大小")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    crops = read_crops(args.crop_scope, include_review=args.include_review)
    rows: list[dict[str, str]] = []
    if args.source in {"all", "ensembl-plants"}:
        rows.extend(inventory_ensembl_species(crop, args.ensembl_base_url.rstrip("/")) for crop in crops)
    if args.source in {"all", "ncbi"}:
        rows.extend(inventory_ncbi(crops, args.ncbi_refseq_summary, "NCBI RefSeq", args.skip_url_check))
        rows.extend(inventory_ncbi(crops, args.ncbi_genbank_summary, "NCBI GenBank", args.skip_url_check))
    if not args.keep_duplicates:
        rows = deduplicate_rows(rows)
    write_manifest(rows, args.out)
    planned = sum(1 for row in rows if row["status"] == "planned")
    skipped = len(rows) - planned
    print(f"Wrote {args.out}: {planned} planned, {skipped} skipped. No genome files downloaded.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
