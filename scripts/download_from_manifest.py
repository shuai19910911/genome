#!/usr/bin/env python3
"""Download approved crop genome rows and generate per-species README files.

By default this script runs in dry-run mode and does not download anything.
Pass `--execute` only after `planned_downloads.tsv` has been reviewed.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


REQUIRED_COLUMNS = {
    "species",
    "common_name",
    "taxon_id",
    "assembly_accession",
    "assembly_name",
    "assembly_level",
    "source",
    "source_release",
    "genome_url",
    "annotation_url",
    "annotation_format",
    "genome_size_bytes",
    "annotation_size_bytes",
    "md5_url",
    "selection_reason",
    "status",
    "skip_reason",
}

FINAL_MANIFEST_COLUMNS = [
    *sorted(REQUIRED_COLUMNS),
    "species_dir",
    "genome_path",
    "annotation_path",
    "gff3_path",
    "gtf_path",
    "genome_sha256",
    "annotation_sha256",
    "gff3_sha256",
    "gtf_sha256",
    "download_date",
    "validation_status",
]

FAILED_COLUMNS = [
    "species",
    "assembly_accession",
    "source",
    "failed_step",
    "url",
    "error",
    "retry_count",
    "timestamp",
]


def read_manifest(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        missing = REQUIRED_COLUMNS.difference(reader.fieldnames or [])
        if missing:
            raise ValueError(f"{path} missing required columns: {', '.join(sorted(missing))}")
        return [dict(row) for row in reader]


def safe_name(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", value.strip())
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    return cleaned or "unknown"


def species_dir_name(row: dict[str, str]) -> str:
    species = safe_name(row["species"])
    accession = safe_name(row.get("assembly_accession", ""))
    return f"{species}_{accession}" if accession else species


def basename_from_url(url: str) -> str:
    return Path(urllib.parse.urlparse(url).path).name


def downloader_env() -> dict[str, str]:
    env = dict(os.environ)
    for key in list(env):
        if key.lower() in {"http_proxy", "https_proxy", "ftp_proxy", "all_proxy", "no_proxy"}:
            env.pop(key, None)
    return env


def annotation_urls(row: dict[str, str]) -> list[tuple[str, str]]:
    urls: list[tuple[str, str]] = []
    if row.get("gff3_url"):
        urls.append(("gff3", row["gff3_url"]))
    if row.get("gtf_url"):
        urls.append(("gtf", row["gtf_url"]))
    if not urls and row.get("annotation_url"):
        urls.append(("annotation", row["annotation_url"]))
    seen: set[str] = set()
    unique: list[tuple[str, str]] = []
    for label, url in urls:
        if url not in seen:
            unique.append((label, url))
            seen.add(url)
    return unique


def download_url(url: str, out_path: Path, retries: int, sleep_seconds: float) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = out_path.with_suffix(out_path.suffix + ".part")
    if shutil.which("aria2c"):
        last_error: subprocess.CalledProcessError | None = None
        for attempt in range(1, retries + 1):
            cmd = [
                "aria2c",
                "--continue=true",
                "--max-tries=2",
                "--retry-wait",
                str(int(sleep_seconds)),
                "--timeout=120",
                "--connect-timeout=60",
                "--max-connection-per-server=1",
                "--split=1",
                "--min-split-size=8M",
                "--file-allocation=none",
                "--allow-overwrite=true",
                "--auto-file-renaming=false",
                "--dir",
                str(tmp_path.parent),
                "--out",
                tmp_path.name,
                url,
            ]
            try:
                subprocess.run(cmd, check=True, env=downloader_env())
                tmp_path.replace(out_path)
                return
            except subprocess.CalledProcessError as exc:
                last_error = exc
                if attempt == retries:
                    break
                print(
                    f"aria2c failed for {url} on attempt {attempt}/{retries}; "
                    f"will resume after {sleep_seconds * attempt:.0f}s",
                    file=sys.stderr,
                    flush=True,
                )
                time.sleep(sleep_seconds * attempt)
        raise RuntimeError(f"aria2c download failed after {retries} attempts: {last_error}") from last_error

    if shutil.which("curl"):
        last_error: subprocess.CalledProcessError | None = None
        for attempt in range(1, retries + 1):
            cmd = [
                "curl",
                "-L",
                "--fail",
                "--retry",
                "2",
                "--retry-delay",
                str(int(sleep_seconds)),
                "-C",
                "-",
                "-o",
                str(tmp_path),
                url,
            ]
            try:
                subprocess.run(cmd, check=True, env=downloader_env())
                tmp_path.replace(out_path)
                return
            except subprocess.CalledProcessError as exc:
                last_error = exc
                if attempt == retries:
                    break
                print(
                    f"curl failed for {url} on attempt {attempt}/{retries}; "
                    f"will resume after {sleep_seconds * attempt:.0f}s",
                    file=sys.stderr,
                    flush=True,
                )
                time.sleep(sleep_seconds * attempt)
        raise RuntimeError(f"curl download failed after {retries} attempts: {last_error}") from last_error

    headers = {"User-Agent": "crop-genome-downloader/0.1"}
    for attempt in range(1, retries + 1):
        try:
            request = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(request, timeout=120) as response, tmp_path.open("wb") as handle:
                shutil.copyfileobj(response, handle, length=1024 * 1024)
            tmp_path.replace(out_path)
            return
        except (urllib.error.URLError, TimeoutError) as exc:
            if attempt == retries:
                raise RuntimeError(f"download failed after {retries} attempts: {exc}") from exc
            time.sleep(sleep_seconds * attempt)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def gzip_ok(path: Path) -> bool:
    if not path.name.endswith(".gz"):
        return True
    try:
        with gzip.open(path, "rb") as handle:
            while handle.read(1024 * 1024):
                pass
        return True
    except OSError:
        return False


def first_non_comment_line(path: Path) -> str:
    opener = gzip.open if path.name.endswith(".gz") else open
    mode = "rt"
    with opener(path, mode, errors="replace") as handle:  # type: ignore[arg-type]
        for line in handle:
            if line.strip() and not line.startswith("#"):
                return line.rstrip("\n")
    return ""


def validate_downloads(genome_path: Path, annotation_path: Path) -> str:
    problems: list[str] = []
    if not genome_path.exists() or genome_path.stat().st_size == 0:
        problems.append("missing_or_empty_genome")
    if not annotation_path.exists() or annotation_path.stat().st_size == 0:
        problems.append("missing_or_empty_annotation")
    if genome_path.exists() and not gzip_ok(genome_path):
        problems.append("invalid_genome_gzip")
    if annotation_path.exists() and not gzip_ok(annotation_path):
        problems.append("invalid_annotation_gzip")
    if genome_path.exists() and first_non_comment_line(genome_path)[:1] != ">":
        problems.append("genome_not_fasta_like")
    annotation_line = first_non_comment_line(annotation_path) if annotation_path.exists() else ""
    if annotation_line and len(annotation_line.split("\t")) < 8:
        problems.append("annotation_not_tabular_gff_gtf_like")
    return "ok" if not problems else ";".join(problems)


def write_readme(
    row: dict[str, str],
    species_dir: Path,
    genome_path: Path,
    annotation_path: Path,
    genome_sha256: str,
    annotation_sha256: str,
    validation_status: str,
    download_date: str,
) -> None:
    readme = species_dir / "README.md"
    content = f"""# {row['species']}

