# 当前基因组下载进展

- 更新时间: 2026-06-06 18:03:42
- 完成记录数: 142
- 失败记录数: 1728
- 已生成 assembly 目录数: 1875
- 已生成 README 的完成目录数: 144
- 本地数据总量: 889686452146 bytes (828.59 GiB)
- 下载管理进程数: 6
- aria2 活动下载数: 3
- 最近速度: 2.37 MiB/s

## 各 shard 进展

- download_manifest.shard01.tsv: 完成 35
- download_manifest.shard02.tsv: 完成 34
- download_manifest.shard03.tsv: 完成 34
- download_manifest.shard04.tsv: 完成 39
- failed_downloads.shard01.tsv: 失败 441
- failed_downloads.shard02.tsv: 失败 417
- failed_downloads.shard03.tsv: 失败 436
- failed_downloads.shard04.tsv: 失败 434

## 当前活动下载

- `43016 aria2c --continue=true --max-tries=2 --retry-wait 20 --timeout=120 --connect-timeout=60 --max-connection-per-server=1 --split=1 --min-split-size=8M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir Arachis_hypogaea_GCA_028451205.1/genome --out GCA_028451205.1_arahy.BaileyII.gnm1.genome_main_genomic.fna.gz.part https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/028/451/205/GCA_028451205.1_arahy.BaileyII.gnm1.genome_main/GCA_028451205.1_arahy.BaileyII.gnm1.genome_main_genomic.fna.gz`
- `51889 aria2c --continue=true --max-tries=2 --retry-wait 20 --timeout=120 --connect-timeout=60 --max-connection-per-server=1 --split=1 --min-split-size=8M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir Lactuca_sativa_GCA_039583335.1/genome --out GCA_039583335.1_cutv01_genomic.fna.gz.part https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/039/583/335/GCA_039583335.1_cutv01/GCA_039583335.1_cutv01_genomic.fna.gz`
- `66054 aria2c --continue=true --max-tries=2 --retry-wait 20 --timeout=120 --connect-timeout=60 --max-connection-per-server=1 --split=1 --min-split-size=8M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir Citrullus_lanatus_GCA_054829975.1/genome --out GCA_054829975.1_ASM5482997v1_genomic.fna.gz.part https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/054/829/975/GCA_054829975.1_ASM5482997v1/GCA_054829975.1_ASM5482997v1_genomic.fna.gz`

## 说明

- 失败记录主要来自 NCBI GenBank (`GCA`) 条目缺少 GFF/GTF 注释文件，脚本会快速跳过并记录失败。
- 没有 README 的目录多为下载中或注释缺失失败后留下的未完成目录，本轮下载结束后再统一清理或补充失败说明。
- 大文件和运行日志不提交到 GitHub；GitHub 只记录脚本、清单和进度文档。
