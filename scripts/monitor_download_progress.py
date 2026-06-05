#!/usr/bin/env python3
"""Print a concise progress snapshot for the genome download job."""

from __future__ import annotations

import glob
import subprocess
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def count_data_rows(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open() as handle:
        lines = sum(1 for _ in handle)
    return max(0, lines - 1)


def command_lines(pattern: str) -> list[str]:
    result = subprocess.run(["pgrep", "-af", pattern], text=True, capture_output=True, check=False)
    return [line for line in result.stdout.splitlines() if line.strip()]


def main() -> int:
    print("=" * 80)
    print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    manifests = sorted(ROOT.glob("download_manifest.shard*.tsv"))
    failures = sorted(ROOT.glob("failed_downloads.shard*.tsv"))
    completed = sum(count_data_rows(path) for path in manifests)
    failed = sum(count_data_rows(path) for path in failures)
    dirs = len([path for path in ROOT.glob("*_GC[AF]_*") if path.is_dir()])

    print(f"已写入完成记录: {completed}")
    print(f"已写入失败记录: {failed}")
    print(f"已生成物种/assembly目录数: {dirs}")

    for path in manifests:
        print(f"{path.name}: 完成 {count_data_rows(path)}")
    for path in failures:
        print(f"{path.name}: 失败 {count_data_rows(path)}")

    managers = command_lines("download_from_manifest")
    aria2 = command_lines("aria2c")
    print(f"下载管理进程数: {len(managers)}")
    print(f"aria2活动下载数: {len(aria2)}")
    for line in aria2[:12]:
        print(f"aria2: {line}")

    part_files = sorted(glob.glob(str(ROOT / "*_GC[AF]_*" / "genome" / "*.part")), key=lambda p: Path(p).stat().st_mtime, reverse=True)
    for filename in part_files[:12]:
        path = Path(filename)
        stat = path.stat()
        rel = path.relative_to(ROOT)
        print(f"part: {rel}\t{stat.st_size}\t{datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
