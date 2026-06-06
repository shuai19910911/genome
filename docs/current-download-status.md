# 当前基因组下载进展

- 更新时间: 2026-06-06 13:59:00
- 完成记录数: 88
- 失败记录数: 1410
- 已生成 assembly 目录数: 1504
- 已生成 README 的完成目录数: 90
- 本地数据总量: 820110220517 bytes (763.79 GiB)
- 下载管理进程数: 8
- aria2 活动下载数: 4
- 最近速度: 6.50 MiB/s

## 各 shard 进展

- download_manifest.shard01.tsv: 完成 22
- download_manifest.shard02.tsv: 完成 23
- download_manifest.shard03.tsv: 完成 19
- download_manifest.shard04.tsv: 完成 24
- failed_downloads.shard01.tsv: 失败 377
- failed_downloads.shard02.tsv: 失败 336
- failed_downloads.shard03.tsv: 失败 342
- failed_downloads.shard04.tsv: 失败 355

## 当前活动下载

- `1951 aria2c --continue=true --max-tries=2 --retry-wait 20 --timeout=120 --connect-timeout=60 --max-connection-per-server=1 --split=1 --min-split-size=8M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir Vitis_vinifera_GCA_044590715.1/genome --out GCA_044590715.1_V059.hap2_v1.0_genomic.fna.gz.part https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/044/590/715/GCA_044590715.1_V059.hap2_v1.0/GCA_044590715.1_V059.hap2_v1.0_genomic.fna.gz`
- `2140 aria2c --continue=true --max-tries=2 --retry-wait 20 --timeout=120 --connect-timeout=60 --max-connection-per-server=1 --split=1 --min-split-size=8M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir Malus_domestica_GCA_052939015.1/genome --out GCA_052939015.1_Prima_h1_genomic.fna.gz.part https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/052/939/015/GCA_052939015.1_Prima_h1/GCA_052939015.1_Prima_h1_genomic.fna.gz`
- `83143 aria2c --continue=true --max-tries=2 --retry-wait 20 --timeout=120 --connect-timeout=60 --max-connection-per-server=1 --split=1 --min-split-size=8M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir Saccharum_spontaneum_GCA_057374775.1/genome --out GCA_057374775.1_Ss10_asmbly_v1_genomic.fna.gz.part https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/057/374/775/GCA_057374775.1_Ss10_asmbly_v1/GCA_057374775.1_Ss10_asmbly_v1_genomic.fna.gz`
- `104541 aria2c --continue=true --max-tries=2 --retry-wait 20 --timeout=120 --connect-timeout=60 --max-connection-per-server=1 --split=1 --min-split-size=8M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir Saccharum_spontaneum_GCA_057375035.1/genome --out GCA_057375035.1_Ss03_asmbly_v1_genomic.fna.gz.part https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/057/375/035/GCA_057375035.1_Ss03_asmbly_v1/GCA_057375035.1_Ss03_asmbly_v1_genomic.fna.gz`

## 说明

- 失败记录主要来自 NCBI GenBank (`GCA`) 条目缺少 GFF/GTF 注释文件，脚本会快速跳过并记录失败。
- 没有 README 的目录多为下载中或注释缺失失败后留下的未完成目录，本轮下载结束后再统一清理或补充失败说明。
- 大文件和运行日志不提交到 GitHub；GitHub 只记录脚本、清单和进度文档。
