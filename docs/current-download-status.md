# 当前基因组下载进展

- 更新时间: 2026-06-07 11:16:51
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
- 没有 README 的目录多为注释缺失失败后留下的未完成目录，后续应优先补注释或统一生成失败说明。
- 大文件和运行日志不提交到 GitHub；GitHub 只记录脚本、清单和进度文档。
