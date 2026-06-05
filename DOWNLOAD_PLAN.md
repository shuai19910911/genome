# 作物基因组下载计划

本文档定义作物基因组与注释文件下载前的规则。只有在候选清单经过审阅并确认后，才应开始下载基因组和注释数据。

## 目标

下载同时具备基因组 FASTA 和 GFF/GTF 注释文件的作物物种数据。每个选中的物种或 assembly 使用独立目录保存，并生成 README 文档，说明数据来源、文件大小、checksum、下载日期和基础组装信息。

## 推荐数据来源

优先使用稳定、公开、可复现的数据源，建议顺序如下：

1. Ensembl Plants
2. NCBI Datasets / RefSeq
3. NCBI GenBank，仅在 RefSeq 不可用时使用
4. 其他作物专项数据库，仅在明确批准后使用

Phytozome 很有价值，但部分下载需要登录或受许可限制，因此不作为默认来源。

## 执行前需要确认的范围

生成下载清单前，需要先确认以下规则：

1. 作物范围：
   - 严格常见作物，例如水稻、玉米、小麦、大豆、棉花、番茄、马铃薯、油菜、大麦、高粱、谷子、木薯、甘薯、甜菜等。
   - 扩展栽培植物，包括果树、蔬菜、牧草、药用植物和园艺植物。
   - 所有具备可用 GFF/GTF 注释的植物 assembly，不再严格限制是否为作物。

2. assembly 粒度：
   - 每个物种只保留一个代表 assembly。
   - 每个 assembly accession 或 cultivar 单独建目录。
   - 对主要作物保留多个重要 cultivar 或版本。

3. 多来源冲突规则：
   - 如果物种存在于 Ensembl Plants，优先使用 Ensembl Plants。
   - 如果存在高质量 RefSeq assembly，优先使用 NCBI RefSeq。
   - 如果 Ensembl 与 NCBI 版本差异较大，可同时保留两个版本。

4. 注释格式：
   - 优先 GFF3。
   - 如果没有 GFF3，再使用 GTF。
   - 如果 GFF3 和 GTF 都有，是否都下载需要单独确认。

5. 压缩格式：
   - 默认保留来源压缩文件 `.gz`。
   - 不默认解压，除非后续分析工具明确需要。

## 候选下载清单

第一阶段只生成候选清单，不下载基因组数据。建议输出文件：

`planned_downloads.tsv`

当前辅助文件：

- `config/crop_scope.tsv`：可编辑的作物范围表。
- `scripts/build_planned_downloads.py`：候选清单生成脚本。它检查来源目录并写出 `planned_downloads.tsv`，不下载基因组或注释文件本体。
- `scripts/summarize_planned_downloads.py`：只读汇总脚本。它统计 planned/skipped 行数、来源分布、注释格式、跳过原因和预计下载大小。
- `scripts/validate_planned_downloads.py`：只读预检脚本。它检查必需字段、重复输出目录、文件后缀、注释格式和非正数大小字段。
- `scripts/download_from_manifest.py`：基于已批准清单的执行脚本。默认 dry-run；只有传入 `--execute` 才会下载文件和创建物种目录。

严格作物范围的清单生成命令：

```bash
python3 scripts/build_planned_downloads.py --crop-scope config/crop_scope.tsv --out planned_downloads.tsv
```

包含 `include=review` 扩展作物的清单生成命令：

```bash
python3 scripts/build_planned_downloads.py --include-review --out planned_downloads.tsv
```

下载前汇总候选清单：

```bash
python3 scripts/summarize_planned_downloads.py --manifest planned_downloads.tsv
```

下载前预检候选清单：

```bash
python3 scripts/validate_planned_downloads.py --manifest planned_downloads.tsv
```

下载前 dry-run：

```bash
python3 scripts/download_from_manifest.py --manifest planned_downloads.tsv
```

审阅通过后才执行下载：

```bash
python3 scripts/download_from_manifest.py \
  --manifest planned_downloads.tsv \
  --final-manifest download_manifest.tsv \
  --failed-downloads failed_downloads.tsv \
  --execute
```

`planned_downloads.tsv` 必需列：

