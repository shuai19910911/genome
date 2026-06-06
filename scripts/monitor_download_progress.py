#!/usr/bin/env python3
"""Print a concise progress snapshot for the genome download job."""

from __future__ import annotations

import glob
import json
import subprocess
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "download.monitor.state.json"


def count_data_rows(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open() as handle:
        lines = sum(1 for _ in handle)
    return max(0, lines - 1)


def command_lines(pattern: str) -> list[str]:
    result = subprocess.run(["pgrep", "-af", pattern], text=True, capture_output=True, check=False)
    return [line for line in result.stdout.splitlines() if line.strip()]


def downloaded_bytes() -> int:
    total = 0
    for directory in ROOT.glob("*_GC[AF]_*"):
        if not directory.is_dir():
            continue
        for path in directory.rglob("*"):
            if path.is_file():
                total += path.stat().st_size
    return total


def part_file_stats() -> dict[str, int]:
    stats: dict[str, int] = {}
    for filename in glob.glob(str(ROOT / "*_GC[AF]_*" / "genome" / "*.part")):
        path = Path(filename)
        stats[str(path.relative_to(ROOT))] = path.stat().st_size
    return stats


def load_state() -> dict[str, object]:
    if not STATE_PATH.exists():
        return {}
    try:
        return json.loads(STATE_PATH.read_text())
    except json.JSONDecodeError:
        return {}


def mib_per_second(byte_delta: int, second_delta: float) -> float:
    if second_delta <= 0:
        return 0.0
    return byte_delta / second_delta / 1024 / 1024


def main() -> int:
    now = datetime.now()
    now_ts = now.timestamp()
    print("=" * 80)
    print(f"检查时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")

    manifests = sorted(ROOT.glob("download_manifest.shard*.tsv"))
    failures = sorted(ROOT.glob("failed_downloads.shard*.tsv"))
    completed = sum(count_data_rows(path) for path in manifests)
    failed = sum(count_data_rows(path) for path in failures)
    dirs = len([path for path in ROOT.glob("*_GC[AF]_*") if path.is_dir()])
    total_bytes = downloaded_bytes()
    parts = part_file_stats()
    state = load_state()

    print(f"已写入完成记录: {completed}")
    print(f"已写入失败记录: {failed}")
    print(f"已生成物种/assembly目录数: {dirs}")
    print(f"本地数据总字节数: {total_bytes}")

    previous_time = float(state.get("timestamp", 0) or 0)
    previous_bytes = int(state.get("downloaded_bytes", total_bytes) or total_bytes)
    if previous_time > 0:
        elapsed = now_ts - previous_time
        delta = max(0, total_bytes - previous_bytes)
        print(f"距上次检查秒数: {elapsed:.0f}")
        print(f"距上次新增字节数: {delta}")
        print(f"距上次平均速度 MiB/s: {mib_per_second(delta, elapsed):.2f}")
    else:
        print("距上次平均速度 MiB/s: NA")

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
    previous_parts = state.get("parts", {})
    for filename in part_files[:12]:
        path = Path(filename)
        stat = path.stat()
        rel = path.relative_to(ROOT)
        speed_text = "NA"
        if isinstance(previous_parts, dict) and previous_time > 0:
            old_size = int(previous_parts.get(str(rel), stat.st_size) or stat.st_size)
            speed_text = f"{mib_per_second(max(0, stat.st_size - old_size), now_ts - previous_time):.2f}"
        print(f"part: {rel}\t{stat.st_size}\t{datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')}\tMiB/s_since_last={speed_text}")
    STATE_PATH.write_text(
        json.dumps(
            {
                "timestamp": now_ts,
                "downloaded_bytes": total_bytes,
                "parts": parts,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
