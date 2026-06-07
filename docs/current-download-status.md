# 当前基因组下载进展

- 更新时间: 2026-06-07 12:08:47 CST
- 完成记录数: 149
- 失败记录数: 1755
- 已生成 assembly 目录数: 1906
- 已生成 README 的完成目录数: 151
- 本地数据总量: 901866154665 bytes (839.93 GiB)
- 下载管理进程数: 0
- aria2 活动下载数: 0
- 最近速度: 0.00 MiB/s

## 当前分类结果

- 有 genome 和至少一种注释的目录: 156
- 只有 genome、缺少 GFF3/GTF 注释的目录: 1750
- 完整索引: `docs/completed-genome-index.tsv`
- 未完整索引: `docs/incomplete-genome-index.tsv`

## NCBI Datasets 小样本测试

- 已在 `genome_down` 环境安装 `ncbi-datasets-cli`。
- 当前 `datasets` 版本: 18.29.1。
- 抽样测试 10 个 genome-only 的 GenBank (`GCA`) accession，覆盖甜菜、大麦、水稻、玉米、西瓜、油菜、马铃薯、葡萄、小麦、大豆。
- 测试结果: 10 个样本均没有从 Datasets 得到 GFF3/GTF 注释；请求 `--include gff3` 或 `--include gtf` 时 CLI 会崩溃。
- 详细结果: `docs/2026-06-07-datasets-annotation-test.md` 和 `docs/2026-06-07-datasets-annotation-test.tsv`。

## Ensembl Plants 候选匹配

- 已建立 Ensembl Plants FTP 候选匹配脚本，只抓目录索引，不下载注释大文件。
- 本次扫描失败最多的前 12 个物种，每个物种最多 25 个 Ensembl 目录。
- 结果: 找到 70 个同物种候选目录，其中 1 个 accession 级精确候选。
- 精确候选: `GCA_949126075.2`，物种为 `Triticum aestivum`，Ensembl 目录为 `triticum_aestivum_paragon`，同时有 GFF3 和 GTF。
- 详细结果: `docs/2026-06-07-ensembl-plants-candidate-map.md`、`docs/2026-06-07-ensembl-plants-exact-matches.tsv`、`docs/2026-06-07-ensembl-plants-species-candidates.tsv`。

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
- Ensembl Plants 只发现少量 accession 级精确候选；同物种候选不能直接混用，必须先做 assembly/cultivar/坐标验证。
- 没有 README 的目录多为注释缺失失败后留下的未完成目录，后续应优先补注释或统一生成失败说明。
- 大文件和运行日志不提交到 GitHub；GitHub 只记录脚本、清单和进度文档。
