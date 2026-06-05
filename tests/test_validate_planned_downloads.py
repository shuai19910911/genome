#!/usr/bin/env python3
from __future__ import annotations

import csv
import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_planned_downloads.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_planned_downloads", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not import {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


validator = load_validator()


def valid_row(species: str = "Oryza sativa", accession: str = "GCA_TEST001") -> dict[str, str]:
    return {
        "species": species,
        "common_name": "rice",
        "taxon_id": "4530",
        "assembly_accession": accession,
        "assembly_name": "IRGSP-1.0",
        "assembly_level": "Chromosome",
        "source": "Ensembl Plants",
        "source_release": "current",
        "genome_url": "https://example.org/Oryza_sativa.dna.toplevel.fa.gz",
        "annotation_url": "https://example.org/Oryza_sativa.60.gff3.gz",
        "annotation_format": "GFF3",
        "genome_size_bytes": "100",
        "annotation_size_bytes": "10",
        "md5_url": "https://example.org/CHECKSUMS",
        "selection_reason": "strict_crop; test row",
        "status": "planned",
        "skip_reason": "",
    }


class ValidatePlannedDownloadsTests(unittest.TestCase):
    def test_valid_planned_row_has_no_problems(self) -> None:
        self.assertEqual(validator.validate_rows([valid_row()]), [])

    def test_duplicate_species_directory_is_reported(self) -> None:
        rows = [valid_row(), valid_row()]
        problems = validator.validate_rows(rows)
        self.assertTrue(any(problem.startswith("duplicate_species_dir") for problem in problems))

    def test_invalid_planned_fields_are_reported(self) -> None:
        row = valid_row()
        row.update(
            {
                "genome_url": "",
                "annotation_url": "https://example.org/annotation.txt",
                "annotation_format": "BED",
                "genome_size_bytes": "0",
                "annotation_size_bytes": "not-an-int",
            }
        )
        problems = "\n".join(validator.validate_rows([row]))
        self.assertIn("missing_genome_url", problems)
        self.assertIn("unexpected_annotation_suffix", problems)
        self.assertIn("invalid_annotation_format", problems)
        self.assertIn("missing_or_nonpositive_genome_size", problems)
        self.assertIn("missing_or_nonpositive_annotation_size", problems)

    def test_read_manifest_requires_expected_columns(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.tsv"
            path.write_text("species\tstatus\nOryza sativa\tplanned\n")
            with self.assertRaisesRegex(ValueError, "missing required columns"):
                validator.read_manifest(path)

    def test_read_manifest_accepts_expected_columns(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "planned.tsv"
            with path.open("w", newline="") as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=sorted(validator.REQUIRED_COLUMNS),
                    delimiter="\t",
                    lineterminator="\n",
                )
                writer.writeheader()
                row = valid_row()
                writer.writerow({column: row[column] for column in sorted(validator.REQUIRED_COLUMNS)})
            rows = validator.read_manifest(path)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["species"], "Oryza sativa")


if __name__ == "__main__":
    unittest.main()
