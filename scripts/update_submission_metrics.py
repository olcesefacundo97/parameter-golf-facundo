#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.submission_tools import extract_metrics_from_text, read_submission_json, write_submission_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Update submission.json metrics from explicit values and/or a train.log file."
    )
    parser.add_argument("path", help="Path to the submission directory.")
    parser.add_argument("--train-log", help="Optional path to a log file. Defaults to <path>/train.log.")
    parser.add_argument("--val-loss", type=float)
    parser.add_argument("--val-bpb", type=float)
    parser.add_argument("--artifact-size-bytes", type=int)
    parser.add_argument("--num-runs", type=int)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the resulting metrics without writing submission.json.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    submission_dir = Path(args.path)
    submission_json_path = submission_dir / "submission.json"
    train_log_path = Path(args.train_log) if args.train_log else submission_dir / "train.log"

    payload = read_submission_json(submission_json_path)
    metrics = dict(payload.get("metrics", {}))

    if train_log_path.exists():
        parsed_metrics = extract_metrics_from_text(train_log_path.read_text(encoding="utf-8"))
        metrics.update(parsed_metrics)

    overrides = {
        "val_loss": args.val_loss,
        "val_bpb": args.val_bpb,
        "artifact_size_bytes": args.artifact_size_bytes,
        "num_runs": args.num_runs,
    }
    for key, value in overrides.items():
        if value is not None:
            metrics[key] = value

    payload["metrics"] = metrics

    if args.dry_run:
        for key in ("val_loss", "val_bpb", "artifact_size_bytes", "num_runs"):
            print(f"{key}={metrics.get(key)}")
        return 0

    write_submission_json(submission_json_path, payload)
    for key in ("val_loss", "val_bpb", "artifact_size_bytes", "num_runs"):
        print(f"{key}={metrics.get(key)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
