# 当前基因组下载进展

- 更新时间: 2026-06-06 13:18:25
- 完成记录数: 83
- 失败记录数: 1358
- 已生成 assembly 目录数: 1447
- 已生成 README 的完成目录数: 85
- 本地数据总量: 797063053823 bytes (742.32 GiB)
- 下载管理进程数: 8
- aria2 活动下载数: 4
- 最近速度: 7.38 MiB/s

## 各 shard 进展

- download_manifest.shard01.tsv: 完成 19
- download_manifest.shard02.tsv: 完成 23
- download_manifest.shard03.tsv: 完成 19
- download_manifest.shard04.tsv: 完成 22
- failed_downloads.shard01.tsv: 失败 354
- failed_downloads.shard02.tsv: 失败 327
- failed_downloads.shard03.tsv: 失败 339
- failed_downloads.shard04.tsv: 失败 338

## 当前活动下载

- `29899 aria2c --continue=true --max-tries=2 --retry-wait 20 --timeout=120 --connect-timeout=60 --max-connection-per-server=1 --split=1 --min-split-size=8M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir Saccharum_spontaneum_GCA_057374655.1/genome --out GCA_057374655.1_Ss01_asmbly_v1_genomic.fna.gz.part https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/057/374/655/GCA_057374655.1_Ss01_asmbly_v1/GCA_057374655.1_Ss01_asmbly_v1_genomic.fna.gz`
- `49437 aria2c --continue=true --max-tries=2 --retry-wait 20 --timeout=120 --connect-timeout=60 --max-connection-per-server=1 --split=1 --min-split-size=8M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir Saccharum_spontaneum_GCA_057374975.1/genome --out GCA_057374975.1_Ss04_asmbly_v1_genomic.fna.gz.part https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/057/374/975/GCA_057374975.1_Ss04_asmbly_v1/GCA_057374975.1_Ss04_asmbly_v1_genomic.fna.gz`
- `56792 aria2c --continue=true --max-tries=2 --retry-wait 20 --timeout=120 --connect-timeout=60 --max-connection-per-server=1 --split=1 --min-split-size=8M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir Beta_vulgaris_GCA_040762215.1/genome --out GCA_040762215.1_ASM4076221v1_genomic.fna.gz.part https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/040/762/215/GCA_040762215.1_ASM4076221v1/GCA_040762215.1_ASM4076221v1_genomic.fna.gz`
- `57992 aria2c --continue=true --max-tries=2 --retry-wait 20 --timeout=120 --connect-timeout=60 --max-connection-per-server=1 --split=1 --min-split-size=8M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir Vitis_vinifera_GCA_044589605.1/genome --out GCA_044589605.1_V092.hap2_v1.0_genomic.fna.gz.part https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/044/589/605/GCA_044589605.1_V092.hap2_v1.0/GCA_044589605.1_V092.hap2_v1.0_genomic.fna.gz`

## 说明

- 失败记录主要来自 NCBI GenBank (`GCA`) 条目缺少 GFF/GTF 注释文件，脚本会快速跳过并记录失败。
- 没有 README 的目录多为下载中或注释缺失失败后留下的未完成目录，本轮下载结束后再统一清理或补充失败说明。
- 大文件和运行日志不提交到 GitHub；GitHub 只记录脚本、清单和进度文档。
