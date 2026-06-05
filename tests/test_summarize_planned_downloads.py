#!/usr/bin/env python3
from __future__ import annotations

import csv
import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "summarize_planned_downloads.py"


def load_summarizer():
    spec = importlib.util.spec_from_file_location("summarize_planned_downloads", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not import {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


summarizer = load_summarizer()


def write_manifest(path: Path, rows: list[dict[str, str]]) -> None:
    columns = [
        "species",
        "common_name",
        "source",
        "genome_size_bytes",
        "annotation_size_bytes",
        "annotation_format",
        "status",
        "skip_reason",
    ]
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


class SummarizePlannedDownloadsTests(unittest.TestCase):
    def test_summarize_counts_sizes_sources_and_skip_reasons(self) -> None:
        rows = [
            {
                "species": "Oryza sativa",
                "common_name": "rice",
                "source": "Ensembl Plants",
                "genome_size_bytes": "100",
                "annotation_size_bytes": "10",
                "annotation_format": "GFF3",
                "status": "planned",
                "skip_reason": "",
            },
            {
                "species": "Zea mays",
                "common_name": "maize",
                "source": "Ensembl Plants",
                "genome_size_bytes": "200",
                "annotation_size_bytes": "20",
                "annotation_format": "GFF3",
                "status": "planned",
                "skip_reason": "",
            },
            {
                "species": "Missing crop",
                "common_name": "missing",
                "source": "Ensembl Plants",
                "genome_size_bytes": "",
                "annotation_size_bytes": "",
                "annotation_format": "",
                "status": "skipped",
                "skip_reason": "missing_genome_fasta;missing_gff_or_gtf",
            },
        ]
        summary = summarizer.summarize(rows)
        self.assertEqual(summary["total_rows"], 3)
        self.assertEqual(summary["planned_rows"], 2)
        self.assertEqual(summary["skipped_rows"], 1)
        self.assertEqual(summary["genome_bytes"], 300)
        self.assertEqual(summary["annotation_bytes"], 30)
        self.assertEqual(summary["total_bytes"], 330)
        self.assertEqual(summary["sources"]["Ensembl Plants"], 2)
        self.assertEqual(summary["annotation_formats"]["GFF3"], 2)
        self.assertEqual(summary["skip_reasons"]["missing_genome_fasta"], 1)
        self.assertEqual(summary["skip_reasons"]["missing_gff_or_gtf"], 1)

    def test_read_rows_requires_expected_columns(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.tsv"
            path.write_text("species\tstatus\nOryza sativa\tplanned\n")
            with self.assertRaisesRegex(ValueError, "missing required columns"):
                summarizer.read_rows(path)

    def test_read_rows_accepts_expected_columns(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "planned.tsv"
            write_manifest(
                path,
                [
                    {
                        "species": "Oryza sativa",
                        "common_name": "rice",
                        "source": "Ensembl Plants",
                        "genome_size_bytes": "100",
                        "annotation_size_bytes": "10",
                        "annotation_format": "GFF3",
                        "status": "planned",
                        "skip_reason": "",
                    }
                ],
            )
            rows = summarizer.read_rows(path)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["species"], "Oryza sativa")


if __name__ == "__main__":
    unittest.main()