## 来源

- 学名: {row['species']}
- 常用名: {row.get('common_name', '')}
- Taxonomy ID: {row.get('taxon_id', '')}
- 组装编号: {row.get('assembly_accession', '')}
- 组装名称: {row.get('assembly_name', '')}
- 组装级别: {row.get('assembly_level', '')}
- 数据来源: {row.get('source', '')}
- 来源版本: {row.get('source_release', '')}
- 下载日期: {download_date}
- 选择理由: {row.get('selection_reason', '')}

## 文件

- 基因组 URL: {row.get('genome_url', '')}
- 基因组文件: {genome_path.name}
- 基因组本地文件大小 bytes: {genome_path.stat().st_size if genome_path.exists() else ''}
- 基因组来源标注大小 bytes: {row.get('genome_size_bytes', '')}
- 基因组 SHA256: {genome_sha256}
- 注释 URL: {row.get('annotation_url', '')}
- 注释文件: {annotation_path.name}
- 注释格式: {row.get('annotation_format', '')}
- 注释本地文件大小 bytes: {annotation_path.stat().st_size if annotation_path.exists() else ''}
- 注释来源标注大小 bytes: {row.get('annotation_size_bytes', '')}
- 注释 SHA256: {annotation_sha256}
- 来源 checksum URL: {row.get('md5_url', '')}

## 校验

