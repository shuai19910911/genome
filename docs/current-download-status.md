# 当前基因组下载进展

- 更新时间: 2026-06-06 15:40:51
- 完成记录数: 118
- 失败记录数: 1587
- 已生成 assembly 目录数: 1711
- 已生成 README 的完成目录数: 120
- 本地数据总量: 859330652683 bytes (800.31 GiB)
- 下载管理进程数: 8
- aria2 活动下载数: 4
- 最近速度: 5.74 MiB/s

## 各 shard 进展

- download_manifest.shard01.tsv: 完成 32
- download_manifest.shard02.tsv: 完成 23
- download_manifest.shard03.tsv: 完成 29
- download_manifest.shard04.tsv: 完成 34
- failed_downloads.shard01.tsv: 失败 439
- failed_downloads.shard02.tsv: 失败 364
- failed_downloads.shard03.tsv: 失败 374
- failed_downloads.shard04.tsv: 失败 410

## 当前活动下载

- `35574 aria2c --continue=true --max-tries=2 --retry-wait 20 --timeout=120 --connect-timeout=60 --max-connection-per-server=1 --split=1 --min-split-size=8M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir Malus_domestica_GCA_002114115.1/genome --out GCA_002114115.1_ASM211411v1_genomic.fna.gz.part https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/002/114/115/GCA_002114115.1_ASM211411v1/GCA_002114115.1_ASM211411v1_genomic.fna.gz`
- `47200 aria2c --continue=true --max-tries=2 --retry-wait 20 --timeout=120 --connect-timeout=60 --max-connection-per-server=1 --split=1 --min-split-size=8M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir Helianthus_annuus_GCA_026538245.1/genome --out GCA_026538245.1_HanHA89r1.0-20210811_genomic.fna.gz.part https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/026/538/245/GCA_026538245.1_HanHA89r1.0-20210811/GCA_026538245.1_HanHA89r1.0-20210811_genomic.fna.gz`
- `49292 aria2c --continue=true --max-tries=2 --retry-wait 20 --timeout=120 --connect-timeout=60 --max-connection-per-server=1 --split=1 --min-split-size=8M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir Citrullus_lanatus_GCA_054826335.1/genome --out GCA_054826335.1_ASM5482633v1_genomic.fna.gz.part https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/054/826/335/GCA_054826335.1_ASM5482633v1/GCA_054826335.1_ASM5482633v1_genomic.fna.gz`
- `50907 aria2c --continue=true --max-tries=2 --retry-wait 20 --timeout=120 --connect-timeout=60 --max-connection-per-server=1 --split=1 --min-split-size=8M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir Malus_domestica_GCA_052939365.1/genome --out GCA_052939365.1_Giambun_h2_genomic.fna.gz.part https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/052/939/365/GCA_052939365.1_Giambun_h2/GCA_052939365.1_Giambun_h2_genomic.fna.gz`

## 说明

- 失败记录主要来自 NCBI GenBank (`GCA`) 条目缺少 GFF/GTF 注释文件，脚本会快速跳过并记录失败。
- 没有 README 的目录多为下载中或注释缺失失败后留下的未完成目录，本轮下载结束后再统一清理或补充失败说明。
- 大文件和运行日志不提交到 GitHub；GitHub 只记录脚本、清单和进度文档。
