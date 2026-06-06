# 当前基因组下载进展

- 更新时间: 2026-06-06 17:43:18
- 完成记录数: 139
- 失败记录数: 1703
- 已生成 assembly 目录数: 1847
- 已生成 README 的完成目录数: 141
- 本地数据总量: 882978564233 bytes (822.34 GiB)
- 下载管理进程数: 6
- aria2 活动下载数: 3
- 最近速度: 3.83 MiB/s

## 各 shard 进展

- download_manifest.shard01.tsv: 完成 35
- download_manifest.shard02.tsv: 完成 33
- download_manifest.shard03.tsv: 完成 33
- download_manifest.shard04.tsv: 完成 38
- failed_downloads.shard01.tsv: 失败 441
- failed_downloads.shard02.tsv: 失败 393
- failed_downloads.shard03.tsv: 失败 435
- failed_downloads.shard04.tsv: 失败 434

## 当前活动下载

- `23284 aria2c --continue=true --max-tries=2 --retry-wait 20 --timeout=120 --connect-timeout=60 --max-connection-per-server=1 --split=1 --min-split-size=8M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir Helianthus_annuus_GCA_026652165.1/genome --out GCA_026652165.1_HanPI659440r1.0-20210824_genomic.fna.gz.part https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/026/652/165/GCA_026652165.1_HanPI659440r1.0-20210824/GCA_026652165.1_HanPI659440r1.0-20210824_genomic.fna.gz`
- `27332 aria2c --continue=true --max-tries=2 --retry-wait 20 --timeout=120 --connect-timeout=60 --max-connection-per-server=1 --split=1 --min-split-size=8M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir Arachis_hypogaea_GCA_039853315.1/genome --out GCA_039853315.1_S245_genomic.fna.gz.part https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/039/853/315/GCA_039853315.1_S245/GCA_039853315.1_S245_genomic.fna.gz`
- `27497 aria2c --continue=true --max-tries=2 --retry-wait 20 --timeout=120 --connect-timeout=60 --max-connection-per-server=1 --split=1 --min-split-size=8M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir Cucumis_melo_GCA_026262305.1/genome --out GCA_026262305.1_BDR_pseudomol_v2.0_genomic.fna.gz.part https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/026/262/305/GCA_026262305.1_BDR_pseudomol_v2.0/GCA_026262305.1_BDR_pseudomol_v2.0_genomic.fna.gz`

## 说明

- 失败记录主要来自 NCBI GenBank (`GCA`) 条目缺少 GFF/GTF 注释文件，脚本会快速跳过并记录失败。
- 没有 README 的目录多为下载中或注释缺失失败后留下的未完成目录，本轮下载结束后再统一清理或补充失败说明。
- 大文件和运行日志不提交到 GitHub；GitHub 只记录脚本、清单和进度文档。
