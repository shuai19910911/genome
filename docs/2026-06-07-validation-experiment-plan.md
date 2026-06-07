# 外部注释补全验证实验计划

## Material Passport

- Origin Skill: experiment-agent
- Origin Mode: plan
- Origin Date: 2026-06-07T20:22:09+0800
- Verification Status: UNVERIFIED
- Version Label: code_plan_v1
- Upstream Dependencies:
  - `research_v1`: `docs/2026-06-07-data-availability-audit.md`
  - `validation_outcome_v1`: `docs/2026-06-07-validation-outcome-table.tsv`

## Experiment Overview

- **Title**: 多来源作物基因组外部注释补全路线的验证表现分析
- **Objective**: 量化不同外部注释来源在补全 GenBank GCA 作物基因组 GFF3/GTF 缺口时的通过率、失败类型和物种/assembly 层级偏倚。
- **Hypothesis**: Ensembl Plants 中 assembly 名称和 metadata 可对应的候选具有最高验证通过率；同物种但 accession/assembly 不一致的候选更容易出现 missing seqid 或 length mismatch；Scaffold/Contig 层级 assembly 的失败风险高于 Chromosome/Complete Genome。
- **Type**: analysis

## Research Questions

1. 外部注释路线的验证通过率是否存在明显差异？
2. 物种和 assembly 层级是否影响候选注释通过验证的概率？
3. 验证失败主要由 missing seqid/region 还是 length mismatch 驱动？
4. GTF metadata accession 与本地 accession 不一致时，是否仍可能通过坐标级验证？

## Variables

| 类型 | 变量 | 定义 |
|---|---|---|
| 因变量 | `verdict` | `pass` / `fail` / `unknown` |
| 自变量 | `source_route` | Ensembl Plants、Gramene、LegumeInfo、MaizeGDB、RefSeq paired |
| 自变量 | `species` | 本地 assembly 对应物种 |
| 自变量 | `assembly_level` | Chromosome、Scaffold、Contig、Complete Genome |
| 自变量 | `metadata_accession_match` | GTF metadata accession 是否等于本地 accession |
| 机制变量 | `failure_class` | missing_seqid_or_region、length_mismatch、其他 |
| 机制变量 | `missing_region_count` | genome 中缺失的 annotation region 数 |
| 机制变量 | `length_mismatch_count` | 坐标长度不一致的 region 数 |
| 机制变量 | `exact_seqid_length_matches` | seqid+length 精确匹配数 |

## Setup

- **Language/Framework**: Python 3，标准库 `csv` / `collections`
- **Entry Command**: `python3 scripts/summarize_validation_outcomes.py`
- **Working Directory**: `/home/user/zhangzhishuai/data/plantDB/genome`
- **Dependencies**: Python 标准库，无额外依赖
- **Environment**: 本地 Linux 工作区；不需要 GPU；不上传数据到外部服务

## Inputs

| Input | Path | Description |
|---|---|---|
| validation outcome 表 | `docs/2026-06-07-validation-outcome-table.tsv` | 99 条外部注释候选验证记录 |
| 数据可用性审计 | `docs/2026-06-07-data-availability-audit.md` | Stage 1 研究审计与候选 RQ |
| 完整索引 | `docs/completed-genome-index.tsv` | 已有 genome+annotation 的本地目录 |
| 未完整索引 | `docs/incomplete-genome-index.tsv` | 只有 genome、缺少 GFF3/GTF 的本地目录 |

## Expected Outputs

| Output | Path | Format | Success Criterion |
|---|---|---|---|
| route 汇总 | `docs/2026-06-07-validation-summary-by-route.tsv` | TSV | 总数为 99，route 总数之和等于 outcome 表记录数 |
| species 汇总 | `docs/2026-06-07-validation-summary-by-species.tsv` | TSV | 每个 species 的 pass/fail 数可追溯到 outcome 表 |
| assembly level 汇总 | `docs/2026-06-07-validation-summary-by-assembly-level.tsv` | TSV | assembly level 总数之和等于 99 |
| failure class 汇总 | `docs/2026-06-07-validation-summary-by-failure-class.tsv` | TSV | fail 记录应分配到 missing_seqid_or_region 或 length_mismatch 等类别 |

## Current Baseline Results

| 分组 | 主要结果 |
|---|---|
| source_route | Ensembl Plants 78/84 通过；RefSeq paired 3/3 通过；Gramene 0/7；MaizeGDB 0/3；LegumeInfo 1/2 |
| species | Hordeum vulgare 56/56 通过；Oryza sativa 15/19；Triticum aestivum 4/10；Zea mays 0/3 |
| assembly_level | Chromosome 78/86 通过；Complete Genome 3/3；Scaffold 1/9；Contig 0/1 |
| failure_class | 失败记录中 missing_seqid_or_region 12 条，length_mismatch 5 条 |

## Monitoring Configuration

- **Timeout**: 5 分钟
- **Monitor files**:
  - `docs/2026-06-07-validation-summary-by-route.tsv`
  - `docs/2026-06-07-validation-summary-by-species.tsv`
  - `docs/2026-06-07-validation-summary-by-assembly-level.tsv`
  - `docs/2026-06-07-validation-summary-by-failure-class.tsv`
- **Experiment type override**: analysis
- **Metric file**: `docs/2026-06-07-validation-summary-by-route.tsv`
- **Metric key**: `pass_rate`

## Analysis Plan

- **Primary metric**: route-level `pass_rate`
- **Secondary metrics**: species-level pass_rate、assembly_level pass_rate、failure_class count
- **Success threshold**:
  - 汇总脚本可重复运行且输出记录数守恒。
  - route 总数之和等于 outcome 表记录数。
  - failure_class 中非 none 记录数等于 outcome 表中 fail 记录数。
- **Comparison**:
  - Ensembl Plants vs Gramene/MaizeGDB 的通过率差异。
  - Chromosome/Complete Genome vs Scaffold/Contig 的通过率差异。
  - Hordeum vulgare 正向样本 vs Zea mays/Triticum aestivum 边界样本。

## Statistical Interpretation Plan

当前样本量仍偏探索性，尤其 RefSeq paired、LegumeInfo、MaizeGDB 样本较少，不应过度解释显著性。下一阶段可做：

1. 描述性统计：通过率、失败类型构成、物种分布。
2. 置信区间：对 route-level pass_rate 使用 Wilson interval。
3. 探索性模型：当样本量扩大后，用 logistic regression 评估 `source_route`、`species`、`assembly_level` 与 `verdict` 的关系。
4. 稳健性检查：将 Hordeum vulgare 从 Ensembl 中单独剥离，检查 Ensembl 高通过率是否主要由单物种驱动。

## Reproducibility Notes

- 当前计划只依赖本地 TSV 和 Python 标准库。
- 所有结论必须回溯到 `docs/2026-06-07-validation-outcome-table.tsv` 和单个 `docs/2026-06-07-GCA_*.validation.md` 报告。
- 后续每新增一批验证报告，应重新生成 outcome 表，再运行 `scripts/summarize_validation_outcomes.py`。

## Gate Decision

- 当前阶段: experiment-agent / plan
- 输出状态: UNVERIFIED，因为计划已制定且初始汇总已运行，但尚未完成后续样本扩展和统计验证报告。
- 下一步: 继续扩大验证样本，优先处理剩余 Hordeum vulgare Ensembl 候选和 RefSeq paired 候选；随后进入 experiment-agent / validate 模式。
