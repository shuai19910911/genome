# 2026-06-05 候选下载清单摘要

## 本次生成了什么

已生成 `planned_downloads.tsv`。

这是一个“快速候选清单”，来源为 NCBI RefSeq 和 NCBI GenBank 的 plant assembly summary。它只整理公开 FTP 路径和候选文件 URL，没有下载 genome、GFF3 或 GTF 数据文件。

## 数量概览

- 总行数：1906 个候选 assembly
- planned 行数：1906
- skipped 行数：0
- 来源分布：
  - NCBI GenBank：1878
  - NCBI RefSeq：28
- 注释格式：
  - `GFF3;GTF`：1906

## 各作物候选数量

| 物种 | 候选 assembly 数 |
|---|---:|
| Beta vulgaris | 328 |
| Hordeum vulgare | 202 |
| Oryza sativa | 198 |
| Zea mays | 189 |
| Citrullus lanatus | 118 |
| Brassica napus | 112 |
| Solanum tuberosum | 98 |
| Vitis vinifera | 90 |
| Malus domestica | 80 |
| Triticum aestivum | 73 |
| Cucumis sativus | 45 |
| Cucumis melo | 45 |
| Glycine max | 42 |
| Solanum lycopersicum | 39 |
| Brassica oleracea | 32 |
| Sorghum bicolor | 27 |
| Brassica rapa | 24 |
| Manihot esculenta | 23 |
| Gossypium hirsutum | 22 |
| Arachis hypogaea | 18 |
| Saccharum spontaneum | 18 |
| Phaseolus vulgaris | 15 |
| Prunus persica | 12 |
| Helianthus annuus | 11 |
| Setaria italica | 10 |
| Musa acuminata | 10 |
| Vigna radiata | 7 |
| Lactuca sativa | 6 |
| Daucus carota | 6 |
| Cicer arietinum | 4 |
| Ipomoea batatas | 2 |

## 需要注意的地方

1. 这是快速清单。
   - 为了避免逐个检查 1906 个 assembly 的 genome/GFF/GTF URL 导致运行很慢，本次没有逐个 HEAD 检查文件大小。
   - 因此 `genome_size_bytes`、`annotation_size_bytes` 等大小字段暂时为空。

2. `GFF3;GTF` 表示候选路径已经按 NCBI 命名规则生成。
   - 后续严格预检或正式下载时，还需要确认对应文件是否真实存在。
   - 如果某些 assembly 只有 GFF3 或只有 GTF，下载阶段会记录失败或需要二次清理。

3. 本次还没有加入 Ensembl Plants。
   - 全来源模式在 Ensembl/URL 检查阶段运行较慢。
   - 当前先完成 NCBI 候选清单，后续再单独补充 Ensembl Plants 和作物专项数据库。

4. 尚未下载任何 genome 或 annotation 数据文件。

## 已运行的检查

```bash
python3 -B scripts/summarize_planned_downloads.py --manifest planned_downloads.tsv
python3 -B scripts/validate_planned_downloads.py --manifest planned_downloads.tsv --allow-unknown-size
```

结果：预检通过，1906 行已检查。

## 下一步

1. 对 `planned_downloads.tsv` 做抽样 URL 检查。
2. 增加严格预检模式，补齐真实文件大小。
3. 单独补充 Ensembl Plants 来源。
4. 开始整理作物专项数据库来源入口。
5. 继续阶段性更新进度文档并推送 GitHub。
