# 当前基因组下载进展

- 更新时间: 2026-06-06 14:19:19
- 完成记录数: 95
- 失败记录数: 1448
- 已生成 assembly 目录数: 1549
- 已生成 README 的完成目录数: 97
- 本地数据总量: 830530066477 bytes (773.49 GiB)
- 下载管理进程数: 8
- aria2 活动下载数: 4
- 最近速度: 5.18 MiB/s

## 各 shard 进展

- download_manifest.shard01.tsv: 完成 28
- download_manifest.shard02.tsv: 完成 23
- download_manifest.shard03.tsv: 完成 20
- download_manifest.shard04.tsv: 完成 24
- failed_downloads.shard01.tsv: 失败 388
- failed_downloads.shard02.tsv: 失败 338
- failed_downloads.shard03.tsv: 失败 351
- failed_downloads.shard04.tsv: 失败 371

## 当前活动下载

- `16090 aria2c --continue=true --max-tries=2 --retry-wait 20 --timeout=120 --connect-timeout=60 --max-connection-per-server=1 --split=1 --min-split-size=8M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir Saccharum_spontaneum_GCA_057375015.1/genome --out GCA_057375015.1_Ss01_asmbly_v1_genomic.fna.gz.part https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/057/375/015/GCA_057375015.1_Ss01_asmbly_v1/GCA_057375015.1_Ss01_asmbly_v1_genomic.fna.gz`
- `23048 aria2c --continue=true --max-tries=2 --retry-wait 20 --timeout=120 --connect-timeout=60 --max-connection-per-server=1 --split=1 --min-split-size=8M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir Vitis_vinifera_GCA_041295515.1/genome --out GCA_041295515.1_HMNGT2T_hap2_genomic.fna.gz.part https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/041/295/515/GCA_041295515.1_HMNGT2T_hap2/GCA_041295515.1_HMNGT2T_hap2_genomic.fna.gz`
- `27398 aria2c --continue=true --max-tries=2 --retry-wait 20 --timeout=120 --connect-timeout=60 --max-connection-per-server=1 --split=1 --min-split-size=8M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir Malus_domestica_GCA_052938555.1/genome --out GCA_052938555.1_Priscilla_h1_genomic.fna.gz.part https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/052/938/555/GCA_052938555.1_Priscilla_h1/GCA_052938555.1_Priscilla_h1_genomic.fna.gz`
- `27694 aria2c --continue=true --max-tries=2 --retry-wait 20 --timeout=120 --connect-timeout=60 --max-connection-per-server=1 --split=1 --min-split-size=8M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir Cucumis_sativus_GCA_054392695.1/genome --out GCA_054392695.1_ASM5439269v1_genomic.fna.gz.part https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/054/392/695/GCA_054392695.1_ASM5439269v1/GCA_054392695.1_ASM5439269v1_genomic.fna.gz`

## 说明

- 失败记录主要来自 NCBI GenBank (`GCA`) 条目缺少 GFF/GTF 注释文件，脚本会快速跳过并记录失败。
- 没有 README 的目录多为下载中或注释缺失失败后留下的未完成目录，本轮下载结束后再统一清理或补充失败说明。
- 大文件和运行日志不提交到 GitHub；GitHub 只记录脚本、清单和进度文档。
