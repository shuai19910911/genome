# 当前基因组下载进展

- 更新时间: 2026-06-06 16:01:27
- 完成记录数: 122
- 失败记录数: 1624
- 已生成 assembly 目录数: 1752
- 已生成 README 的完成目录数: 124
- 本地数据总量: 865050562040 bytes (805.64 GiB)
- 下载管理进程数: 8
- aria2 活动下载数: 4
- 最近速度: 3.55 MiB/s

## 各 shard 进展

- download_manifest.shard01.tsv: 完成 33
- download_manifest.shard02.tsv: 完成 23
- download_manifest.shard03.tsv: 完成 32
- download_manifest.shard04.tsv: 完成 34
- failed_downloads.shard01.tsv: 失败 439
- failed_downloads.shard02.tsv: 失败 371
- failed_downloads.shard03.tsv: 失败 390
- failed_downloads.shard04.tsv: 失败 424

## 当前活动下载

- `57150 aria2c --continue=true --max-tries=2 --retry-wait 20 --timeout=120 --connect-timeout=60 --max-connection-per-server=1 --split=1 --min-split-size=8M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir Helianthus_annuus_GCA_026651695.1/genome --out GCA_026651695.1_HanIRr1.0-20201123_genomic.fna.gz.part https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/026/651/695/GCA_026651695.1_HanIRr1.0-20201123/GCA_026651695.1_HanIRr1.0-20201123_genomic.fna.gz`
- `73296 aria2c --continue=true --max-tries=2 --retry-wait 20 --timeout=120 --connect-timeout=60 --max-connection-per-server=1 --split=1 --min-split-size=8M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir Malus_domestica_GCA_047142335.1/genome --out GCA_047142335.1_ASM4714233v1_genomic.fna.gz.part https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/047/142/335/GCA_047142335.1_ASM4714233v1/GCA_047142335.1_ASM4714233v1_genomic.fna.gz`
- `75935 aria2c --continue=true --max-tries=2 --retry-wait 20 --timeout=120 --connect-timeout=60 --max-connection-per-server=1 --split=1 --min-split-size=8M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir Citrullus_lanatus_GCA_054831825.1/genome --out GCA_054831825.1_ASM5483182v1_genomic.fna.gz.part https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/054/831/825/GCA_054831825.1_ASM5483182v1/GCA_054831825.1_ASM5483182v1_genomic.fna.gz`
- `85807 aria2c --continue=true --max-tries=2 --retry-wait 20 --timeout=120 --connect-timeout=60 --max-connection-per-server=1 --split=1 --min-split-size=8M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir Cucumis_melo_GCA_026261915.1/genome --out GCA_026261915.1_SAS_pseudomol_v2.0_genomic.fna.gz.part https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/026/261/915/GCA_026261915.1_SAS_pseudomol_v2.0/GCA_026261915.1_SAS_pseudomol_v2.0_genomic.fna.gz`

## 说明

- 失败记录主要来自 NCBI GenBank (`GCA`) 条目缺少 GFF/GTF 注释文件，脚本会快速跳过并记录失败。
- 没有 README 的目录多为下载中或注释缺失失败后留下的未完成目录，本轮下载结束后再统一清理或补充失败说明。
- 大文件和运行日志不提交到 GitHub；GitHub 只记录脚本、清单和进度文档。
