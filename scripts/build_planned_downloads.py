#!/usr/bin/env python3
"""Build a planned crop genome download manifest without downloading genomes.

The script inventories Ensembl Plants FTP directory listings and matches species
from a local scope table to genome FASTA and GFF/GTF annotation URLs. It writes a
TSV candidate manifest for review. It intentionally does not download genome or
annotation payloads.
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
    "genome_size_bytes",
    "annotation_size_bytes",
    "md5_url",
    "selection_reason",
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
    annotation_format = ""
    try:
        gff3_files = list_links(gff3_dir)
    except urllib.error.URLError:
        gff3_files = []
    annotation_file = choose_first(gff3_files, (".gff3.gz", ".gff.gz"))
    if annotation_file:
        annotation_dir = gff3_dir
        annotation_format = "GFF3"
    else:
        try:
            gtf_files = list_links(gtf_dir)
        except urllib.error.URLError:
            gtf_files = []
        annotation_file = choose_first(gtf_files, (".gtf.gz",))
        if annotation_file:
            annotation_dir = gtf_dir
            annotation_format = "GTF"

    if annotation_file:
        row["annotation_url"] = urllib.parse.urljoin(annotation_dir, annotation_file)
        row["annotation_format"] = annotation_format
        row["annotation_size_bytes"] = remote_size(row["annotation_url"])
    else:
        skip_reasons.append("missing_gff_or_gtf")

    md5_url = f"{base_url}/CHECKSUMS"
    if url_exists(md5_url):
        row["md5_url"] = md5_url

    row["status"] = "planned" if row["genome_url"] and row["annotation_url"] else "skipped"
    row["skip_reason"] = ";".join(skip_reasons)
    return row


def write_manifest(rows: list[dict[str, str]], path: Path) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=MANIFEST_COLUMNS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--crop-scope", type=Path, default=Path("config/crop_scope.tsv"))
    parser.add_argument("--out", type=Path, default=Path("planned_downloads.tsv"))
    parser.add_argument("--source", choices=["ensembl-plants"], default="ensembl-plants")
    parser.add_argument("--ensembl-base-url", default=ENSEMBL_PLANTS_BASE)
    parser.add_argument("--include-review", action="store_true", help="include rows marked review in crop_scope.tsv")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    crops = read_crops(args.crop_scope, include_review=args.include_review)
    rows = [inventory_ensembl_species(crop, args.ensembl_base_url.rstrip("/")) for crop in crops]
    write_manifest(rows, args.out)
    planned = sum(1 for row in rows if row["status"] == "planned")
    skipped = len(rows) - planned
    print(f"Wrote {args.out}: {planned} planned, {skipped} skipped. No genome files downloaded.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
