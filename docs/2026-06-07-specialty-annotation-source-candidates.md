# 作物注释补源候选来源

- 检查时间: 2026-06-07 11:41:18 CST
- 目的: 为 1750 个“只有 genome、缺少 GFF3/GTF 注释”的目录寻找后续补注释来源。
- 当前判断: NCBI Datasets 对抽样 GCA 条目没有补到注释，下一步应按物种查 Ensembl Plants、Gramene 和作物专项数据库。

## 优先来源

| 来源 | 适合用途 | GFF3/GTF 情况 | 当前处理建议 |
|---|---|---|---|
| Ensembl Plants FTP | 多数常见作物的参考 genome 和注释 | 官方 FTP 当前有 `gff3/` 和 `gtf/` 目录 | 优先建立自动匹配脚本，但必须检查 assembly/cultivar 是否和本地 genome 一致 |
| Gramene | 禾本科和多种作物参考注释 | Gramene bulk download 说明包含 GTF/GFF3 | 可作为 Ensembl Plants 的补充入口，特别是水稻、玉米、小麦、大麦、高粱 |
| SoyBase / LegumeInfo | 大豆和豆科作物 | SoyBase 资源页记录 soybean genome/annotation 版本命名 | 优先用于大豆 cultivar 或泛豆科条目 |
| MaizeGDB | 玉米 B73 和玉米专项注释 | MaizeGDB assembly 页面提供参考组装和 gene model 下载入口 | 优先用于玉米，尤其是 B73 和 NAM 相关版本 |
| Phytozome | 多植物 genome/annotation | 通常有 GFF3 等注释下载 | 用户已要求暂不下载，只记录后续可选 |

## 失败最多物种的建议路线

| 物种 | 未完整目录数 | 推荐第一来源 | 说明 |
|---|---:|---|---|
| Beta vulgaris | 326 | Ensembl Plants | Ensembl Plants 当前列表包含 `beta_vulgaris`，可先核对参考版本 |
| Hordeum vulgare | 195 | Ensembl Plants / Gramene | 大麦是 Ensembl Plants 热门作物之一，GTF/GFF3 入口明确 |
| Oryza sativa | 190 | Ensembl Plants / Gramene | Ensembl Plants 有多个水稻品种目录，适合先做 cultivar 匹配 |
| Zea mays | 185 | MaizeGDB / Ensembl Plants / Gramene | 玉米优先查 MaizeGDB，再用 Ensembl Plants 补参考版本 |
| Citrullus lanatus | 118 | Ensembl Plants | 当前 Ensembl Plants GFF3/GTF 列表包含 `citrullus_lanatus` |
| Brassica napus | 107 | Ensembl Plants | 当前 Ensembl Plants GFF3/GTF 列表包含 `brassica_napus` |
| Solanum tuberosum | 93 | Ensembl Plants | 当前 Ensembl Plants GFF3/GTF 列表包含 `solanum_tuberosum` 和 `solanum_tuberosum_rh8903916` |
| Vitis vinifera | 87 | Ensembl Plants | 当前 Ensembl Plants GFF3/GTF 列表包含 `vitis_vinifera` |
| Triticum aestivum | 60 | Ensembl Plants / Gramene | Ensembl Plants 有多个小麦 cultivar 目录和 `triticum_aestivum_refseqv2` |
| Glycine max | 33 | SoyBase / LegumeInfo / Ensembl Plants | 大豆优先用 SoyBase/LegumeInfo 判断 genome/annotation 版本 |

## 执行原则

- 不能只因为物种名相同就把注释混到本地 genome 上；必须核对 assembly 名称、cultivar、BioProject、染色体命名和 FASTA 序列长度。
- 如果专项数据库注释与本地 genome 不是同一个 assembly，只能记录为“同物种参考注释”，不能标记为该目录已完整。
- 如果专项数据库只有 GFF3，没有 GTF，可以先保留 GFF3，并在 README 里说明 GTF 缺失或后续由工具转换。
- 每个物种先做 1 到 2 个小样本，验证坐标和文件格式，再批量下载。

## 官方来源链接

- Ensembl Plants FTP 说明: https://plants.ensembl.org/info/data/ftp/index.html
- Ensembl Plants 当前 FTP 根目录: https://ftp.ebi.ac.uk/ensemblgenomes/pub/plants/current/
- Ensembl Plants 当前 GFF3 目录: https://ftp.ebi.ac.uk/ensemblgenomes/pub/plants/current/gff3/
- Ensembl Plants 当前 GTF 目录: https://ftp.ebi.ac.uk/ensemblgenomes/pub/plants/current/gtf/
- Gramene bulk download: https://news.gramene.org/node/297
- SoyBase resources: https://www.soybase.org/resources/
- MaizeGDB assembly information: https://maizegdb.org/assembly
