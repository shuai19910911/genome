# 作物基因组注释补全数据可用性审计

## Material Passport

- artifact_id: plantdb_genome_annotation_availability_audit_2026-06-07
- artifact_type: dataset_audit
- version_label: research_v1
- generated_at: 2026-06-07 20:07:29 CST
- workflow_stage: ARS Stage 1 / RESEARCH
- source_workspace: `/home/user/zhangzhishuai/data/plantDB/genome`
- primary_inputs:
  - `local_reports/completed-genome-index.tsv`
  - `local_reports/incomplete-genome-index.tsv`
  - `docs/current-download-status.md`
  - `validation_reports/2026-06-07-GCA_*.validation.md`
  - `local_reports/2026-06-07-ensembl-plants-candidate-map.md`
  - `local_reports/2026-06-07-ensembl-plants-species-candidates.tsv`
- verification_status: ANALYZED
- integrity_scope: local file existence, local index classification, external annotation coordinate validation reports
- downstream_use: experiment planning, research question refinement, paper pipeline intake

## 审计结论

本地作物基因组库当前包含 1906 个 assembly 目录，其中 262 个已有 genome 和至少一种注释文件，1644 个只有 genome、缺少 GFF3/GTF 注释。注释缺口不是下载中断造成的空目录问题，而主要是 GenBank GCA 条目在 NCBI 端缺少 GFF3/GTF 注释。

外部注释补全路线目前呈现明显分层：Ensembl Plants 是当前最高收益路线，已验证通过 99 个候选、失败 7 个；RefSeq paired assembly 路线小样本 3/3 通过；LegumeInfo 2 个候选中 1 个通过；MaizeGDB 18 个候选中 3 个通过、15 个失败；Gramene 当前验证样本均未通过，不能作为直接归档路线。

## 当前数据状态

| 指标 | 数值 | 证据来源 |
|---|---:|---|
| assembly 目录总数 | 1906 | `docs/current-download-status.md` |
| genome+注释完整目录 | 262 | `local_reports/completed-genome-index.tsv` |
| 只有 genome、缺少 GFF3/GTF | 1644 | `local_reports/incomplete-genome-index.tsv` |
| 本地数据总量 | 903365117479 bytes / 841.32 GiB | `docs/current-download-status.md` |
| 已生成英文和中文 README 的完整目录 | 233 | `docs/current-download-status.md` |
| 同时具有 GFF3 和 GTF 的完整目录 | 232 | `local_reports/completed-genome-index.tsv` |
| 只有 GFF3、没有 GTF 的完整目录 | 6 | `local_reports/completed-genome-index.tsv` |

## 完整目录的物种分布

当前完整目录最多的物种为：

| 物种 | 完整目录数 |
|---|---:|
| Hordeum vulgare | 79 |
| Malus domestica | 42 |
| Oryza sativa | 23 |
| Triticum aestivum | 17 |
| Glycine max | 10 |
| Arachis hypogaea | 9 |
| Helianthus annuus | 9 |
| Brassica rapa | 6 |
| Cucumis melo | 6 |
| Solanum tuberosum | 6 |
| Brassica napus | 5 |
| Sorghum bicolor | 5 |

完整目录来源仍以 NCBI GenBank 为主：GenBank 210 个，RefSeq 28 个。后续分析需要明确区分“原始 NCBI 注释完整”和“外部补全后完整”两类来源。

## 缺口目录的物种分布

当前缺口最集中的物种为：

| 物种 | 缺少 GFF3/GTF 的目录数 | 优先级判断 |
|---|---:|---|
| Beta vulgaris | 326 | 高；缺口最大，但当前 Ensembl 只有同物种参考候选 |
| Zea mays | 185 | 高；MaizeGDB 小样本未通过，需重新设计验证路线 |
| Oryza sativa | 175 | 高；Ensembl 有多 accession 候选，但同物种混用风险高 |
| Hordeum vulgare | 139 | 高；Ensembl assembly 名称候选已连续高通过 |
| Citrullus lanatus | 117 | 中高；已有一个 Ensembl 成功案例 |
| Brassica napus | 107 | 中高；Ensembl 只有同物种参考候选，需防止误配 |
| Solanum tuberosum | 92 | 中高；已有一个 Ensembl 成功案例 |
| Vitis vinifera | 87 | 中；需先查外部专库或 RefSeq paired |
| Triticum aestivum | 56 | 中；已有 Ensembl 成功和失败样本，需按品种细分 |
| Cucumis sativus | 44 | 中；可进入 Ensembl/专库候选扫描 |
| Cucumis melo | 39 | 中；已有一个 Ensembl 成功案例 |
| Malus domestica | 38 | 中；已有 Ensembl 与 RefSeq paired 成功样本，也有失败样本 |