- `species`
- `common_name`
- `taxon_id`
- `assembly_accession`
- `assembly_name`
- `assembly_level`
- `source`
- `source_release`
- `genome_url`
- `annotation_url`
- `annotation_format`
- `genome_size_bytes`
- `annotation_size_bytes`
- `md5_url`
- `selection_reason`
- `status`
- `skip_reason`

只有同时具备 genome URL 和 annotation URL 的行才能标记为 `planned`。

## 目录结构

审阅通过并执行下载后，推荐目录结构如下：

```text
genome/
  DOWNLOAD_PLAN.md
  README.md
  planned_downloads.tsv
  download_manifest.tsv
  download.log
  failed_downloads.tsv
  scripts/
  Species_name_ASSEMBLY_ACCESSION/
    README.md
    README.zh.md
    genome/
      *.fa.gz
    annotation/
      *.gff3.gz or *.gtf.gz
    checksums/
      md5checksums.txt
      sha256sums.txt
    metadata/
      source_metadata.json
```

如果每个物种只保留一个代表 assembly，目录可以使用 `Species_name/`。如果允许多个 assembly，目录名必须包含 accession，避免混淆。

## 每个物种的 README 字段

每个物种目录应生成中文为主的 `README.md`，并同步生成中文副本 `README.zh.md`。两个文件都应说明同一组来源和文件元数据。

README 应至少包含：

- 学名
- 常用作物名
- Taxonomy ID
- assembly accession
- assembly 名称和版本
- assembly 级别
- 数据来源
- 来源版本或访问日期
- 原始 genome URL
- 原始 annotation URL
- genome 文件名和大小
- annotation 文件名和大小
- 注释格式
- checksum 方法和值
- 下载日期
- 选择理由
- cultivar、亚种、倍性或特殊处理备注

## 校验规则

进入 `download_manifest.tsv` 前，应满足：

1. genome URL 存在，并指向 FASTA 类文件。
2. annotation URL 存在，并指向 GFF、GFF3 或 GTF。
3. 文件大小字段为正数。
4. 有来源 checksum，或本地生成 SHA256。
5. 物种或 assembly 目录名唯一。

下载后应执行：

1. 如果来源提供远程大小，核对文件大小。
2. 如果来源提供 MD5，核对 MD5。
3. 为每个下载文件生成 SHA256。
4. 对压缩文件执行 gzip 完整性检查。
5. 确认 genome FASTA 至少包含一条序列记录。
6. 确认 annotation 文件具备可识别的 feature 行和 GFF/GTF 表格结构。

## 本地预下载检查

这些检查只使用临时文件和假 URL，不访问远程基因组来源，也不下载 genome 或 annotation 数据。

```bash
python3 -B -m unittest tests/test_manifest_workflow.py
python3 -B -m unittest tests/test_summarize_planned_downloads.py
python3 -B -m unittest tests/test_validate_planned_downloads.py
python3 -B -m py_compile scripts/build_planned_downloads.py scripts/summarize_planned_downloads.py scripts/validate_planned_downloads.py scripts/download_from_manifest.py tests/test_manifest_workflow.py tests/test_summarize_planned_downloads.py tests/test_validate_planned_downloads.py
```

## 失败处理

失败记录写入 `failed_downloads.tsv`，字段包括：

- `species`
- `assembly_accession`
- `source`
- `failed_step`
- `url`
- `error`
- `retry_count`
- `timestamp`

下载器应支持恢复执行，并避免重复下载已经通过 checksum 校验的文件。

## 执行阶段

1. 生成候选来源清单。
2. 筛选同时具备 genome FASTA 和 GFF/GTF annotation 的 assembly。
3. 估算总下载大小。
4. 汇总 `planned_downloads.tsv`。
5. 预检 `planned_downloads.tsv`。
6. 人工审阅 `planned_downloads.tsv`。
7. 对已批准行运行 dry-run。
8. 只有确认后才使用 `--execute` 下载。
9. 校验 checksum 和压缩文件完整性。
10. 为每个物种生成中文 `README.md` 和 `README.zh.md`。
11. 生成最终 `download_manifest.tsv` 和失败报告。

## 当前状态

目前仍处于规划和脚本准备阶段。尚未生成真实候选清单，尚未下载 genome 或 annotation 文件。
