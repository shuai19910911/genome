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
    current_aliases: set[str] = set()
    with opener(path) as handle:
        for line in handle:
            if line.startswith(">"):
                if current_id:
                    lengths[current_id] = current_len
                    for alias in current_aliases:
                        aliases[alias] = current_id
                current_id = line[1:].split()[0]
                current_aliases = candidate_aliases(line[1:].strip())
                current_len = 0
            else:
                current_len += len(line.strip())
        if current_id:
            lengths[current_id] = current_len
            for alias in current_aliases:
                aliases[alias] = current_id
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


def gff3_feature_max_ends(path: Path) -> dict[str, int]:
    max_ends: dict[str, int] = {}
    with opener(path) as handle:
        for line in handle:
            if line.startswith("#"):
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 5:
                continue
            try:
                end = int(parts[4])
            except ValueError:
                continue
            max_ends[parts[0]] = max(max_ends.get(parts[0], 0), end)
    return max_ends


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
    chromosome_match = re.search(r"\bchromosome\s+([0-9]+[A-Za-z]*)\b", name, flags=re.I)
    if chromosome_match:
        return normalize_seq_label(chromosome_match.group(1))
    contig_match = re.search(r"\bcontig:\s*([A-Za-z]*[0-9]+[A-Za-z]*)\b", name, flags=re.I)
    if contig_match:
        return normalize_seq_label(contig_match.group(1))
    match = re.search(r"\b([1-7][ABD])\b", name)
    if match:
        return match.group(1)
    return normalize_seq_label(name)


def normalize_seq_label(value: str) -> str:
    label = value.strip()
    if label.lower().startswith("chr"):
        label = label[3:]
    if re.fullmatch(r"0+[0-9]+", label):
        return str(int(label))
    return label


