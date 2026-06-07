# NCBI Datasets 注释可用性小样本测试

- 检查时间: 2026-06-07 11:39:22
- 测试方式: 对样本 accession 运行 `datasets download genome accession --include none/gff3/gtf --preview`。
- 说明: 本测试只看 Datasets 是否声明可提供注释文件，不下载正式数据。
- 样本数: 10

## 结果概览

- Datasets 未给出注释，CLI 请求注释时崩溃: 10

## 样本明细

- GCA_000397105.1 (Beta vulgaris): Datasets 未给出注释，CLI 请求注释时崩溃
- GCA_000227425.1 (Hordeum vulgare): Datasets 未给出注释，CLI 请求注释时崩溃
- GCA_000164945.1 (Oryza sativa): Datasets 未给出注释，CLI 请求注释时崩溃
- GCA_000223545.1 (Zea mays): Datasets 未给出注释，CLI 请求注释时崩溃
- GCA_000238415.2 (Citrullus lanatus): Datasets 未给出注释，CLI 请求注释时崩溃
- GCA_000686985.2 (Brassica napus): Datasets 未给出注释，CLI 请求注释时崩溃
- GCA_009827155.1 (Solanum tuberosum): Datasets 未给出注释，CLI 请求注释时崩溃
- GCA_002922885.1 (Vitis vinifera): Datasets 未给出注释，CLI 请求注释时崩溃
- GCA_000188135.1 (Triticum aestivum): Datasets 未给出注释，CLI 请求注释时崩溃
- GCA_001269945.2 (Glycine max): Datasets 未给出注释，CLI 请求注释时崩溃

## 结论

- 已安装 `ncbi-datasets-cli`，当前版本可用于后续测试。
- 对已知有注释的 RefSeq accession，Datasets 能正常报告 GFF3/GTF；但本次抽到的 genome-only GenBank 样本没有报告可用注释。
- 对没有注释的 accession，请求 `--include gff3` 或 `--include gtf` 时 CLI 可能崩溃；后续脚本需要把这种情况当作“Datasets 无注释”，并继续尝试专项数据库。
- 详细 TSV: `docs/2026-06-07-datasets-annotation-test.tsv`
