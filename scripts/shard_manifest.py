#!/usr/bin/env python3
"""Split a TSV manifest into stable row-number shards."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=Path("planned_downloads.tsv"))
    parser.add_argument("--out-dir", type=Path, default=Path("shards"))
    parser.add_argument("--shards", type=int, default=4)
    parser.add_argument("--skip-first", type=int, default=0, help="跳过前 N 条数据行，不含表头")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.shards < 1:
        raise ValueError("--shards must be >= 1")
    args.out_dir.mkdir(parents=True, exist_ok=True)

    with args.manifest.open(newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if not reader.fieldnames:
            raise ValueError(f"{args.manifest} has no header")
        rows = [row for index, row in enumerate(reader) if index >= args.skip_first]

    writers: list[tuple[object, csv.DictWriter]] = []
    try:
        for shard_index in range(args.shards):
            path = args.out_dir / f"planned_downloads.shard{shard_index + 1:02d}.tsv"
            handle = path.open("w", newline="")
            writer = csv.DictWriter(handle, fieldnames=reader.fieldnames, delimiter="\t", lineterminator="\n")
            writer.writeheader()
            writers.append((handle, writer))

        counts = [0] * args.shards
        for row_index, row in enumerate(rows):
            shard_index = row_index % args.shards
            writers[shard_index][1].writerow(row)
            counts[shard_index] += 1
    finally:
        for handle, _ in writers:
            handle.close()

    for shard_index, count in enumerate(counts, start=1):
        print(f"shard{shard_index:02d}: {count} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
