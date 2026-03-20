#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.submission_tools import export_submission


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export a validated local submission into a local clone of the official Parameter Golf repo."
    )
    parser.add_argument("submission_path", help="Path to the local submission directory.")
    parser.add_argument("upstream_repo", help="Path to a local clone of openai/parameter-golf.")
    parser.add_argument(
        "--mode",
        choices=("draft", "submission"),
        default="submission",
        help="Validation mode to enforce before exporting.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite the destination directory if it already exists.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    target_dir = export_submission(
        Path(args.submission_path),
        Path(args.upstream_repo),
        mode=args.mode,
        force=args.force,
    )
    print(target_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
