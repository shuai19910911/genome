#!/usr/bin/env python3
"""Archive a validated external annotation into an existing genome directory."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import shutil
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def gzip_ok(path: Path) -> bool:
    with gzip.open(path, "rb") as handle:
        while handle.read(1024 * 1024):
            pass
    return True


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_text(path: Path, content: str) -> None:
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def build_readme_zh(
    metadata: dict[str, object],
    genome: Path,
    gff3: Path,
    gtf: Path,
    checksums_path: Path,
    validation_report: Path,
    source_name: str,
    source_dir: str,
    gff3_url: str,
    gtf_url: str,
    gtf_build_accession: str,
    gtf_genome_version: str,
    validation_summary: str,
    archived_at: str,
) -> str:
    species = metadata.get("species", "")
    accession = metadata.get("assembly_accession", "")
    assembly = metadata.get("assembly_name", "")
    return f"""# {species} {accession}

## 简要说明

这个目录保存一个作物基因组 assembly 及其已经验证可配套使用的注释文件。

- 物种: {species}
- 常用名: {metadata.get("common_name", "")}
- Taxon ID: {metadata.get("taxon_id", "")}
- Assembly accession: {accession}
- Assembly 名称: {assembly}
- Assembly 级别: {metadata.get("assembly_level", "")}
- BioProject: {metadata.get("bioproject", "")}
- 归档时间: {archived_at}

## 基因组来源

- 来源: {metadata.get("source", "")}
- 来源版本: {metadata.get("source_release", "")}
- 原始下载地址: {metadata.get("genome_url", "")}
- 本地文件: `{rel(genome)}`
- 本地压缩文件大小: {genome.stat().st_size} bytes

## 注释来源

- 来源: {source_name}
- 来源目录: {source_dir}
- GFF3 原始地址: {gff3_url}
- GTF 原始地址: {gtf_url}
- 本地 GFF3: `{rel(gff3)}` ({gff3.stat().st_size} bytes)
- 本地 GTF: `{rel(gtf)}` ({gtf.stat().st_size} bytes)

## 版本差异和验证结论

- Ensembl GTF 记录的 genome-build-accession: {gtf_build_accession}
- Ensembl GTF 记录的 genome-version: {gtf_genome_version}
- 本地基因组 accession: {accession}
- 验证结论: {validation_summary}
- 验证报告: `{rel(validation_report)}`

注意：这里的注释文件来自 Ensembl Plants，而基因组文件来自 NCBI GenBank。GTF 元数据中的 accession 版本与本地 NCBI accession 版本不完全相同，所以不能只看名字判断是否可用。本次按染色体别名和长度做了校验，21 条主染色体全部匹配，因此作为同坐标注释候选归档。

## 校验和

- SHA256 文件: `{rel(checksums_path)}`

## Phytozome 记录

Phytozome 目前暂不下载，只记录为后续可选来源。
"""


def build_readme_en(
    metadata: dict[str, object],
    genome: Path,
    gff3: Path,
    gtf: Path,
    checksums_path: Path,
    validation_report: Path,
    source_name: str,
    source_dir: str,
    gff3_url: str,
    gtf_url: str,
    gtf_build_accession: str,
    gtf_genome_version: str,
    validation_summary: str,
    archived_at: str,
) -> str:
    species = metadata.get("species", "")
    accession = metadata.get("assembly_accession", "")
    assembly = metadata.get("assembly_name", "")
    return f"""# {species} {accession}

## Summary

This directory stores one crop genome assembly and validated matching annotation files.

- Species: {species}
- Common name: {metadata.get("common_name", "")}
- Taxon ID: {metadata.get("taxon_id", "")}
- Assembly accession: {accession}
- Assembly name: {assembly}
- Assembly level: {metadata.get("assembly_level", "")}
- BioProject: {metadata.get("bioproject", "")}
- Archived at: {archived_at}

## Genome Source

- Source: {metadata.get("source", "")}
- Source release: {metadata.get("source_release", "")}
- Original URL: {metadata.get("genome_url", "")}
- Local file: `{rel(genome)}`
- Compressed size: {genome.stat().st_size} bytes

## Annotation Source

- Source: {source_name}
- Source directory: {source_dir}
- GFF3 URL: {gff3_url}
- GTF URL: {gtf_url}
- Local GFF3: `{rel(gff3)}` ({gff3.stat().st_size} bytes)
- Local GTF: `{rel(gtf)}` ({gtf.stat().st_size} bytes)

## Version Note and Validation

