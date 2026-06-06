# 当前基因组下载进展

- 更新时间: 2026-06-06 13:38:42
- 完成记录数: 83
- 失败记录数: 1382
- 已生成 assembly 目录数: 1471
- 已生成 README 的完成目录数: 85
- 本地数据总量: 807899780322 bytes (752.42 GiB)
- 下载管理进程数: 8
- aria2 活动下载数: 4
- 最近速度: 10.08 MiB/s

## 各 shard 进展

- download_manifest.shard01.tsv: 完成 19
- download_manifest.shard02.tsv: 完成 23
- download_manifest.shard03.tsv: 完成 19
- download_manifest.shard04.tsv: 完成 22
- failed_downloads.shard01.tsv: 失败 366
- failed_downloads.shard02.tsv: 失败 336
- failed_downloads.shard03.tsv: 失败 341
- failed_downloads.shard04.tsv: 失败 339

## 当前活动下载

- `77391 aria2c --continue=true --max-tries=2 --retry-wait 20 --timeout=120 --connect-timeout=60 --max-connection-per-server=1 --split=1 --min-split-size=8M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir Saccharum_spontaneum_GCA_057375055.1/genome --out GCA_057375055.1_Ss02_asmbly_v1_genomic.fna.gz.part https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/057/375/055/GCA_057375055.1_Ss02_asmbly_v1/GCA_057375055.1_Ss02_asmbly_v1_genomic.fna.gz`
- `77457 aria2c --continue=true --max-tries=2 --retry-wait 20 --timeout=120 --connect-timeout=60 --max-connection-per-server=1 --split=1 --min-split-size=8M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir Vitis_vinifera_GCA_977016225.1/genome --out GCA_977016225.1_VITVvi_vSauBlan06_v1.0_genomic.fna.gz.part https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/977/016/225/GCA_977016225.1_VITVvi_vSauBlan06_v1.0/GCA_977016225.1_VITVvi_vSauBlan06_v1.0_genomic.fna.gz`
- `83143 aria2c --continue=true --max-tries=2 --retry-wait 20 --timeout=120 --connect-timeout=60 --max-connection-per-server=1 --split=1 --min-split-size=8M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir Saccharum_spontaneum_GCA_057374775.1/genome --out GCA_057374775.1_Ss10_asmbly_v1_genomic.fna.gz.part https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/057/374/775/GCA_057374775.1_Ss10_asmbly_v1/GCA_057374775.1_Ss10_asmbly_v1_genomic.fna.gz`
- `87316 aria2c --continue=true --max-tries=2 --retry-wait 20 --timeout=120 --connect-timeout=60 --max-connection-per-server=1 --split=1 --min-split-size=8M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir Saccharum_spontaneum_GCA_057374955.1/genome --out GCA_057374955.1_Ss07_asmbly_v1_genomic.fna.gz.part https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/057/374/955/GCA_057374955.1_Ss07_asmbly_v1/GCA_057374955.1_Ss07_asmbly_v1_genomic.fna.gz`

## 说明

- 失败记录主要来自 NCBI GenBank (`GCA`) 条目缺少 GFF/GTF 注释文件，脚本会快速跳过并记录失败。
- 没有 README 的目录多为下载中或注释缺失失败后留下的未完成目录，本轮下载结束后再统一清理或补充失败说明。
- 大文件和运行日志不提交到 GitHub；GitHub 只记录脚本、清单和进度文档。
