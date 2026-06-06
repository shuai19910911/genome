# 当前基因组下载进展

- 更新时间: 2026-06-06 15:00:07
- 完成记录数: 106
- 失败记录数: 1533
- 已生成 assembly 目录数: 1645
- 已生成 README 的完成目录数: 108
- 本地数据总量: 846566464946 bytes (788.43 GiB)
- 下载管理进程数: 8
- aria2 活动下载数: 4
- 最近速度: 4.76 MiB/s

## 各 shard 进展

- download_manifest.shard01.tsv: 完成 29
- download_manifest.shard02.tsv: 完成 23
- download_manifest.shard03.tsv: 完成 21
- download_manifest.shard04.tsv: 完成 33
- failed_downloads.shard01.tsv: 失败 423
- failed_downloads.shard02.tsv: 失败 349
- failed_downloads.shard03.tsv: 失败 374
- failed_downloads.shard04.tsv: 失败 387

## 当前活动下载

- `89336 aria2c --continue=true --max-tries=2 --retry-wait 20 --timeout=120 --connect-timeout=60 --max-connection-per-server=1 --split=1 --min-split-size=8M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir Vitis_vinifera_GCA_044589015.1/genome --out GCA_044589015.1_V093.hap2_v1.0_genomic.fna.gz.part https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/044/589/015/GCA_044589015.1_V093.hap2_v1.0/GCA_044589015.1_V093.hap2_v1.0_genomic.fna.gz`
- `91118 aria2c --continue=true --max-tries=2 --retry-wait 20 --timeout=120 --connect-timeout=60 --max-connection-per-server=1 --split=1 --min-split-size=8M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir Citrullus_lanatus_GCA_054830095.1/genome --out GCA_054830095.1_ASM5483009v1_genomic.fna.gz.part https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/054/830/095/GCA_054830095.1_ASM5483009v1/GCA_054830095.1_ASM5483009v1_genomic.fna.gz`
- `91523 aria2c --continue=true --max-tries=2 --retry-wait 20 --timeout=120 --connect-timeout=60 --max-connection-per-server=1 --split=1 --min-split-size=8M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir Malus_domestica_GCA_052938535.1/genome --out GCA_052938535.1_TropicalBeauty_h1_genomic.fna.gz.part https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/052/938/535/GCA_052938535.1_TropicalBeauty_h1/GCA_052938535.1_TropicalBeauty_h1_genomic.fna.gz`
- `91756 aria2c --continue=true --max-tries=2 --retry-wait 20 --timeout=120 --connect-timeout=60 --max-connection-per-server=1 --split=1 --min-split-size=8M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir Cucumis_melo_GCA_020920055.1/genome --out GCA_020920055.1_TAD_pseudomol_v1.0_genomic.fna.gz.part https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/020/920/055/GCA_020920055.1_TAD_pseudomol_v1.0/GCA_020920055.1_TAD_pseudomol_v1.0_genomic.fna.gz`

## 说明

- 失败记录主要来自 NCBI GenBank (`GCA`) 条目缺少 GFF/GTF 注释文件，脚本会快速跳过并记录失败。
- 没有 README 的目录多为下载中或注释缺失失败后留下的未完成目录，本轮下载结束后再统一清理或补充失败说明。
- 大文件和运行日志不提交到 GitHub；GitHub 只记录脚本、清单和进度文档。
