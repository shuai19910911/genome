# 当前基因组下载进展

- 更新时间: 2026-06-06 17:22:57
- 完成记录数: 136
- 失败记录数: 1672
- 已生成 assembly 目录数: 1814
- 已生成 README 的完成目录数: 138
- 本地数据总量: 877516232657 bytes (817.25 GiB)
- 下载管理进程数: 8
- aria2 活动下载数: 4
- 最近速度: 9.04 MiB/s

## 各 shard 进展

- download_manifest.shard01.tsv: 完成 34
- download_manifest.shard02.tsv: 完成 32
- download_manifest.shard03.tsv: 完成 33
- download_manifest.shard04.tsv: 完成 37
- failed_downloads.shard01.tsv: 失败 440
- failed_downloads.shard02.tsv: 失败 372
- failed_downloads.shard03.tsv: 失败 428
- failed_downloads.shard04.tsv: 失败 432

## 当前活动下载

- `85445 aria2c --continue=true --max-tries=2 --retry-wait 20 --timeout=120 --connect-timeout=60 --max-connection-per-server=1 --split=1 --min-split-size=8M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir Lactuca_sativa_GCA_900198505.1/genome --out GCA_900198505.1_Lsativa_genomic.fna.gz.part https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/900/198/505/GCA_900198505.1_Lsativa/GCA_900198505.1_Lsativa_genomic.fna.gz`
- `100795 aria2c --continue=true --max-tries=2 --retry-wait 20 --timeout=120 --connect-timeout=60 --max-connection-per-server=1 --split=1 --min-split-size=8M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir Arachis_hypogaea_GCA_054824525.1/genome --out GCA_054824525.1_ASM5482452v1_genomic.fna.gz.part https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/054/824/525/GCA_054824525.1_ASM5482452v1/GCA_054824525.1_ASM5482452v1_genomic.fna.gz`
- `104906 aria2c --continue=true --max-tries=2 --retry-wait 20 --timeout=120 --connect-timeout=60 --max-connection-per-server=1 --split=1 --min-split-size=8M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir Phaseolus_vulgaris_GCA_016509735.1/genome --out GCA_016509735.1_ASM1650973v1_genomic.fna.gz.part https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/016/509/735/GCA_016509735.1_ASM1650973v1/GCA_016509735.1_ASM1650973v1_genomic.fna.gz`
- `105060 aria2c --continue=true --max-tries=2 --retry-wait 20 --timeout=120 --connect-timeout=60 --max-connection-per-server=1 --split=1 --min-split-size=8M --file-allocation=none --allow-overwrite=true --auto-file-renaming=false --dir Malus_domestica_GCA_052939425.1/genome --out GCA_052939425.1_Enterprise_h1_genomic.fna.gz.part https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/052/939/425/GCA_052939425.1_Enterprise_h1/GCA_052939425.1_Enterprise_h1_genomic.fna.gz`

## 说明

- 失败记录主要来自 NCBI GenBank (`GCA`) 条目缺少 GFF/GTF 注释文件，脚本会快速跳过并记录失败。
- 没有 README 的目录多为下载中或注释缺失失败后留下的未完成目录，本轮下载结束后再统一清理或补充失败说明。
- 大文件和运行日志不提交到 GitHub；GitHub 只记录脚本、清单和进度文档。
