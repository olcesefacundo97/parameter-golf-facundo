#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Launch a campaign preset against a local clone of the official Parameter Golf repo."
    )
    parser.add_argument("--campaign", required=True, help="Path to a .env campaign preset.")
    parser.add_argument("--upstream-repo", required=True, help="Path to a local clone of openai/parameter-golf.")
    parser.add_argument("--slug", required=True)
    parser.add_argument("--author-name", required=True)
    parser.add_argument("--github-id", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--track", default="track_non_record_16mb")
    parser.add_argument("--base-dir", default="records")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def parse_env_file(path: Path) -> tuple[dict[str, str], list[str]]:
    env_vars: dict[str, str] = {}
    command: list[str] | None = None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        key, value = line.split("=", 1)
        if key == "COMMAND":
            command = shlex.split(value)
        else:
            env_vars[key] = value
    if command is None:
        raise SystemExit(f"Campaign file is missing COMMAND=: {path}")
    return env_vars, command


def main() -> int:
    args = parse_args()
    campaign_path = Path(args.campaign)
    upstream_repo = Path(args.upstream_repo)
    env_vars, command = parse_env_file(campaign_path)

    full_command = ["env"] + [f"{key}={value}" for key, value in env_vars.items()] + command
    run_cmd = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "run_submission.py"),
        "--track",
        args.track,
        "--slug",
        args.slug,
        "--author-name",
        args.author_name,
        "--github-id",
        args.github_id,
        "--summary",
        args.summary,
        "--base-dir",
        args.base_dir,
        "--workdir",
        str(upstream_repo),
        "--train-script",
        str(upstream_repo / "train_gpt.py"),
        "--",
        *full_command,
    ]

    if args.dry_run:
        print(shlex.join(run_cmd))
        return 0

    completed = subprocess.run(run_cmd, cwd=REPO_ROOT, text=True, check=False)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
