# 下一轮注释补全方案

- 检查时间: 2026-06-07 11:41:18 CST
- 当前状态来源: `docs/current-download-status.md`、`docs/completed-genome-index.tsv`、`docs/incomplete-genome-index.tsv`

## 当前结论

- NCBI 第一轮下载已经结束，没有下载进程和 aria2 活动任务。
- 计划条目一共 1906 个。
- 有 genome 和至少一种注释的目录有 156 个，其中 149 个已经完全进入完成清单。
- 未完整目录有 1750 个；这些目录不是空目录，都已经有 genome 文件，主要缺少 GFF3/GTF 注释。
- `genome_down` 环境已安装 `ncbi-datasets-cli`，`datasets` 版本为 18.29.1。
- 已抽样测试 10 个 genome-only 的 GenBank (`GCA`) accession；这些样本在 Datasets 中能查到 genome 记录，但没有得到 GFF3/GTF 注释，请求注释时 CLI 会崩溃。

## 下一轮优先顺序

1. 保留 Datasets 作为辅助验证工具。
   - `ncbi-datasets-cli` 已安装，可以继续少量验证 accession。
   - 对本轮 1750 个 genome-only 的 GCA 条目，不建议直接全量跑 Datasets；抽样结果显示成功率很低，而且 CLI 会在无注释时崩溃。
   - 后续脚本遇到 Datasets 崩溃，应记录为“Datasets 无可用注释”，不要无限重试。

2. 按物种转向专项数据库。
   - 水稻、玉米、小麦、大豆、油菜、番茄、马铃薯、葡萄、甜菜等重点作物优先查专项库或 Ensembl Plants。
   - 如果专项数据库只提供基因结构注释而 accession 名称不完全一致，需要在 README 里明确“注释来源与 genome 来源不同”。
   - Phytozome 继续按用户要求暂不下载，只保留记录。

3. 补齐文档。
   - 对补到注释的目录生成中文 `README.zh.md` 和英文 `README.md`。
   - 对确实没有注释来源的目录，生成中文失败说明，避免目录看起来像遗漏。
   - 每次阶段进展继续更新 `docs/current-download-status.md` 并推送 GitHub。

## 建议的批处理口径

- 第一批: 从 `incomplete-genome-index.tsv` 中按物种建立专项数据库候选表，先覆盖失败最多的作物。
- 第二批: 对每个物种找 1 到 2 个权威专项来源做小样本验证，确认注释坐标版本是否能和现有 genome 对上。
- 第三批: 对验证通过的来源批量补注释；对验证不通过的来源只记录，不强行混用。

## 当前不建议做的事

- 不建议删除 1750 个未完整目录，因为这些目录已经包含 genome 文件。
- 不建议把 genome-only 目录直接标记为完成，因为用户要求的是带 GFF/GTF 注释的基因组。
- 不建议现在启用 Phytozome 下载；该来源需要后续单独确认。
