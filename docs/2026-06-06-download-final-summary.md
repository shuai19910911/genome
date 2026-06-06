# NCBI 作物基因组下载阶段总结

- 总结时间: 2026-06-06 22:27:16
- 原始计划条目数: 1906
- 已完成并写入 shard manifest 的条目数: 149
- 已失败并写入 failed 表的条目数: 1755
- 已生成 assembly 目录数: 1906
- 已生成 README 的完成目录数: 151
- 本地文件总量: 901866154665 bytes (839.93 GiB)

## 完成来源统计

- NCBI GenBank: 123
- NCBI RefSeq: 26

## 失败原因统计

- 注释文件不存在: 1755

## 失败来源统计

- NCBI GenBank: 1755

## 失败物种 Top 20

- Beta vulgaris: 326
- Hordeum vulgare: 199
- Oryza sativa: 190
- Zea mays: 185
- Citrullus lanatus: 118
- Brassica napus: 107
- Solanum tuberosum: 93
- Vitis vinifera: 87
- Triticum aestivum: 60
- Cucumis sativus: 44
- Malus domestica: 40
- Cucumis melo: 40
- Solanum lycopersicum: 38
- Glycine max: 33
- Brassica oleracea: 28
- Sorghum bicolor: 22
- Manihot esculenta: 22
- Gossypium hirsutum: 19
- Brassica rapa: 18
- Saccharum spontaneum: 18

## 结论

- 这一轮 NCBI 清单已经全部处理完成；没有下载管理进程和 aria2 活动下载。
- 成功条目主要是同时能取得 genome 与 GFF/GTF 注释的 assembly。
- 大量失败来自 NCBI GenBank (`GCA`) 条目缺少对应 GFF/GTF 注释文件；脚本已快速跳过并记录失败。
- 失败后留下的目录多包含 metadata、部分 genome 或 `.part` 文件，当前未删除，便于后续补注释、复核或清理。

## 建议下一步

1. 先按 `failed_downloads.merged.tsv` 区分“genome 已下载但注释缺失”和“genome 本身失败”。
2. 对注释缺失的 GCA 条目，优先决定是否保留 genome-only 数据；如果不保留，再统一清理未完成目录。
3. 针对重要作物和 cultivar，尝试用 NCBI Datasets、Ensembl Plants 或作物专项数据库补注释。
4. 合并 `download_manifest.merged.tsv` 后，可生成最终索引表和每物种完成/失败报告。
