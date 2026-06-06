# 当前基因组下载进展

- 更新时间: 2026-06-06 19:05:12
- 完成记录数: 149
- 失败记录数: 1753
- 已生成 assembly 目录数: 1905
- 已生成 README 的完成目录数: 151
- 本地数据总量: 901604153676 bytes (839.68 GiB)
- 下载管理进程数: 2
- aria2 活动下载数: 1
- 最近速度: 1.39 MiB/s

## 各 shard 进展

- download_manifest.shard01.tsv: 完成 35
- download_manifest.shard02.tsv: 完成 38
- download_manifest.shard03.tsv: 完成 36
- download_manifest.shard04.tsv: 完成 40
- failed_downloads.shard01.tsv: 失败 441
- failed_downloads.shard02.tsv: 失败 436
- failed_downloads.shard03.tsv: 失败 440
- failed_downloads.shard04.tsv: 失败 436

## 当前活动下载

- `56991 aria2c --continue=true --max-tries=2 --retry-wait 20 --timeout=120 --connect-timeout=60 --max-connection-per-server=1 --split=1 --min-split-size=8M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir Lactuca_sativa_GCA_900243165.1/genome --out GCA_900243165.1_Salat_v21_genomic.fna.gz.part https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/900/243/165/GCA_900243165.1_Salat_v21/GCA_900243165.1_Salat_v21_genomic.fna.gz`

## 说明

- 失败记录主要来自 NCBI GenBank (`GCA`) 条目缺少 GFF/GTF 注释文件，脚本会快速跳过并记录失败。
- 没有 README 的目录多为下载中或注释缺失失败后留下的未完成目录，本轮下载结束后再统一清理或补充失败说明。
- 大文件和运行日志不提交到 GitHub；GitHub 只记录脚本、清单和进度文档。