- 校验状态: {validation_status}

## 备注

{row.get('skip_reason', '')}
"""
    readme.write_text(content)


def write_readme_zh(
    row: dict[str, str],
    species_dir: Path,
    genome_path: Path,
    annotation_path: Path,
    genome_sha256: str,
    annotation_sha256: str,
    validation_status: str,
    download_date: str,
) -> None:
    readme = species_dir / "README.zh.md"
    content = f"""# {row['species']}

## 来源

- 学名: {row['species']}
- 常用名: {row.get('common_name', '')}
- Taxonomy ID: {row.get('taxon_id', '')}
- 组装编号: {row.get('assembly_accession', '')}
- 组装名称: {row.get('assembly_name', '')}
- 组装级别: {row.get('assembly_level', '')}
- 数据来源: {row.get('source', '')}
- 来源版本: {row.get('source_release', '')}
- 下载日期: {download_date}
- 选择理由: {row.get('selection_reason', '')}

## 文件

- 基因组 URL: {row.get('genome_url', '')}
- 基因组文件: {genome_path.name}
- 基因组本地文件大小 bytes: {genome_path.stat().st_size if genome_path.exists() else ''}
- 基因组来源标注大小 bytes: {row.get('genome_size_bytes', '')}
- 基因组 SHA256: {genome_sha256}
- 注释 URL: {row.get('annotation_url', '')}
- 注释文件: {annotation_path.name}
- 注释格式: {row.get('annotation_format', '')}
- 注释本地文件大小 bytes: {annotation_path.stat().st_size if annotation_path.exists() else ''}
- 注释来源标注大小 bytes: {row.get('annotation_size_bytes', '')}
- 注释 SHA256: {annotation_sha256}
- 来源 checksum URL: {row.get('md5_url', '')}

## 校验

- 校验状态: {validation_status}

## 备注

