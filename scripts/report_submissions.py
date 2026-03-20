#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.submission_tools import collect_submission_rows, VALID_TRACKS


SORTABLE_FIELDS = ("date", "val_loss", "val_bpb", "artifact_size_bytes", "num_runs")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Report local Parameter Golf submissions and compare their metrics."
    )
    parser.add_argument("--base-dir", default="records", help="Base directory to scan. Defaults to ./records.")
    parser.add_argument("--track", choices=VALID_TRACKS)
    parser.add_argument("--sort-by", choices=SORTABLE_FIELDS, default="val_bpb")
    parser.add_argument("--descending", action="store_true")
    parser.add_argument("--format", choices=("table", "json"), default="table")
    return parser.parse_args()


def sort_rows(rows: list[dict[str, Any]], sort_by: str, descending: bool) -> list[dict[str, Any]]:
    def key(row: dict[str, Any]) -> tuple[int, Any]:
        value = row.get(sort_by)
        return (value is None, value)

    return sorted(rows, key=key, reverse=descending)


def render_table(rows: list[dict[str, Any]]) -> str:
    headers = ["track", "date", "val_bpb", "val_loss", "size", "runs", "title"]
    table_rows = []
    for row in rows:
        table_rows.append(
            [
                str(row.get("track", "")),
                str(row.get("date", "")),
                str(row.get("val_bpb", "")),
                str(row.get("val_loss", "")),
                str(row.get("artifact_size_bytes", "")),
                str(row.get("num_runs", "")),
                str(row.get("title", "")),
            ]
        )

    widths = [len(header) for header in headers]
    for row in table_rows:
        for idx, cell in enumerate(row):
            widths[idx] = max(widths[idx], len(cell))

    lines = []
    header_line = " | ".join(header.ljust(widths[idx]) for idx, header in enumerate(headers))
    separator = "-+-".join("-" * widths[idx] for idx in range(len(headers)))
    lines.append(header_line)
    lines.append(separator)
    for row in table_rows:
        lines.append(" | ".join(cell.ljust(widths[idx]) for idx, cell in enumerate(row)))
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    rows = collect_submission_rows(Path(args.base_dir), args.track)
    rows = sort_rows(rows, args.sort_by, args.descending)

    if args.format == "json":
        print(json.dumps(rows, indent=2))
    else:
        print(render_table(rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