- Ensembl GTF genome-build-accession: {gtf_build_accession}
- Ensembl GTF genome-version: {gtf_genome_version}
- Local genome accession: {accession}
- Validation summary: {validation_summary}
- Validation report: `{rel(validation_report)}`

The annotation files come from Ensembl Plants, while the genome file comes from NCBI GenBank. The accession versions are not identical in the metadata, so this pair was validated by chromosome alias and sequence length before being archived. All 21 primary chromosomes matched.

## Checksums

- SHA256 file: `{rel(checksums_path)}`

## Phytozome Note

Phytozome is not downloaded at this stage; it is only recorded as a possible later source.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--species-dir", required=True)
    parser.add_argument("--metadata", required=True)
    parser.add_argument("--genome", required=True)
    parser.add_argument("--gff3", required=True)
    parser.add_argument("--gtf", required=True)
    parser.add_argument("--validation-report", required=True)
    parser.add_argument("--source-name", required=True)
    parser.add_argument("--source-dir", required=True)
    parser.add_argument("--gff3-url", required=True)
    parser.add_argument("--gtf-url", required=True)
    parser.add_argument("--gtf-build-accession", required=True)
    parser.add_argument("--gtf-genome-version", required=True)
    parser.add_argument("--validation-summary", required=True)
    args = parser.parse_args()

    species_dir = ROOT / args.species_dir
    metadata_path = ROOT / args.metadata
    genome = ROOT / args.genome
    src_gff3 = ROOT / args.gff3
    src_gtf = ROOT / args.gtf
    validation_report = ROOT / args.validation_report
    annotation_dir = species_dir / "annotation"
    checksums_dir = species_dir / "checksums"
    provenance_path = species_dir / "metadata" / "external_annotation_source.json"

    for path in [species_dir, metadata_path, genome, src_gff3, src_gtf, validation_report]:
        if not path.exists():
            raise FileNotFoundError(path)

    gzip_ok(src_gff3)
    gzip_ok(src_gtf)

    annotation_dir.mkdir(parents=True, exist_ok=True)
    checksums_dir.mkdir(parents=True, exist_ok=True)
    (species_dir / "metadata").mkdir(parents=True, exist_ok=True)

    dest_gff3 = annotation_dir / src_gff3.name
    dest_gtf = annotation_dir / src_gtf.name
    shutil.copy2(src_gff3, dest_gff3)
    shutil.copy2(src_gtf, dest_gtf)

    archived_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z").strip()
    metadata = load_json(metadata_path)
    checksums = {
        rel(genome): sha256_file(genome),
        rel(dest_gff3): sha256_file(dest_gff3),
        rel(dest_gtf): sha256_file(dest_gtf),
    }
    checksums_path = checksums_dir / "SHA256SUMS"
    write_text(checksums_path, "\n".join(f"{digest}  {path}" for path, digest in checksums.items()))

    provenance = {
        "archived_at": archived_at,
        "source_name": args.source_name,
        "source_dir": args.source_dir,
        "gff3_url": args.gff3_url,
        "gtf_url": args.gtf_url,
        "gtf_build_accession": args.gtf_build_accession,
        "gtf_genome_version": args.gtf_genome_version,
        "validation_summary": args.validation_summary,
        "validation_report": rel(validation_report),
        "local_gff3": rel(dest_gff3),
        "local_gtf": rel(dest_gtf),
        "sha256": checksums,
    }
    provenance_path.write_text(json.dumps(provenance, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    write_text(
        species_dir / "README.zh.md",
        build_readme_zh(
            metadata,
            genome,
            dest_gff3,
            dest_gtf,
            checksums_path,
            validation_report,
            args.source_name,
            args.source_dir,
            args.gff3_url,
            args.gtf_url,
            args.gtf_build_accession,
            args.gtf_genome_version,
            args.validation_summary,
            archived_at,
        ),
    )
    write_text(
        species_dir / "README.md",
        build_readme_en(
            metadata,
            genome,
            dest_gff3,
            dest_gtf,
            checksums_path,
            validation_report,
            args.source_name,
            args.source_dir,
            args.gff3_url,
            args.gtf_url,
            args.gtf_build_accession,
            args.gtf_genome_version,
            args.validation_summary,
            archived_at,
        ),
    )

    print(f"archived_gff3={rel(dest_gff3)}")
    print(f"archived_gtf={rel(dest_gtf)}")
    print(f"readme_zh={rel(species_dir / 'README.zh.md')}")
    print(f"readme_en={rel(species_dir / 'README.md')}")
    print(f"checksums={rel(checksums_path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