{row.get('skip_reason', '')}
"""
    readme.write_text(content)


def write_metadata(row: dict[str, str], metadata_path: Path) -> None:
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.write_text(json.dumps(row, indent=2, sort_keys=True) + "\n")


def process_row(
    row: dict[str, str],
    output_dir: Path,
    execute: bool,
    retries: int,
    sleep_seconds: float,
) -> dict[str, str]:
    species_dir = output_dir / species_dir_name(row)
    genome_path = species_dir / "genome" / basename_from_url(row["genome_url"])
    annotations = annotation_urls(row)
    annotation_path = species_dir / "annotation" / basename_from_url(annotations[0][1])
    gff3_path = species_dir / "annotation" / basename_from_url(row.get("gff3_url", "")) if row.get("gff3_url") else Path("")
    gtf_path = species_dir / "annotation" / basename_from_url(row.get("gtf_url", "")) if row.get("gtf_url") else Path("")
    download_date = datetime.now(timezone.utc).date().isoformat()

    result = {column: row.get(column, "") for column in REQUIRED_COLUMNS}
    result.update(
        {
            "species_dir": str(species_dir),
            "genome_path": str(genome_path),
            "annotation_path": str(annotation_path),
            "gff3_path": str(gff3_path),
            "gtf_path": str(gtf_path),
            "genome_sha256": "",
            "annotation_sha256": "",
            "gff3_sha256": "",
            "gtf_sha256": "",
            "download_date": download_date,
            "validation_status": "dry_run",
        }
    )

    if not execute:
        print(f"DRY-RUN {row['species']}: {genome_path} and {annotation_path}")
        return result

    if row.get("status") != "planned":
        result["validation_status"] = "skipped_not_planned"
        return result

    species_dir.mkdir(parents=True, exist_ok=True)
    (species_dir / "checksums").mkdir(exist_ok=True)
    write_metadata(row, species_dir / "metadata" / "source_metadata.json")

    if not genome_path.exists():
        download_url(row["genome_url"], genome_path, retries=retries, sleep_seconds=sleep_seconds)
    annotation_paths: dict[str, Path] = {}
    for label, url in annotations:
        path = species_dir / "annotation" / basename_from_url(url)
        annotation_paths[label] = path
        if not path.exists():
            download_url(url, path, retries=retries, sleep_seconds=sleep_seconds)

    genome_sha256 = sha256_file(genome_path)
    annotation_sha256 = sha256_file(annotation_path)
    gff3_sha256 = sha256_file(annotation_paths["gff3"]) if "gff3" in annotation_paths else ""
    gtf_sha256 = sha256_file(annotation_paths["gtf"]) if "gtf" in annotation_paths else ""
    sha_path = species_dir / "checksums" / "sha256sums.txt"
    checksum_lines = [f"{genome_sha256}  {genome_path.relative_to(species_dir)}"]
    for path in annotation_paths.values():
        checksum_lines.append(f"{sha256_file(path)}  {path.relative_to(species_dir)}")
    sha_path.write_text("\n".join(checksum_lines) + "\n")

    validation_status = validate_downloads(genome_path, annotation_path)
    write_readme(
        row=row,
        species_dir=species_dir,
        genome_path=genome_path,
        annotation_path=annotation_path,
        genome_sha256=genome_sha256,
        annotation_sha256=annotation_sha256,
        validation_status=validation_status,
        download_date=download_date,
    )
    write_readme_zh(
        row=row,
        species_dir=species_dir,
        genome_path=genome_path,
        annotation_path=annotation_path,
        genome_sha256=genome_sha256,
        annotation_sha256=annotation_sha256,
        validation_status=validation_status,
        download_date=download_date,
    )
    result.update(
        {
            "genome_sha256": genome_sha256,
            "annotation_sha256": annotation_sha256,
            "gff3_sha256": gff3_sha256,
            "gtf_sha256": gtf_sha256,
            "validation_status": validation_status,
        }
    )
    return result


def row_completed(row: dict[str, str], output_dir: Path) -> bool:
    species_dir = output_dir / species_dir_name(row)
    genome_path = species_dir / "genome" / basename_from_url(row["genome_url"])
    if not genome_path.exists() or genome_path.stat().st_size == 0:
        return False
    for _, url in annotation_urls(row):
        path = species_dir / "annotation" / basename_from_url(url)
        if not path.exists() or path.stat().st_size == 0:
            return False
    return (species_dir / "README.md").exists() and (species_dir / "README.zh.md").exists()


def write_final_manifest(rows: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FINAL_MANIFEST_COLUMNS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_failed_downloads(rows: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FAILED_COLUMNS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=Path("planned_downloads.tsv"))
    parser.add_argument("--output-dir", type=Path, default=Path("."))
    parser.add_argument("--final-manifest", type=Path, default=Path("download_manifest.tsv"))
    parser.add_argument("--failed-downloads", type=Path, default=Path("failed_downloads.tsv"))
    parser.add_argument("--execute", action="store_true", help="download files and write species directories")
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--sleep-seconds", type=float, default=5.0)
    parser.add_argument("--limit", type=int, default=0, help="最多处理多少个 planned 行；0 表示不限制")
    parser.add_argument("--skip-completed", action="store_true", help="跳过本地文件和 README 已存在的行")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    rows = [row for row in read_manifest(args.manifest) if row.get("status") == "planned"]
    if args.skip_completed:
        rows = [row for row in rows if not row_completed(row, args.output_dir)]
    if args.limit > 0:
        rows = rows[: args.limit]
    results: list[dict[str, str]] = []
    failures: list[dict[str, str]] = []
    for index, row in enumerate(rows, start=1):
        try:
            results.append(
                process_row(
                    row=row,
                    output_dir=args.output_dir,
                    execute=args.execute,
                    retries=args.retries,
                    sleep_seconds=args.sleep_seconds,
                )
            )
        except Exception as exc:
            failures.append(
                {
                    "species": row.get("species", ""),
                    "assembly_accession": row.get("assembly_accession", ""),
                    "source": row.get("source", ""),
                    "failed_step": "process_row",
                    "url": row.get("genome_url", "") or row.get("annotation_url", ""),
                    "error": str(exc),
                    "retry_count": str(args.retries),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )
            print(f"FAILED {row.get('species', '')}: {exc}", file=sys.stderr)
        if args.execute:
            write_final_manifest(results, args.final_manifest)
            write_failed_downloads(failures, args.failed_downloads)
            print(f"Progress: {index}/{len(rows)} rows processed.", flush=True)
    if args.execute:
        write_final_manifest(results, args.final_manifest)
        write_failed_downloads(failures, args.failed_downloads)
        print(
            f"Wrote {args.final_manifest} for {len(results)} downloaded/planned rows; "
            f"{len(failures)} failures in {args.failed_downloads}."
        )
    else:
        print(f"Dry-run complete for {len(results)} planned rows. Re-run with --execute to download.")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
