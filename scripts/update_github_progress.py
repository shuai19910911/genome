#!/usr/bin/env python3
"""Write a Chinese progress snapshot for GitHub."""

from __future__ import annotations

import json
import subprocess
import csv
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "current-download-status.md"
STATE = ROOT / "download.monitor.state.json"
MONITOR_LOG = ROOT / "download.monitor.log"
LOCAL_REPORTS = ROOT / "local_reports"
COMPLETE_INDEX = LOCAL_REPORTS / "completed-genome-index.tsv"
INCOMPLETE_INDEX = LOCAL_REPORTS / "incomplete-genome-index.tsv"


def count_data_rows(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open() as handle:
        return max(0, sum(1 for _ in handle) - 1)


def sum_index_bytes(paths: list[Path]) -> int:
    total = 0
    for path in paths:
        if not path.exists():
            continue
        with path.open(newline="") as handle:
            reader = csv.DictReader(handle, delimiter="\t")
            for row in reader:
                try:
                    total += int(row.get("directory_size_bytes", "") or 0)
                except ValueError:
                    continue
    return total


def command_lines(pattern: str) -> list[str]:
    result = subprocess.run(["pgrep", "-af", pattern], text=True, capture_output=True, check=False)
    return [line for line in result.stdout.splitlines() if line.strip()]


def load_state() -> dict[str, object]:
    if not STATE.exists():
        return {}
    try:
        return json.loads(STATE.read_text())
    except json.JSONDecodeError:
        return {}


def format_bytes(value: int) -> str:
    gib = value / 1024 / 1024 / 1024
    return f"{value} bytes ({gib:.2f} GiB)"


def latest_speed_line() -> str:
    if not MONITOR_LOG.exists():
        return "暂无；等待自动监控生成速度基准。"
    for line in reversed(MONITOR_LOG.read_text(errors="replace").splitlines()):
        if line.startswith("距上次平均速度 MiB/s:"):
            value = line.split(":", 1)[1].strip()
            return f"{value} MiB/s"
    return "暂无；等待自动监控生成速度基准。"


def main() -> int:
    now = datetime.now()
    stamp = now.strftime("%Y-%m-%d %H:%M:%S")

    def item(text: str) -> str:
        return f"- [{stamp}] {text}"

    manifests = sorted(ROOT.glob("download_manifest.shard*.tsv"))
    failures = sorted(ROOT.glob("failed_downloads.shard*.tsv"))
    completed = sum(count_data_rows(path) for path in manifests)
    failed = sum(count_data_rows(path) for path in failures)
    complete_index_rows = count_data_rows(COMPLETE_INDEX)
    incomplete_index_rows = count_data_rows(INCOMPLETE_INDEX)
    dirs = len([path for path in ROOT.glob("*_GC[AF]_*") if path.is_dir()])
    readmes = len(list(ROOT.glob("*_GC[AF]_*" + "/README.md")))
    aria2 = command_lines("aria2c")
    managers = command_lines("download_from_manifest")
    state = load_state()
    indexed_bytes = sum_index_bytes([COMPLETE_INDEX, INCOMPLETE_INDEX])
    total_bytes = indexed_bytes or int(state.get("downloaded_bytes", 0) or 0)

    speed_line = latest_speed_line()

    lines = [
        "# 当前基因组下载进展",
        "",
        item(f"更新时间: {stamp}"),
        item(f"完成记录数: {completed}"),
        item(f"失败记录数: {failed}"),
        item(f"已生成 assembly 目录数: {dirs}"),
        item(f"已生成 README 的完成目录数: {readmes}"),
        item(f"本地数据总量: {format_bytes(total_bytes) if total_bytes else '暂无统计'}"),
        item(f"下载管理进程数: {len(managers)}"),
        item(f"aria2 活动下载数: {len(aria2)}"),
        item(f"最近速度: {speed_line}"),
        "",
        "## 当前分类结果",
        "",
        item(f"有 genome 和至少一种注释的目录: {complete_index_rows}"),
        item(f"只有 genome、缺少 GFF3/GTF 注释的目录: {incomplete_index_rows}"),
        item(f"完整索引保留本地: `{COMPLETE_INDEX.relative_to(ROOT)}`"),
        item(f"未完整索引保留本地: `{INCOMPLETE_INDEX.relative_to(ROOT)}`"),
        "",
        "## 外部注释补充",
        "",
        item("已将 99 个 Ensembl Plants 候选 GFF3/GTF 归档到本地 assembly 目录；本次扩大扫描到 31 个当前缺口物种、每物种最多 100 个目录。"),
        item("已归档: `Cucumis_melo_GCA_902497455.1`、`Citrullus_lanatus_GCA_000238415.2`、`Solanum_tuberosum_GCA_014189475.1`、`Malus_domestica_GCA_002114115.1`、`Saccharum_spontaneum_GCA_003544955.1`、14 个 `Oryza sativa` assembly、76 个 `Hordeum vulgare` assembly，以及 4 个 `Triticum aestivum` assembly。"),
        item("本次新增 `Saccharum_spontaneum_GCA_003544955.1`，已按 seqid/长度验证通过；`Solanum_lycopersicum_GCA_927333815.3` 的 Ensembl SL3.0 候选验证失败，未归档。"),
        item("当前 Ensembl assembly-name 候选已清空；后续不应自动处理 species-only 候选，除非先建立更严格的 accession/assembly 证据。"),
        item("最近八批新增的 62 个大麦候选的 Ensembl GTF metadata accession/genome-version 与本地 assembly 一致，并已按染色体/contig 别名和长度验证通过。"),
        item("`Oryza_sativa_GCA_965117765.1` 与 `oryza_sativa_ir64`、`Malus_domestica_GCA_033882605.1` 与 `malus_domestica_golden` 注释候选验证失败，已记录报告但没有归档。"),
        item("水稻 `Oryza_sativa_GCA_001623365.2` / MH63 候选验证失败，已记录报告但没有归档。"),
        item("小麦 `Triticum_aestivum_GCA_902810645.1` / Cadenza、`GCA_902810655.1` / Claire、`GCA_902810685.1` / Robigus 三个候选验证失败，已记录报告但没有归档。"),
        item("小麦 `Triticum_aestivum_GCA_949126075.2` 的 Ensembl GTF 元数据记录 `GCA_949126075.1` / `GCA949126075v1`，与本地 `GCA_949126075.2` 版本不完全相同；已按 21 条主染色体别名和长度验证通过。"),
        item("小麦 `Triticum_aestivum_GCA_910594105.1` / Kariega、`GCA_920937835.1` / Renan、`GCA_937894285.1` / Renan 均已用 Ensembl 完整 GFF3/GTF 验证通过并归档。"),
        item("Gramene release-61 已完成扩展候选扫描，前 16 个高缺口物种中发现 69 个同物种候选、7 个 assembly 名称候选、0 个 accession 精确候选。"),
        item("Gramene `Oryza_sativa_GCA_965117765.1` / IR64、`Oryza_sativa_GCA_001623365.2` / MH63、`Malus_domestica_GCA_033882605.1` / Golden、`Solanum_lycopersicum_GCA_927333815.3` / SL3.0，以及小麦 Cadenza/Claire/Robigus 候选验证失败，已记录报告但没有归档。"),
        item("LegumeInfo 已扫描 Arachis hypogaea、Glycine max、Phaseolus vulgaris、Vigna radiata、Cicer arietinum 5 个豆科作物目录，找到 2 个 assembly 名称候选。"),
        item("LegumeInfo 大豆 `Glycine_max_GCA_002905335.2` / Lee 候选只有 GFF3、没有 GTF；已用 30 个 feature seqid 最大 end 坐标不越界规则验证通过并归档。"),
        item("LegumeInfo 花生 `Arachis_hypogaea_GCA_028451205.1` / BaileyII 候选验证失败，已记录报告但没有归档。"),
        item("MaizeGDB 已扫描官方下载目录和 `All_gene_model_GFF/` 汇总目录，在 185 个未完整玉米条目中找到 39 个 assembly 名称候选。"),
        item("MaizeGDB 玉米 W22、EP1、F7 三个小样本均未通过完整坐标验证；W22 主染色体可对上但 scaffold 长度不一致，EP1/F7 有大量 scaffold seqid 在本地 genome 中缺失，因此没有归档。"),
        item("NCBI GenBank assembly_summary 的 `gbrs_paired_asm` 字段在 1703 个未完整条目中找到 9 个 GCA->GCF 配对，其中 3 个 RefSeq GCF 端有 GFF3/GTF。"),
        item("RefSeq paired 路线已验证并归档 `Malus_domestica_GCA_042453785.1`、`Oryza_sativa_GCA_034140825.1`、`Solanum_lycopersicum_GCA_036512215.2` 三个候选；虽然 NCBI 记录 `paired_asm_comp=different`，但三者均按 seqid/长度验证通过。"),
        item("单条验证报告和中间候选/索引/统计表保留在本地 `validation_reports/` 与 `local_reports/`，不再上传 GitHub；GitHub 只保留关键进展文档。"),
        item("Phytozome 仍按原决定暂不下载，只记录后续可用性。"),
        "",
        "## 前期测试结论",
        "",
        item("已在 `genome_down` 环境安装 `ncbi-datasets-cli`，版本为 18.29.1。"),
        item("抽样测试 10 个 genome-only 的 GenBank (`GCA`) accession，没有从 Datasets 补到 GFF3/GTF；请求 `--include gff3` 或 `--include gtf` 时 CLI 会崩溃。"),
        item("Ensembl Plants 候选扫描已扩展到当前 31 个缺口物种，发现 140 个同物种候选目录、60 个 assembly 名称候选；目前已有 99 个候选完成坐标验证和归档。"),
        item("同物种候选不能直接混用，必须继续按 assembly、品种名、染色体名和长度做验证。"),
        "",
        "## 各 shard 进展",
        "",
    ]
    for path in manifests:
        lines.append(item(f"{path.name}: 完成 {count_data_rows(path)}"))
    for path in failures:
        lines.append(item(f"{path.name}: 失败 {count_data_rows(path)}"))

    lines.extend(["", "## 当前活动下载", ""])
    if aria2:
        for line in aria2[:12]:
            lines.append(item(f"`{line}`"))
    else:
        lines.append(item("当前没有 aria2 活动下载。"))

    lines.extend(
        [
            "",
            "## 说明",
            "",
            item("失败记录主要来自 NCBI GenBank (`GCA`) 条目缺少 GFF/GTF 注释文件，脚本会快速跳过并记录失败。"),
            item("最新分类显示，未完整目录不是空目录，均已经有 genome 文件；当前主要缺口是 GFF3/GTF 注释。"),
            item("Datasets 小样本测试没有解决这些 GCA 注释缺口；下一步应优先按物种进入 Ensembl Plants 和作物专项数据库路线。"),
            item("没有 README 的目录多为注释缺失失败后留下的未完成目录，后续应优先补注释或统一生成失败说明。"),
            item("大文件、运行日志和中间数据表不提交到 GitHub；GitHub 只记录脚本和关键进展文档。"),
            "",
        ]
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines))
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
