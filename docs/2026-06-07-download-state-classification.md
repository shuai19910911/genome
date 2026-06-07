# 作物基因组下载状态分类

- 检查时间: 2026-06-07 13:03:35
- 计划条目: 1906
- 完成清单条目: 149
- 失败清单条目: 1755
- 实际 assembly 目录: 1906
- 完整或基本完整目录: 157
- 未完整目录: 1749
- 未完整但已有 genome 文件的目录: 1749
- 未完整且没有 genome 文件的目录: 0
- 本地目录总大小: 901924711614 bytes (839.98 GiB)

## 分类结果

- 只有基因组：缺少 GFF3/GTF 注释: 1749
- 完整：清单、文件、中文 README 都存在: 149
- 基本完整：文件存在，但清单或 README 需要复核: 8

## 生成的索引

- 完整索引: `docs/completed-genome-index.tsv`
- 未完整索引: `docs/incomplete-genome-index.tsv`

## 怎么理解这些结果

- “完整”表示 genome 文件、GFF3/GTF 注释文件、中文 README 都存在，并且该 assembly 在完成清单中。
- “基本完整”表示 genome 和至少一种注释文件存在，但清单或 README 需要再复核。
- “只有基因组”表示已经留下 `.fna.gz` 等 genome 文件，但没有找到 `.gff.gz`、`.gff3.gz` 或 `.gtf.gz`。
- “空目录或仅元数据”表示目前没有可用 genome/annotation 数据文件，通常是因为注释 URL 不存在后快速跳过。
- 本次没有删除任何目录；这些分类表只是帮助后续决定保留、补注释或清理。

## 完整目录物种 Top 20

- Malus domestica: 40
- Triticum aestivum: 14
- Arachis hypogaea: 9
- Glycine max: 9
- Helianthus annuus: 9
- Oryza sativa: 8
- Hordeum vulgare: 7
- Brassica rapa: 6
- Brassica napus: 5
- Cucumis melo: 5
- Solanum tuberosum: 5
- Sorghum bicolor: 5
- Brassica oleracea: 4
- Musa acuminata: 4
- Zea mays: 4
- Daucus carota: 3
- Gossypium hirsutum: 3
- Vitis vinifera: 3
- Beta vulgaris: 2
- Phaseolus vulgaris: 2

## 未完整目录物种 Top 20

- Beta vulgaris: 326
- Hordeum vulgare: 195
- Oryza sativa: 190
- Zea mays: 185
- Citrullus lanatus: 118
- Brassica napus: 107
- Solanum tuberosum: 93
- Vitis vinifera: 87
- Triticum aestivum: 59
- Cucumis sativus: 44
- Cucumis melo: 40
- Malus domestica: 40
- Solanum lycopersicum: 37
- Glycine max: 33
- Brassica oleracea: 28
- Manihot esculenta: 22
- Sorghum bicolor: 22
- Gossypium hirsutum: 19
- Brassica rapa: 18
- Saccharum spontaneum: 18

## 下一步建议

1. 保留 `completed-genome-index.tsv` 作为当前可直接使用的数据索引。
2. 对 `incomplete-genome-index.tsv` 中“只有基因组”的条目，优先从 NCBI Datasets、Ensembl Plants 和作物专项数据库补注释。
3. 对“空目录或仅元数据”的条目，后续如果不再补源，可以统一清理，但清理前应先按索引确认。
4. Phytozome 仍按原决定暂不下载，只在计划清单和报告中保留说明。
