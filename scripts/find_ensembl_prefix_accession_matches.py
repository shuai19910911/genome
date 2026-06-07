#!/usr/bin/env python3
"""Find conservative Ensembl candidates whose observed accession matches locally by prefix."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
CANDIDATES = DOCS / "2026-06-07-ensembl-plants-species-candidates.tsv"
INCOMPLETE = DOCS / "incomplete-genome-index.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle, delimiter="\t")]


def accession_prefix(accession: str) -> str:
    return accession.split(".", 1)[0]


def main() -> int:
    incomplete = read_tsv(INCOMPLETE)
    by_prefix: dict[str, list[dict[str, str]]] = {}
    for row in incomplete:
        by_prefix.setdefault(accession_prefix(row["assembly_accession"]), []).append(row)

    fields = [
        "species",
        "ensembl_dir",
        "match_type",
        "observed_accession",
        "local_accession",
        "local_species_dir",
        "gff3_url",
        "gtf_url",
    ]
    writer = csv.DictWriter(__import__("sys").stdout, fieldnames=fields, delimiter="\t")
    writer.writeheader()
    for row in read_tsv(CANDIDATES):
        if row["has_gff3"] != "yes" or row["has_gtf"] != "yes":
            continue
        observed = [item for item in row["observed_accessions"].split(";") if item]
        for item in observed:
            matches = by_prefix.get(accession_prefix(item), [])
            if len(matches) != 1:
                continue
            local = matches[0]
            if local["species"] != row["species"]:
                continue
            writer.writerow(
                {
                    "species": row["species"],
                    "ensembl_dir": row["ensembl_dir"],
                    "match_type": row["match_type"],
                    "observed_accession": item,
                    "local_accession": local["assembly_accession"],
                    "local_species_dir": local["species_dir"],
                    "gff3_url": row["gff3_url"],
                    "gtf_url": row["gtf_url"],
                }
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
