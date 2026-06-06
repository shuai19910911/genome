# 当前基因组下载进展

- 更新时间: 2026-06-06 12:37:50
- 完成记录数: 81
- 失败记录数: 1289
- 已生成 assembly 目录数: 1376
- 已生成 README 的完成目录数: 83
- 本地数据总量: 776176959479 bytes (722.87 GiB)
- 下载管理进程数: 8
- aria2 活动下载数: 4
- 最近速度: 8.82 MiB/s

## 各 shard 进展

- download_manifest.shard01.tsv: 完成 17
- download_manifest.shard02.tsv: 完成 23
- download_manifest.shard03.tsv: 完成 19
- download_manifest.shard04.tsv: 完成 22
- failed_downloads.shard01.tsv: 失败 344
- failed_downloads.shard02.tsv: 失败 294
- failed_downloads.shard03.tsv: 失败 323
- failed_downloads.shard04.tsv: 失败 328

## 当前活动下载

- `6050 aria2c --continue=true --max-tries=2 --retry-wait 20 --timeout=120 --connect-timeout=60 --max-connection-per-server=1 --split=1 --min-split-size=8M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir Saccharum_spontaneum_GCA_057374995.1/genome --out GCA_057374995.1_Ss05_asmbly_v1_genomic.fna.gz.part https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/057/374/995/GCA_057374995.1_Ss05_asmbly_v1/GCA_057374995.1_Ss05_asmbly_v1_genomic.fna.gz`
- `8170 aria2c --continue=true --max-tries=2 --retry-wait 20 --timeout=120 --connect-timeout=60 --max-connection-per-server=1 --split=1 --min-split-size=8M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir Beta_vulgaris_GCA_037017235.1/genome --out GCA_037017235.1_ASM3701723v1_genomic.fna.gz.part https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/037/017/235/GCA_037017235.1_ASM3701723v1/GCA_037017235.1_ASM3701723v1_genomic.fna.gz`
- `8858 aria2c --continue=true --max-tries=2 --retry-wait 20 --timeout=120 --connect-timeout=60 --max-connection-per-server=1 --split=1 --min-split-size=8M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir Beta_vulgaris_GCA_040762275.1/genome --out GCA_040762275.1_ASM4076227v1_genomic.fna.gz.part https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/040/762/275/GCA_040762275.1_ASM4076227v1/GCA_040762275.1_ASM4076227v1_genomic.fna.gz`
- `8993 aria2c --continue=true --max-tries=2 --retry-wait 20 --timeout=120 --connect-timeout=60 --max-connection-per-server=1 --split=1 --min-split-size=8M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir Beta_vulgaris_GCA_040761275.1/genome --out GCA_040761275.1_ASM4076127v1_genomic.fna.gz.part https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/040/761/275/GCA_040761275.1_ASM4076127v1/GCA_040761275.1_ASM4076127v1_genomic.fna.gz`

## 说明

- 失败记录主要来自 NCBI GenBank (`GCA`) 条目缺少 GFF/GTF 注释文件，脚本会快速跳过并记录失败。
- 没有 README 的目录多为下载中或注释缺失失败后留下的未完成目录，本轮下载结束后再统一清理或补充失败说明。
- 大文件和运行日志不提交到 GitHub；GitHub 只记录脚本、清单和进度文档。
