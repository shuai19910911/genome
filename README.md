# genome

作物基因组与注释文件下载工作区。

本仓库用于规划和执行作物基因组数据集的本地构建流程。目标是为具有
GFF/GTF 注释的作物物种下载基因组 FASTA 和对应注释文件，并按物种或
assembly 建目录保存。

当前流程强调先审阅、再执行：

1. 维护作物范围表。
2. 生成候选下载清单 `planned_downloads.tsv`。
3. 汇总和预检候选清单。
4. 先 dry-run，确认目录和文件路径。
5. 通过 `--execute` 显式执行下载。
6. 为每个物种目录生成中文 README 文档、元数据和校验文件。

当前已确认的下载策略：

- 作物范围：扩展栽培植物。
- assembly 粒度：尽量收集当前作物所有已有基因组；不同 cultivar 或不同 assembly accession 都进入候选。
- 去重规则：同一 cultivar 或同一 assembly 的重复版本，只保留更合适的一份。
- 注释格式：尽量同时保留 GFF3 和 GTF。
- 压缩格式：默认保留来源 `.gz` 文件。
- 数据源：Ensembl Plants、NCBI RefSeq/GenBank 和作物专项数据库均可使用。
- Phytozome：先记录，不下载，后续再决定是否使用。

阶段进度见 [docs/2026-06-05-progress.md](docs/2026-06-05-progress.md)。

仓库当前只保存规划文档、配置、脚本和测试，不提交基因组或注释数据本体。