## 外部注释路线表现

| 路线 | 验证通过 | 验证失败 | 当前解释 |
|---|---:|---:|---|
| Ensembl Plants | 99 | 7 | 最高收益路线；必须继续做 accession、assembly、品种和长度级验证；assembly-name 候选已清空，species-only 候选不应直接自动归档 |
| RefSeq paired GCA->GCF | 3 | 0 | 小样本全通过；适合继续扩大 assembly_summary 配对扫描 |
| LegumeInfo | 1 | 1 | 对豆科作物有价值，但不同 assembly/版本风险明显 |
| Gramene | 0 | 7 | 小样本未通过；不应直接归档同物种参考注释 |
| MaizeGDB | 3 | 15 | PE0075、DK105、Dan340 通过；NAM 系列连续失败，后续需分组确认 assembly/version 证据后再扩大 |

## 证据、推断与建议

### 证据

- Ensembl Plants 当前已经归档 99 个候选，其中 Hordeum vulgare 贡献 76 个；Ensembl assembly-name 候选目前已清空。
- Hordeum vulgare 最近多批 HOR/HID/FT 等候选的 GTF metadata accession/genome-version 与本地 assembly 一致，并通过 seqid/长度验证。
- Gramene 和 MaizeGDB 的失败样本说明同物种注释不能直接混用；MaizeGDB 中 PE0075、DK105、Dan340 的成功样本说明同源 assembly-name 候选仍可作为小批验证路线。
- NCBI Datasets 小样本测试不能补齐 GenBank GCA 的 GFF3/GTF 缺口。

### 推断

- 当前项目最可发表的数据工程问题不是“下载更多 genome”，而是“如何在多来源植物数据库之间做可验证的注释补全”。
- 通过率差异本身可以构成方法学结果：不同数据源在 accession 对齐、assembly 命名、品种一致性和 scaffold 完整性上有系统性差异。
- Hordeum vulgare 是最适合作为正向样本集的物种；Zea mays、Oryza sativa、Gramene/MaizeGDB 失败样本适合作为负向或边界样本。

### 建议

- 继续优先处理剩余 Hordeum vulgare Ensembl assembly 名称候选，直到该路线收益明显下降。
- 同步扩大 RefSeq paired GCA->GCF 路线，因为它目前样本少但通过率高。
- 对 Beta vulgaris、Zea mays、Oryza sativa 三个高缺口物种分别建立独立验证策略，不要使用单一同物种参考注释批量合并。
- 将每个失败候选保留为负样本，后续用于总结失败类型：accession 不一致、sequence-region 缺失、seqid 缺失、长度不一致、scaffold 不完整。

## 候选研究问题

**RQ1:** 在作物 GenBank GCA 基因组条目中，缺失 GFF3/GTF 注释的 assembly 能否通过 Ensembl Plants、RefSeq paired assembly 和作物专项数据库进行可验证补全？

**RQ2:** 不同外部注释来源的验证通过率是否受到物种、assembly 层级、品种命名一致性和 scaffold 完整性的系统性影响？

**RQ3:** 基于 accession、assembly 名称、GTF metadata、seqid 别名和序列长度的多级验证流程，能否有效降低同物种注释误配风险？

## 下一步实验计划输入

1. 继续执行 Hordeum vulgare Ensembl 候选批处理，记录每批通过率和失败原因。
2. 重新扫描当前 incomplete index 中的 GCA->GCF paired assembly，扩大 RefSeq paired 验证样本。
3. 为高缺口物种生成分物种路线表：Beta vulgaris、Zea mays、Oryza sativa、Hordeum vulgare、Citrullus lanatus。
4. 设计一个 validation outcome 表，字段至少包括 source_route、species、assembly_accession、candidate_accession、metadata_match、seqid_match_count、missing_seqid_count、length_mismatch_count、verdict。
5. 在 ARS experiment-agent 阶段，将以上 outcome 表作为可重复统计分析输入，报告各来源通过率、失败类型构成和物种偏倚。

## 当前门控状态

- Stage: ARS Stage 1 / RESEARCH
- Gate: 尚未进入写作；需要先完成实验设计与更多验证样本。
- Blocking issue: 尚未完成后续批次验证与统计建模；统一 validation outcome 汇总表已生成。
- Produced next artifact: `local_reports/2026-06-07-validation-outcome-table.tsv`
