# 当前基因组下载进展

- 更新时间: 2026-06-07 14:48:49
- 完成记录数: 149
- 失败记录数: 1755
- 已生成 assembly 目录数: 1906
- 已生成 README 的完成目录数: 193
- 本地数据总量: 902580498711 bytes (840.59 GiB)
- 下载管理进程数: 0
- aria2 活动下载数: 0
- 最近速度: 0.00 MiB/s

## 当前分类结果

- 有 genome 和至少一种注释的目录: 198
- 只有 genome、缺少 GFF3/GTF 注释的目录: 1708
- 完整索引: `docs/completed-genome-index.tsv`
- 未完整索引: `docs/incomplete-genome-index.tsv`

## 外部注释补充

- 已将 42 个 Ensembl Plants 候选 GFF3/GTF 归档到本地 assembly 目录，其中最近两次检查新增 14 个大麦候选。
- 已归档: `Triticum_aestivum_GCA_949126075.2`、`Cucumis_melo_GCA_902497455.1`、`Citrullus_lanatus_GCA_000238415.2`、`Solanum_tuberosum_GCA_014189475.1`、`Malus_domestica_GCA_002114115.1`、13 个 `Oryza sativa` assembly，以及 24 个 `Hordeum vulgare` assembly。
- 最近两次新增的 14 个大麦候选的 Ensembl GTF metadata accession/genome-version 与本地 assembly 一致，并已按染色体/contig 别名和长度验证通过。
- `Oryza_sativa_GCA_965117765.1` 与 `oryza_sativa_ir64`、`Malus_domestica_GCA_033882605.1` 与 `malus_domestica_golden` 注释候选验证失败，已记录报告但没有归档。
- 小麦 `Triticum_aestivum_GCA_949126075.2` 的 Ensembl GTF 元数据记录 `GCA_949126075.1` / `GCA949126075v1`，与本地 `GCA_949126075.2` 版本不完全相同；已按 21 条主染色体别名和长度验证通过。
- 详细验证报告在 `docs/2026-06-07-GCA_*-ensembl-*.validation.md`。
- Phytozome 仍按原决定暂不下载，只记录后续可用性。

## 前期测试结论

- 已在 `genome_down` 环境安装 `ncbi-datasets-cli`，版本为 18.29.1。
- 抽样测试 10 个 genome-only 的 GenBank (`GCA`) accession，没有从 Datasets 补到 GFF3/GTF；请求 `--include gff3` 或 `--include gtf` 时 CLI 会崩溃。
- Ensembl Plants 候选扫描覆盖失败最多的前 12 个物种，发现 70 个同物种候选目录；目前已有 42 个候选完成坐标验证和归档。
- 同物种候选不能直接混用，必须继续按 assembly、品种名、染色体名和长度做验证。

## 各 shard 进展

- download_manifest.shard01.tsv: 完成 35
- download_manifest.shard02.tsv: 完成 38
- download_manifest.shard03.tsv: 完成 36
- download_manifest.shard04.tsv: 完成 40
- failed_downloads.shard01.tsv: 失败 441
- failed_downloads.shard02.tsv: 失败 438
- failed_downloads.shard03.tsv: 失败 440
- failed_downloads.shard04.tsv: 失败 436

## 当前活动下载

- 当前没有 aria2 活动下载。

## 说明

- 失败记录主要来自 NCBI GenBank (`GCA`) 条目缺少 GFF/GTF 注释文件，脚本会快速跳过并记录失败。
- 最新分类显示，未完整目录不是空目录，均已经有 genome 文件；当前主要缺口是 GFF3/GTF 注释。
- Datasets 小样本测试没有解决这些 GCA 注释缺口；下一步应优先按物种进入 Ensembl Plants 和作物专项数据库路线。
- 没有 README 的目录多为注释缺失失败后留下的未完成目录，后续应优先补注释或统一生成失败说明。
- 大文件和运行日志不提交到 GitHub；GitHub 只记录脚本、清单和进度文档。
