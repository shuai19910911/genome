# 当前基因组下载进展

- 更新时间: 2026-06-06 19:46:02
- 完成记录数: 149
- 失败记录数: 1755
- 已生成 assembly 目录数: 1906
- 已生成 README 的完成目录数: 151
- 本地数据总量: 901866154665 bytes (839.93 GiB)
- 下载管理进程数: 0
- aria2 活动下载数: 0
- 最近速度: 0.00 MiB/s

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
- 没有 README 的目录多为下载中或注释缺失失败后留下的未完成目录，本轮下载结束后再统一清理或补充失败说明。
- 大文件和运行日志不提交到 GitHub；GitHub 只记录脚本、清单和进度文档。