def candidate_aliases(name: str) -> set[str]:
    aliases = {name, normalize_chromosome_name(name)}
    for token in re.split(r"[\s,;]+", name):
        token = token.strip()
        if not token:
            continue
        aliases.add(token)
        token = token.removesuffix(".")
        aliases.add(token)
        dotted_parts = token.split(".")
        if dotted_parts:
            aliases.add(dotted_parts[-1])
        if len(dotted_parts) >= 2:
            aliases.add(".".join(dotted_parts[-2:]))
        if len(dotted_parts) >= 3:
            aliases.add(".".join(dotted_parts[-3:]))
        gm_match = re.fullmatch(r"Gm0*([0-9]+)", dotted_parts[-1], flags=re.I)
        if gm_match:
            number = str(int(gm_match.group(1)))
            aliases.update({number, f"chr{number}", f"Gm{int(number):02d}"})
        scaffold_match = re.fullmatch(r"Scaffold_0*([0-9]+)", dotted_parts[-1], flags=re.I)
        if scaffold_match:
            number = str(int(scaffold_match.group(1)))
            aliases.update({f"Scaffold_{int(number):03d}", f"Scaffold_{number}"})
        sc_match = re.fullmatch(r"sc0*([0-9]+)", dotted_parts[-1], flags=re.I)
        if sc_match:
            number = str(int(sc_match.group(1)))
            aliases.update({f"sc{number}", f"Lee.sc{number}"})
    for pattern in [
        r"chromosome:\s*([0-9]+[A-Za-z]*)",
        r"\bchromosome\s+([0-9]+[A-Za-z]*)\b",
        r"\bcontig:\s*([A-Za-z]*[0-9]+[A-Za-z]*)\b",
    ]:
        for match in re.finditer(pattern, name, flags=re.I):
            raw = match.group(1)
            normalized = normalize_seq_label(raw)
            aliases.add(raw)
            aliases.add(normalized)
            aliases.add(f"chr{normalized}")
            if raw.lower().startswith("chr") and normalized.isdigit():
                aliases.add(f"contig{int(normalized) + 1}")
    return {alias for alias in aliases if alias}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--accession", required=True)
    parser.add_argument("--genome", type=Path, required=True)
    parser.add_argument("--gff3", type=Path, required=True)
    parser.add_argument("--gtf", type=Path)
    parser.add_argument("--output-prefix", type=Path, required=True)
    args = parser.parse_args()

    genome_lengths, genome_aliases = fasta_lengths(args.genome)
    region_lengths = gff3_regions(args.gff3)
    gff_seqids = gff3_seqids(args.gff3)
    feature_max_ends = gff3_feature_max_ends(args.gff3)
    meta = gtf_metadata(args.gtf) if args.gtf else {}

    normalized_genome: dict[str, list[tuple[str, int]]] = {}
    for seqid, length in genome_lengths.items():
        for alias in candidate_aliases(seqid):
            normalized_genome.setdefault(alias, []).append((seqid, length))
    for alias, seqid in genome_aliases.items():
        normalized_genome.setdefault(alias, []).append((seqid, genome_lengths[seqid]))

    length_to_seqids: dict[int, list[str]] = {}
    for seqid, length in genome_lengths.items():
        length_to_seqids.setdefault(length, []).append(seqid)

    rows: list[dict[str, object]] = []
    exact_matches = 0
    normalized_matches = 0
    unique_length_matches = 0
    length_mismatches = 0
    missing_regions = 0
    validation_targets = dict(region_lengths)
    feature_bound_seqids: set[str] = set()
    for seqid, max_end in feature_max_ends.items():
        if seqid not in validation_targets:
            validation_targets[seqid] = max_end
            feature_bound_seqids.add(seqid)
    used_feature_bounds = bool(feature_bound_seqids) or not region_lengths
    for seqid, ann_length in sorted(validation_targets.items()):
        target_uses_feature_bounds = seqid in feature_bound_seqids or not region_lengths
        local_exact = genome_lengths.get(seqid)
        normalized_candidates: list[tuple[str, int]] = []
        seen_candidates: set[tuple[str, int]] = set()
        for alias in candidate_aliases(seqid):
            for item in normalized_genome.get(alias, []):
                if item not in seen_candidates:
                    normalized_candidates.append(item)
                    seen_candidates.add(item)
        unique_length_ids = length_to_seqids.get(ann_length, [])
        if target_uses_feature_bounds and local_exact is not None and local_exact >= ann_length:
            status = "exact_seqid_feature_within_length"
            exact_matches += 1
            local_id = seqid
            local_length = local_exact
        elif not target_uses_feature_bounds and local_exact == ann_length:
            status = "exact_seqid_and_length"
            exact_matches += 1
            local_id = seqid
            local_length = local_exact
        elif target_uses_feature_bounds and any(length >= ann_length for _, length in normalized_candidates):
            status = "normalized_seqid_feature_within_length"
            normalized_matches += 1
            local_id, local_length = next((item for item in normalized_candidates if item[1] >= ann_length))
        elif not target_uses_feature_bounds and any(length == ann_length for _, length in normalized_candidates):
            status = "normalized_seqid_and_length"
            normalized_matches += 1
            local_id, local_length = next((item for item in normalized_candidates if item[1] == ann_length))
        elif not target_uses_feature_bounds and len(unique_length_ids) == 1:
            status = "unique_length_match"
            unique_length_matches += 1
            local_id = unique_length_ids[0]
            local_length = ann_length
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

    covered_seqids = len(gff_seqids & set(validation_targets))
    pass_validation = (
        len(validation_targets) > 0
        and missing_regions == 0
        and length_mismatches == 0
        and (exact_matches + normalized_matches + unique_length_matches) == len(validation_targets)
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
        f"- GTF: `{args.gtf}`" if args.gtf else "- GTF: 未提供",
        f"- GTF genome-build-accession: {meta.get('genome-build-accession', '未提供')}",
        f"- GTF genome-version: {meta.get('genome-version', '未提供')}",
        f"- genome 序列数: {len(genome_lengths)}",
        f"- GFF3 sequence-region 数: {len(region_lengths)}",
        f"- GFF3 feature seqid 数: {len(feature_max_ends)}",
        f"- 使用 feature 最大 end 坐标兜底验证: {'是' if used_feature_bounds else '否'}",
        f"- GFF3 已抽样 feature seqid 覆盖 region 数: {covered_seqids}",
        f"- exact seqid+length 匹配数: {exact_matches}",
        f"- 归一化 seqid+length 匹配数: {normalized_matches}",
        f"- 唯一长度匹配数: {unique_length_matches}",
        f"- 长度不一致数: {length_mismatches}",
        f"- genome 缺失 region 数: {missing_regions}",
        f"- 验证结论: {'通过，可作为同坐标注释候选' if pass_validation else '未通过，不能直接合并'}",
        "",
        "## 说明",
        "",
        "- 归一化匹配处理 FASTA 头中的常见染色体/contig 别名，例如 `chromosome 1`、`chromosome: 1A`、`contig: chr01`。",
        "- 唯一长度匹配表示该注释 region 的长度在本地 genome 中只出现一次；这只能作为 accession/genome-version 明确对应时的补充证据。",
        "- 如果 GFF3 没有 `##sequence-region`，则使用每个 feature seqid 的最大 end 坐标兜底验证；这种验证能确认坐标不越界，但不能证明整条序列长度完全一致。",
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
