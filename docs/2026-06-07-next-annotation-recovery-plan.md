# 下一轮注释补全方案

- 检查时间: 2026-06-07 11:22:38 CST
- 当前状态来源: `docs/current-download-status.md`、`docs/completed-genome-index.tsv`、`docs/incomplete-genome-index.tsv`

## 当前结论

- NCBI 第一轮下载已经结束，没有下载进程和 aria2 活动任务。
- 计划条目一共 1906 个。
- 有 genome 和至少一种注释的目录有 156 个，其中 149 个已经完全进入完成清单。
- 未完整目录有 1750 个；这些目录不是空目录，都已经有 genome 文件，主要缺少 GFF3/GTF 注释。
- `genome_down` 环境目前没有 `datasets` 命令，不能直接使用 NCBI Datasets CLI 补注释。

## 下一轮优先顺序

1. 先安装或补齐工具。
   - 优先在 `genome_down` 中安装 `ncbi-datasets-cli`。
   - 安装后先运行 `datasets --version` 记录版本。
   - 不建议一开始全量跑，先选 5 到 10 个失败 accession 做小样本测试。

2. 用 NCBI Datasets 测试补注释。
   - 对 `docs/incomplete-genome-index.tsv` 里的 accession 批量尝试。
   - 目标文件优先是 GFF3，其次是 GTF。
   - 如果 Datasets 包里也没有注释，就记录为“NCBI Datasets 也缺注释”，不要重复浪费时间。

3. 按物种转向专项数据库。
   - 水稻、玉米、小麦、大豆、油菜、番茄、马铃薯、葡萄、甜菜等重点作物优先查专项库或 Ensembl Plants。
   - 如果专项数据库只提供基因结构注释而 accession 名称不完全一致，需要在 README 里明确“注释来源与 genome 来源不同”。
   - Phytozome 继续按用户要求暂不下载，只保留记录。

4. 补齐文档。
   - 对补到注释的目录生成中文 `README.zh.md` 和英文 `README.md`。
   - 对确实没有注释来源的目录，生成中文失败说明，避免目录看起来像遗漏。
   - 每次阶段进展继续更新 `docs/current-download-status.md` 并推送 GitHub。

## 建议的批处理口径

- 第一批: 从 `incomplete-genome-index.tsv` 中每个物种抽 1 到 2 个 accession，验证 NCBI Datasets 是否能补到注释。
- 第二批: 如果 NCBI Datasets 有效，再按物种并发补注释，但保留限速和失败重试日志。
- 第三批: 对 Datasets 仍失败的重点作物，进入专项数据库人工规则。

## 当前不建议做的事

- 不建议删除 1750 个未完整目录，因为这些目录已经包含 genome 文件。
- 不建议把 genome-only 目录直接标记为完成，因为用户要求的是带 GFF/GTF 注释的基因组。
- 不建议现在启用 Phytozome 下载；该来源需要后续单独确认。
