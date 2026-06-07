#!/usr/bin/env python3
"""Validate whether an external GFF3/GTF candidate matches a local genome FASTA."""

from __future__ import annotations

import argparse
import csv
import gzip
import re
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def opener(path: Path):
    return gzip.open(path, "rt", errors="replace") if path.suffix == ".gz" else path.open(errors="replace")


def fasta_lengths(path: Path) -> tuple[dict[str, int], dict[str, str]]:
    lengths: dict[str, int] = {}
    aliases: dict[str, str] = {}
    current_id = ""
    current_len = 0
    current_alias = ""
    with opener(path) as handle:
        for line in handle:
            if line.startswith(">"):
                if current_id:
                    lengths[current_id] = current_len
                    if current_alias:
                        aliases[current_alias] = current_id
                current_id = line[1:].split()[0]
                current_alias = normalize_chromosome_name(line[1:].strip())
                current_len = 0
            else:
                current_len += len(line.strip())
        if current_id:
            lengths[current_id] = current_len
            if current_alias:
                aliases[current_alias] = current_id
    return lengths, aliases


def gff3_regions(path: Path) -> dict[str, int]:
    regions: dict[str, int] = {}
    with opener(path) as handle:
        for line in handle:
            if line.startswith("##sequence-region"):
                parts = line.strip().split()
                if len(parts) >= 4:
                    regions[parts[1]] = int(parts[3])
            elif line.startswith("#"):
                continue
            else:
                break
    return regions


def gff3_seqids(path: Path, limit: int = 100000) -> set[str]:
    seqids: set[str] = set()
    with opener(path) as handle:
        seen = 0
        for line in handle:
            if line.startswith("#"):
                continue
            parts = line.split("\t", 1)
            if len(parts) == 2:
                seqids.add(parts[0])
                seen += 1
            if seen >= limit:
                break
    return seqids


def gtf_metadata(path: Path) -> dict[str, str]:
    meta: dict[str, str] = {}
    with opener(path) as handle:
        for line in handle:
            if not line.startswith("#!"):
                break
            if " " in line:
                key, value = line[2:].strip().split(" ", 1)
                meta[key] = value
    return meta


def normalize_chromosome_name(name: str) -> str:
    description_match = re.search(r"chromosome:\s*([0-9][A-Za-z]+)", name, flags=re.I)
    if description_match:
        return description_match.group(1)
    match = re.search(r"\b([1-7][ABD])\b", name)
    if match:
        return match.group(1)
    return name


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--accession", required=True)
    parser.add_argument("--genome", type=Path, required=True)
    parser.add_argument("--gff3", type=Path, required=True)
    parser.add_argument("--gtf", type=Path, required=True)
    parser.add_argument("--output-prefix", type=Path, required=True)
    args = parser.parse_args()

    genome_lengths, genome_aliases = fasta_lengths(args.genome)
    region_lengths = gff3_regions(args.gff3)
    gff_seqids = gff3_seqids(args.gff3)
    meta = gtf_metadata(args.gtf)

    normalized_genome: dict[str, list[tuple[str, int]]] = {}
    for seqid, length in genome_lengths.items():
        normalized_genome.setdefault(normalize_chromosome_name(seqid), []).append((seqid, length))
    for alias, seqid in genome_aliases.items():
        normalized_genome.setdefault(alias, []).append((seqid, genome_lengths[seqid]))

    rows: list[dict[str, object]] = []
    exact_matches = 0
    normalized_matches = 0
    length_mismatches = 0
    missing_regions = 0
    for seqid, ann_length in sorted(region_lengths.items()):
        local_exact = genome_lengths.get(seqid)
        normalized_candidates = normalized_genome.get(seqid, [])
        if local_exact == ann_length:
            status = "exact_seqid_and_length"
            exact_matches += 1
            local_id = seqid
            local_length = local_exact
        elif any(length == ann_length for _, length in normalized_candidates):
            status = "normalized_seqid_and_length"
            normalized_matches += 1
            local_id, local_length = next((item for item in normalized_candidates if item[1] == ann_length))
        elif local_exact is None and not normalized_candidates:
            status = "missing_in_genome"
            missing_regions += 1
            local_id = ""
            local_length = ""
        else:
            status = "length_mismatch"
            length_mismatches += 1
            local_id = seqid if local_exact is not None else ";".join(item[0] for item in normalized_candidates[:3])
            local_length = local_exact if local_exact is not None else ";".join(str(item[1]) for item in normalized_candidates[:3])
        rows.append(
            {
                "annotation_seqid": seqid,
                "annotation_length": ann_length,
                "local_seqid": local_id,
                "local_length": local_length,
                "status": status,
            }
        )

    covered_seqids = len(gff_seqids & set(region_lengths))
    pass_validation = (
        len(region_lengths) > 0
        and missing_regions == 0
        and length_mismatches == 0
        and (exact_matches + normalized_matches) == len(region_lengths)
    )

    args.output_prefix.parent.mkdir(parents=True, exist_ok=True)
    output_prefix = args.output_prefix if args.output_prefix.is_absolute() else ROOT / args.output_prefix
    tsv_path = Path(str(output_prefix) + ".seqid-validation.tsv")
    with tsv_path.open("w", newline="") as handle:
        fields = ["annotation_seqid", "annotation_length", "local_seqid", "local_length", "status"]
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    md_path = Path(str(output_prefix) + ".validation.md")
    lines = [
        "# 外部注释候选验证报告",
        "",
        f"- 检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"- accession: {args.accession}",
        f"- genome: `{args.genome}`",
        f"- GFF3: `{args.gff3}`",
        f"- GTF: `{args.gtf}`",
        f"- GTF genome-build-accession: {meta.get('genome-build-accession', '未记录')}",
        f"- GTF genome-version: {meta.get('genome-version', '未记录')}",
        f"- genome 序列数: {len(genome_lengths)}",
        f"- GFF3 sequence-region 数: {len(region_lengths)}",
        f"- GFF3 已抽样 feature seqid 覆盖 region 数: {covered_seqids}",
        f"- exact seqid+length 匹配数: {exact_matches}",
        f"- 归一化 seqid+length 匹配数: {normalized_matches}",
        f"- 长度不一致数: {length_mismatches}",
        f"- genome 缺失 region 数: {missing_regions}",
        f"- 验证结论: {'通过，可作为同坐标注释候选' if pass_validation else '未通过，不能直接合并'}",
        "",
        "## 说明",
        "",
        "- 归一化匹配只处理小麦染色体名这类情况，例如 FASTA 头中带有额外描述但可提取 `1A`、`1B` 等染色体名。",
        "- 如果 GTF 记录的 accession 版本和本地 genome accession 版本不同，即使长度匹配，也需要在 README 中明确来源差异。",
        f"- 明细表: `{tsv_path.relative_to(ROOT) if tsv_path.is_relative_to(ROOT) else tsv_path}`",
        "",
    ]
    md_path.write_text("\n".join(lines))
    print(f"validation_pass={pass_validation}")
    print(f"wrote {md_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
