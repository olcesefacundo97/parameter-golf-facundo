#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.submission_tools import validate_submission_dir


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate a local Parameter Golf submission scaffold or final submission."
    )
    parser.add_argument("path", help="Path to the submission directory to validate.")
    parser.add_argument(
        "--mode",
        choices=("draft", "submission"),
        default="submission",
        help="Draft mode allows placeholders; submission mode requires completed content.",
    )
    return parser.parse_args()


def print_report(submission_dir: Path, errors: list[str], warnings: list[str]) -> None:
    status = "PASS" if not errors else "FAIL"
    print(f"[{status}] {submission_dir}")
    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}")


def main() -> int:
    args = parse_args()
    submission_dir = Path(args.path)
    result = validate_submission_dir(submission_dir, args.mode)
    print_report(submission_dir, result.errors, result.warnings)
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
