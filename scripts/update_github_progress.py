#!/usr/bin/env python3
"""Write a Chinese progress snapshot for GitHub."""

from __future__ import annotations

import json
import subprocess
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "current-download-status.md"
STATE = ROOT / "download.monitor.state.json"
MONITOR_LOG = ROOT / "download.monitor.log"


def count_data_rows(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open() as handle:
        return max(0, sum(1 for _ in handle) - 1)


def command_lines(pattern: str) -> list[str]:
    result = subprocess.run(["pgrep", "-af", pattern], text=True, capture_output=True, check=False)
    return [line for line in result.stdout.splitlines() if line.strip()]


def load_state() -> dict[str, object]:
    if not STATE.exists():
        return {}
    try:
        return json.loads(STATE.read_text())
    except json.JSONDecodeError:
        return {}


def format_bytes(value: int) -> str:
    gib = value / 1024 / 1024 / 1024
    return f"{value} bytes ({gib:.2f} GiB)"


def latest_speed_line() -> str:
    if not MONITOR_LOG.exists():
        return "暂无；等待自动监控生成速度基准。"
    for line in reversed(MONITOR_LOG.read_text(errors="replace").splitlines()):
        if line.startswith("距上次平均速度 MiB/s:"):
            value = line.split(":", 1)[1].strip()
            return f"{value} MiB/s"
    return "暂无；等待自动监控生成速度基准。"


def main() -> int:
    now = datetime.now()
    manifests = sorted(ROOT.glob("download_manifest.shard*.tsv"))
    failures = sorted(ROOT.glob("failed_downloads.shard*.tsv"))
    completed = sum(count_data_rows(path) for path in manifests)
    failed = sum(count_data_rows(path) for path in failures)
    dirs = len([path for path in ROOT.glob("*_GC[AF]_*") if path.is_dir()])
    readmes = len(list(ROOT.glob("*_GC[AF]_*" + "/README.md")))
    aria2 = command_lines("aria2c")
    managers = command_lines("download_from_manifest")
    state = load_state()
    total_bytes = int(state.get("downloaded_bytes", 0) or 0)

    speed_line = latest_speed_line()

    lines = [
        "# 当前基因组下载进展",
        "",
        f"- 更新时间: {now.strftime('%Y-%m-%d %H:%M:%S')}",
        f"- 完成记录数: {completed}",
        f"- 失败记录数: {failed}",
        f"- 已生成 assembly 目录数: {dirs}",
        f"- 已生成 README 的完成目录数: {readmes}",
        f"- 本地数据总量: {format_bytes(total_bytes) if total_bytes else '暂无统计'}",
        f"- 下载管理进程数: {len(managers)}",
        f"- aria2 活动下载数: {len(aria2)}",
        f"- 最近速度: {speed_line}",
        "",
        "## 各 shard 进展",
        "",
    ]
    for path in manifests:
        lines.append(f"- {path.name}: 完成 {count_data_rows(path)}")
    for path in failures:
        lines.append(f"- {path.name}: 失败 {count_data_rows(path)}")

    lines.extend(["", "## 当前活动下载", ""])
    if aria2:
        for line in aria2[:12]:
            lines.append(f"- `{line}`")
    else:
        lines.append("- 当前没有 aria2 活动下载。")

    lines.extend(
        [
            "",
            "## 说明",
            "",
            "- 失败记录主要来自 NCBI GenBank (`GCA`) 条目缺少 GFF/GTF 注释文件，脚本会快速跳过并记录失败。",
            "- 没有 README 的目录多为下载中或注释缺失失败后留下的未完成目录，本轮下载结束后再统一清理或补充失败说明。",
            "- 大文件和运行日志不提交到 GitHub；GitHub 只记录脚本、清单和进度文档。",
            "",
        ]
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines))
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
