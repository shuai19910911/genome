# 当前基因组下载进展

- 更新时间: 2026-06-06 14:39:41
- 完成记录数: 101
- 失败记录数: 1479
- 已生成 assembly 目录数: 1586
- 已生成 README 的完成目录数: 103
- 本地数据总量: 837933223358 bytes (780.39 GiB)
- 下载管理进程数: 8
- aria2 活动下载数: 4
- 最近速度: 7.58 MiB/s

## 各 shard 进展

- download_manifest.shard01.tsv: 完成 29
- download_manifest.shard02.tsv: 完成 23
- download_manifest.shard03.tsv: 完成 20
- download_manifest.shard04.tsv: 完成 29
- failed_downloads.shard01.tsv: 失败 408
- failed_downloads.shard02.tsv: 失败 339
- failed_downloads.shard03.tsv: 失败 361
- failed_downloads.shard04.tsv: 失败 371

## 当前活动下载

- `48585 aria2c --continue=true --max-tries=2 --retry-wait 20 --timeout=120 --connect-timeout=60 --max-connection-per-server=1 --split=1 --min-split-size=8M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir Saccharum_spontaneum_GCA_900500655.1/genome --out GCA_900500655.1_Sugarcane_genome_genomic.fna.gz.part https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/900/500/655/GCA_900500655.1_Sugarcane_genome/GCA_900500655.1_Sugarcane_genome_genomic.fna.gz`
- `55197 aria2c --continue=true --max-tries=2 --retry-wait 20 --timeout=120 --connect-timeout=60 --max-connection-per-server=1 --split=1 --min-split-size=8M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir Citrullus_lanatus_GCA_054825445.1/genome --out GCA_054825445.1_ASM5482544v1_genomic.fna.gz.part https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/054/825/445/GCA_054825445.1_ASM5482544v1/GCA_054825445.1_ASM5482544v1_genomic.fna.gz`
- `55376 aria2c --continue=true --max-tries=2 --retry-wait 20 --timeout=120 --connect-timeout=60 --max-connection-per-server=1 --split=1 --min-split-size=8M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir Vitis_vinifera_GCA_051166855.1/genome --out GCA_051166855.1_TST2T_hap2_genomic.fna.gz.part https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/051/166/855/GCA_051166855.1_TST2T_hap2/GCA_051166855.1_TST2T_hap2_genomic.fna.gz`
- `56515 aria2c --continue=true --max-tries=2 --retry-wait 20 --timeout=120 --connect-timeout=60 --max-connection-per-server=1 --split=1 --min-split-size=8M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir Malus_domestica_GCA_052939155.1/annotation --out GCA_052939155.1_Braeburn_h1_genomic.gff.gz.part https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/052/939/155/GCA_052939155.1_Braeburn_h1/GCA_052939155.1_Braeburn_h1_genomic.gff.gz`

## 说明

- 失败记录主要来自 NCBI GenBank (`GCA`) 条目缺少 GFF/GTF 注释文件，脚本会快速跳过并记录失败。
- 没有 README 的目录多为下载中或注释缺失失败后留下的未完成目录，本轮下载结束后再统一清理或补充失败说明。
- 大文件和运行日志不提交到 GitHub；GitHub 只记录脚本、清单和进度文档。
