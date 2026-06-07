# Ensembl Plants 注释候选匹配报告

- 检查时间: 2026-06-07 12:06:55
- Ensembl Plants FTP 根目录: `https://ftp.ebi.ac.uk/ensemblgenomes/pub/plants/current/`
- GFF3 根目录状态: cached
- GTF 根目录状态: cached
- 本地 genome-only 条目数: 1750
- 本地涉及物种数: 31
- 本次扫描物种数: 12
- 每个物种最多扫描目录数: 25
- Ensembl Plants 中找到同物种目录的物种数: 12
- 找到精确 accession 匹配的本地条目数: 1
- 找到精确 accession 匹配的物种数: 1

## 分类统计

- 精确 accession 候选目录数: 1
- assembly 名称候选目录数: 48
- 只有同物种候选目录数: 21

## 主要结论

- 有 accession 级别匹配，可以优先对这些条目做小样本下载和坐标验证。
- 同物种候选不能直接标记为完成，必须核对 assembly、cultivar、染色体命名和 FASTA 序列长度。
- 如果只能找到同物种参考注释，应单独建参考目录或在 README 中明确“注释来源与 genome 来源不同”。

## 输出文件

- 精确匹配表: `docs/2026-06-07-ensembl-plants-exact-matches.tsv`
- 物种候选表: `docs/2026-06-07-ensembl-plants-species-candidates.tsv`

## 精确匹配样例

- GCA_949126075.2 (Triticum aestivum): triticum_aestivum_paragon

## 同物种候选 Top 20

- Beta vulgaris / beta_vulgaris: GFF3=yes, GTF=yes, 本地未完整 326
- Hordeum vulgare / hordeum_vulgare: GFF3=yes, GTF=yes, 本地未完整 195
- Hordeum vulgare / hordeum_vulgare_10tj18: GFF3=yes, GTF=yes, 本地未完整 195
- Hordeum vulgare / hordeum_vulgare_aizu6: GFF3=yes, GTF=yes, 本地未完整 195
- Hordeum vulgare / hordeum_vulgare_akashinriki: GFF3=yes, GTF=yes, 本地未完整 195
- Hordeum vulgare / hordeum_vulgare_barke: GFF3=yes, GTF=yes, 本地未完整 195
- Hordeum vulgare / hordeum_vulgare_bonus: GFF3=yes, GTF=yes, 本地未完整 195
- Hordeum vulgare / hordeum_vulgare_bowman: GFF3=yes, GTF=yes, 本地未完整 195
- Hordeum vulgare / hordeum_vulgare_chikurinibaraki1: GFF3=yes, GTF=yes, 本地未完整 195
- Hordeum vulgare / hordeum_vulgare_foma: GFF3=yes, GTF=yes, 本地未完整 195
- Hordeum vulgare / hordeum_vulgare_ft11: GFF3=yes, GTF=yes, 本地未完整 195
- Hordeum vulgare / hordeum_vulgare_ft144: GFF3=yes, GTF=yes, 本地未完整 195
- Hordeum vulgare / hordeum_vulgare_ft262: GFF3=yes, GTF=yes, 本地未完整 195
- Hordeum vulgare / hordeum_vulgare_ft286: GFF3=yes, GTF=yes, 本地未完整 195
- Hordeum vulgare / hordeum_vulgare_ft333: GFF3=yes, GTF=yes, 本地未完整 195
- Hordeum vulgare / hordeum_vulgare_ft628: GFF3=yes, GTF=yes, 本地未完整 195
- Hordeum vulgare / hordeum_vulgare_ft67: GFF3=yes, GTF=yes, 本地未完整 195
- Hordeum vulgare / hordeum_vulgare_ft880: GFF3=yes, GTF=yes, 本地未完整 195
- Hordeum vulgare / hordeum_vulgare_goldenmelon: GFF3=yes, GTF=yes, 本地未完整 195
- Hordeum vulgare / hordeum_vulgare_goldenpromise: GFF3=yes, GTF=yes, 本地未完整 195