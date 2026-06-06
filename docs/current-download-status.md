# 当前基因组下载进展

- 更新时间: 2026-06-06 15:20:29
- 完成记录数: 110
- 失败记录数: 1568
- 已生成 assembly 目录数: 1684
- 已生成 README 的完成目录数: 112
- 本地数据总量: 851938464772 bytes (793.43 GiB)
- 下载管理进程数: 8
- aria2 活动下载数: 4
- 最近速度: 8.46 MiB/s

## 各 shard 进展

- download_manifest.shard01.tsv: 完成 29
- download_manifest.shard02.tsv: 完成 23
- download_manifest.shard03.tsv: 完成 24
- download_manifest.shard04.tsv: 完成 34
- failed_downloads.shard01.tsv: 失败 433
- failed_downloads.shard02.tsv: 失败 360
- failed_downloads.shard03.tsv: 失败 374
- failed_downloads.shard04.tsv: 失败 401

## 当前活动下载

- `12390 aria2c --continue=true --max-tries=2 --retry-wait 20 --timeout=120 --connect-timeout=60 --max-connection-per-server=1 --split=1 --min-split-size=8M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir Citrullus_lanatus_GCA_054825255.1/genome --out GCA_054825255.1_ASM5482525v1_genomic.fna.gz.part https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/054/825/255/GCA_054825255.1_ASM5482525v1/GCA_054825255.1_ASM5482525v1_genomic.fna.gz`
- `12918 aria2c --continue=true --max-tries=2 --retry-wait 20 --timeout=120 --connect-timeout=60 --max-connection-per-server=1 --split=1 --min-split-size=8M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir Phaseolus_vulgaris_GCA_029448765.1/genome --out GCA_029448765.1_ASM2944876v1_genomic.fna.gz.part https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/029/448/765/GCA_029448765.1_ASM2944876v1/GCA_029448765.1_ASM2944876v1_genomic.fna.gz`
- `13074 aria2c --continue=true --max-tries=2 --retry-wait 20 --timeout=120 --connect-timeout=60 --max-connection-per-server=1 --split=1 --min-split-size=8M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir Malus_domestica_GCA_052938975.1/genome --out GCA_052938975.1_Rouget_h2_genomic.fna.gz.part https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/052/938/975/GCA_052938975.1_Rouget_h2/GCA_052938975.1_Rouget_h2_genomic.fna.gz`
- `13180 aria2c --continue=true --max-tries=2 --retry-wait 20 --timeout=120 --connect-timeout=60 --max-connection-per-server=1 --split=1 --min-split-size=8M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir Vitis_vinifera_GCA_940446525.1/genome --out GCA_940446525.1_Gf.99-03_haplotype_Gf9918_genomic.fna.gz.part https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/940/446/525/GCA_940446525.1_Gf.99-03_haplotype_Gf9918/GCA_940446525.1_Gf.99-03_haplotype_Gf9918_genomic.fna.gz`

## 说明

- 失败记录主要来自 NCBI GenBank (`GCA`) 条目缺少 GFF/GTF 注释文件，脚本会快速跳过并记录失败。
- 没有 README 的目录多为下载中或注释缺失失败后留下的未完成目录，本轮下载结束后再统一清理或补充失败说明。
- 大文件和运行日志不提交到 GitHub；GitHub 只记录脚本、清单和进度文档。
