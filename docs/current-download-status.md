# 当前基因组下载进展

- 更新时间: 2026-06-07 19:17:06
- 完成记录数: 149
- 失败记录数: 1755
- 已生成 assembly 目录数: 1906
- 已生成 README 的完成目录数: 217
- 本地数据总量: 903096120356 bytes (841.07 GiB)
- 下载管理进程数: 0
- aria2 活动下载数: 0
- 最近速度: 0.00 MiB/s

## 当前分类结果

- 有 genome 和至少一种注释的目录: 222
- 只有 genome、缺少 GFF3/GTF 注释的目录: 1684
- 完整索引: `docs/completed-genome-index.tsv`
- 未完整索引: `docs/incomplete-genome-index.tsv`

## 外部注释补充

- 已将 62 个 Ensembl Plants 候选 GFF3/GTF 归档到本地 assembly 目录；本次扩大扫描到 31 个当前缺口物种、每物种最多 100 个目录。
- 已归档: `Cucumis_melo_GCA_902497455.1`、`Citrullus_lanatus_GCA_000238415.2`、`Solanum_tuberosum_GCA_014189475.1`、`Malus_domestica_GCA_002114115.1`、14 个 `Oryza sativa` assembly、40 个 `Hordeum vulgare` assembly，以及 4 个 `Triticum aestivum` assembly。
- 本次新增 8 个大麦 HOR 候选: `GCA_949783395.1`、`GCA_949783295.1`、`GCA_949783355.1`、`GCA_949783365.1`、`GCA_949783335.1`、`GCA_949783535.1`、`GCA_949783465.1`、`GCA_949783405.1`，均已按 seqid/长度验证通过。
- 最近四批新增的 30 个大麦候选的 Ensembl GTF metadata accession/genome-version 与本地 assembly 一致，并已按染色体/contig 别名和长度验证通过。
- `Oryza_sativa_GCA_965117765.1` 与 `oryza_sativa_ir64`、`Malus_domestica_GCA_033882605.1` 与 `malus_domestica_golden` 注释候选验证失败，已记录报告但没有归档。
- 水稻 `Oryza_sativa_GCA_001623365.2` / MH63 候选验证失败，已记录报告但没有归档。
- 小麦 `Triticum_aestivum_GCA_902810645.1` / Cadenza、`GCA_902810655.1` / Claire、`GCA_902810685.1` / Robigus 三个候选验证失败，已记录报告但没有归档。
- 小麦 `Triticum_aestivum_GCA_949126075.2` 的 Ensembl GTF 元数据记录 `GCA_949126075.1` / `GCA949126075v1`，与本地 `GCA_949126075.2` 版本不完全相同；已按 21 条主染色体别名和长度验证通过。
- 小麦 `Triticum_aestivum_GCA_910594105.1` / Kariega、`GCA_920937835.1` / Renan、`GCA_937894285.1` / Renan 均已用 Ensembl 完整 GFF3/GTF 验证通过并归档。
- Gramene release-61 已完成扩展候选扫描，前 16 个高缺口物种中发现 69 个同物种候选、7 个 assembly 名称候选、0 个 accession 精确候选。
- Gramene `Oryza_sativa_GCA_965117765.1` / IR64、`Oryza_sativa_GCA_001623365.2` / MH63、`Malus_domestica_GCA_033882605.1` / Golden、`Solanum_lycopersicum_GCA_927333815.3` / SL3.0，以及小麦 Cadenza/Claire/Robigus 候选验证失败，已记录报告但没有归档。
- LegumeInfo 已扫描 Arachis hypogaea、Glycine max、Phaseolus vulgaris、Vigna radiata、Cicer arietinum 5 个豆科作物目录，找到 2 个 assembly 名称候选。
- LegumeInfo 大豆 `Glycine_max_GCA_002905335.2` / Lee 候选只有 GFF3、没有 GTF；已用 30 个 feature seqid 最大 end 坐标不越界规则验证通过并归档。
- LegumeInfo 花生 `Arachis_hypogaea_GCA_028451205.1` / BaileyII 候选验证失败，已记录报告但没有归档。
- MaizeGDB 已扫描官方下载目录和 `All_gene_model_GFF/` 汇总目录，在 185 个未完整玉米条目中找到 39 个 assembly 名称候选。
- MaizeGDB 玉米 W22、EP1、F7 三个小样本均未通过完整坐标验证；W22 主染色体可对上但 scaffold 长度不一致，EP1/F7 有大量 scaffold seqid 在本地 genome 中缺失，因此没有归档。
- NCBI GenBank assembly_summary 的 `gbrs_paired_asm` 字段在 1703 个未完整条目中找到 9 个 GCA->GCF 配对，其中 3 个 RefSeq GCF 端有 GFF3/GTF。
- RefSeq paired 路线已验证并归档 `Malus_domestica_GCA_042453785.1`、`Oryza_sativa_GCA_034140825.1`、`Solanum_lycopersicum_GCA_036512215.2` 三个候选；虽然 NCBI 记录 `paired_asm_comp=different`，但三者均按 seqid/长度验证通过。
- 详细验证报告在 `docs/2026-06-07-GCA_*-ensembl-*.validation.md`、`docs/2026-06-07-GCA_*-gramene-*.validation.md`、`docs/2026-06-07-GCA_*-legumeinfo-*.validation.md`、`docs/2026-06-07-GCA_*-maizegdb-*.validation.md` 和 `docs/2026-06-07-GCA_*-refseq-paired-*.validation.md`。
- Phytozome 仍按原决定暂不下载，只记录后续可用性。

## 前期测试结论

- 已在 `genome_down` 环境安装 `ncbi-datasets-cli`，版本为 18.29.1。
- 抽样测试 10 个 genome-only 的 GenBank (`GCA`) accession，没有从 Datasets 补到 GFF3/GTF；请求 `--include gff3` 或 `--include gtf` 时 CLI 会崩溃。
- Ensembl Plants 候选扫描已扩展到当前 31 个缺口物种，发现 140 个同物种候选目录、60 个 assembly 名称候选；目前已有 62 个候选完成坐标验证和归档。
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
