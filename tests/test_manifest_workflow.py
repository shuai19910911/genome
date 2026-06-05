#!/usr/bin/env python3
from __future__ import annotations

import csv
import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "download_from_manifest.py"


def load_downloader():
    spec = importlib.util.spec_from_file_location("download_from_manifest", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not import {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


downloader = load_downloader()


def example_row() -> dict[str, str]:
    return {
        "species": "Oryza sativa",
        "common_name": "rice",
        "taxon_id": "4530",
        "assembly_accession": "GCA_TEST001",
        "assembly_name": "IRGSP-1.0",
        "assembly_level": "Chromosome",
        "source": "Ensembl Plants",
        "source_release": "current",
        "genome_url": "https://example.org/Oryza_sativa.dna.toplevel.fa.gz",
        "annotation_url": "https://example.org/Oryza_sativa.60.gff3.gz",
        "annotation_format": "GFF3",
        "genome_size_bytes": "123",
        "annotation_size_bytes": "45",
        "md5_url": "https://example.org/CHECKSUMS",
        "selection_reason": "strict_crop; test row",
        "status": "planned",
        "skip_reason": "",
    }


class ManifestWorkflowTests(unittest.TestCase):
    def test_species_dir_name_includes_accession(self) -> None:
        self.assertEqual(downloader.species_dir_name(example_row()), "Oryza_sativa_GCA_TEST001")

    def test_dry_run_does_not_create_species_directory(self) -> None:
        row = example_row()
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            result = downloader.process_row(row, out, execute=False, retries=1, sleep_seconds=0)
            self.assertEqual(result["validation_status"], "dry_run")
            self.assertFalse((out / "Oryza_sativa_GCA_TEST001").exists())
            self.assertTrue(result["genome_path"].endswith("Oryza_sativa.dna.toplevel.fa.gz"))
            self.assertTrue(result["annotation_path"].endswith("Oryza_sativa.60.gff3.gz"))

    def test_manifest_requires_expected_columns(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad_manifest.tsv"
            path.write_text("species\tstatus\nOryza sativa\tplanned\n")
            with self.assertRaisesRegex(ValueError, "missing required columns"):
                downloader.read_manifest(path)

    def test_read_manifest_accepts_required_columns(self) -> None:
        row = example_row()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "planned_downloads.tsv"
            with path.open("w", newline="") as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=sorted(downloader.REQUIRED_COLUMNS),
                    delimiter="\t",
                    lineterminator="\n",
                )
                writer.writeheader()
                writer.writerow({column: row[column] for column in sorted(downloader.REQUIRED_COLUMNS)})
            rows = downloader.read_manifest(path)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["species"], "Oryza sativa")

    def test_writes_english_and_chinese_readmes(self) -> None:
        row = example_row()
        with tempfile.TemporaryDirectory() as tmp:
            species_dir = Path(tmp) / "Oryza_sativa_GCA_TEST001"
            genome_path = species_dir / "genome" / "Oryza_sativa.dna.toplevel.fa.gz"
            annotation_path = species_dir / "annotation" / "Oryza_sativa.60.gff3.gz"
            genome_path.parent.mkdir(parents=True)
            annotation_path.parent.mkdir(parents=True)
            genome_path.write_bytes(b">chr1\nACGT\n")
            annotation_path.write_text("chr1\tsource\tgene\t1\t4\t.\t+\t.\tID=gene1\n")

            downloader.write_readme(
                row=row,
                species_dir=species_dir,
                genome_path=genome_path,
                annotation_path=annotation_path,
                genome_sha256="genome-sha",
                annotation_sha256="annotation-sha",
                validation_status="ok",
                download_date="2026-06-05",
            )
            downloader.write_readme_zh(
                row=row,
                species_dir=species_dir,
                genome_path=genome_path,
                annotation_path=annotation_path,
                genome_sha256="genome-sha",
                annotation_sha256="annotation-sha",
                validation_status="ok",
                download_date="2026-06-05",
            )

            english = (species_dir / "README.md").read_text()
            chinese = (species_dir / "README.zh.md").read_text()
            self.assertIn("Data source: Ensembl Plants", english)
            self.assertIn("Genome file size bytes", english)
            self.assertIn("数据来源: Ensembl Plants", chinese)
            self.assertIn("基因组本地文件大小 bytes", chinese)
            self.assertIn("校验状态: ok", chinese)


if __name__ == "__main__":
    unittest.main()
