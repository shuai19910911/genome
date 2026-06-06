# 当前基因组下载进展

- 更新时间: 2026-06-06 18:24:07
- 完成记录数: 145
- 失败记录数: 1748
- 已生成 assembly 目录数: 1897
- 已生成 README 的完成目录数: 147
- 本地数据总量: 895336669147 bytes (833.85 GiB)
- 下载管理进程数: 4
- aria2 活动下载数: 2
- 最近速度: 4.26 MiB/s

## 各 shard 进展

- download_manifest.shard01.tsv: 完成 35
- download_manifest.shard02.tsv: 完成 34
- download_manifest.shard03.tsv: 完成 36
- download_manifest.shard04.tsv: 完成 40
- failed_downloads.shard01.tsv: 失败 441
- failed_downloads.shard02.tsv: 失败 433
- failed_downloads.shard03.tsv: 失败 438
- failed_downloads.shard04.tsv: 失败 436

## 当前活动下载

- `99241 aria2c --continue=true --max-tries=2 --retry-wait 20 --timeout=120 --connect-timeout=60 --max-connection-per-server=1 --split=1 --min-split-size=8M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir Lactuca_sativa_GCA_041283435.1/genome --out GCA_041283435.1_ASM4128343v1_genomic.fna.gz.part https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/041/283/435/GCA_041283435.1_ASM4128343v1/GCA_041283435.1_ASM4128343v1_genomic.fna.gz`
- `114327 aria2c --continue=true --max-tries=2 --retry-wait 20 --timeout=120 --connect-timeout=60 --max-connection-per-server=1 --split=1 --min-split-size=8M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir Arachis_hypogaea_GCA_016103905.1/genome --out GCA_016103905.1_Haihua1_v1_genomic.fna.gz.part https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/016/103/905/GCA_016103905.1_Haihua1_v1/GCA_016103905.1_Haihua1_v1_genomic.fna.gz`

## 说明

- 失败记录主要来自 NCBI GenBank (`GCA`) 条目缺少 GFF/GTF 注释文件，脚本会快速跳过并记录失败。
- 没有 README 的目录多为下载中或注释缺失失败后留下的未完成目录，本轮下载结束后再统一清理或补充失败说明。
- 大文件和运行日志不提交到 GitHub；GitHub 只记录脚本、清单和进度文档。
