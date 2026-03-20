#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a local submission scaffold, run a command, capture train.log, and sync metrics."
    )
    parser.add_argument("--track", default="track_non_record_16mb")
    parser.add_argument("--slug", required=True)
    parser.add_argument("--author-name", required=True)
    parser.add_argument("--github-id", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--base-dir", default="records")
    parser.add_argument("--workdir", default=".")
    parser.add_argument("--train-script", help="Optional path to the training script to copy into the scaffold.")
    parser.add_argument(
        "--env",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="Environment variable to inject into the child command. Repeat as needed.",
    )
    parser.add_argument(
        "--no-update-metrics",
        action="store_true",
        help="Skip automatic metric extraction after the command finishes.",
    )
    parser.add_argument(
        "command",
        nargs=argparse.REMAINDER,
        help="Command to execute. Prefix it with --, e.g. -- python3 train_gpt.py",
    )
    return parser.parse_args()


def create_submission(args: argparse.Namespace) -> Path:
    init_cmd = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "init_submission.py"),
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
    ]
    created = subprocess.run(init_cmd, text=True, capture_output=True, cwd=REPO_ROOT, check=False)
    if created.returncode != 0:
        raise SystemExit(created.stderr or created.stdout)
    return Path(created.stdout.strip())


def parse_env_overrides(values: list[str]) -> dict[str, str]:
    env_updates: dict[str, str] = {}
    for value in values:
        key, sep, raw = value.partition("=")
        if not sep or not key:
            raise SystemExit(f"Invalid --env value '{value}'. Expected KEY=VALUE.")
        env_updates[key] = raw
    return env_updates


def update_readme_command(submission_dir: Path, command: list[str], env_updates: dict[str, str]) -> None:
    readme_path = submission_dir / "README.md"
    readme = readme_path.read_text(encoding="utf-8")
    env_prefix = " ".join(f"{key}={shlex.quote(value)}" for key, value in env_updates.items())
    command_text = shlex.join(command)
    if env_prefix:
        command_text = f"{env_prefix} {command_text}"
    readme = readme.replace("# Replace with the exact command used for the run.", command_text)
    readme_path.write_text(readme, encoding="utf-8")


def copy_train_script(submission_dir: Path, train_script: str | None) -> None:
    if not train_script:
        return
    source = Path(train_script)
    shutil.copyfile(source, submission_dir / "train_gpt.py")


def run_and_capture(
    submission_dir: Path,
    command: list[str],
    workdir: str,
    env_updates: dict[str, str],
) -> int:
    log_path = submission_dir / "train.log"
    child_env = dict(os.environ)
    child_env["SUBMISSION_DIR"] = str(submission_dir.resolve())
    child_env["TRAIN_LOG_PATH"] = str(log_path.resolve())
    child_env.update(env_updates)
    with log_path.open("w", encoding="utf-8") as log_file:
        process = subprocess.Popen(
            command,
            cwd=workdir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            env=child_env,
        )
        assert process.stdout is not None
        for line in process.stdout:
            print(line, end="")
            log_file.write(line)
        return process.wait()


def update_metrics(submission_dir: Path) -> None:
    update_cmd = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "update_submission_metrics.py"),
        str(submission_dir),
    ]
    updated = subprocess.run(update_cmd, text=True, capture_output=True, cwd=REPO_ROOT, check=False)
    if updated.returncode != 0:
        raise SystemExit(updated.stderr or updated.stdout)
    print(updated.stdout, end="")


def main() -> int:
    args = parse_args()
    command = args.command[1:] if args.command and args.command[0] == "--" else args.command
    if not command:
        raise SystemExit("You must provide a command after --, e.g. -- python3 train_gpt.py")
    env_updates = parse_env_overrides(args.env)

    submission_dir = create_submission(args)
    copy_train_script(submission_dir, args.train_script)
    update_readme_command(submission_dir, command, env_updates)
    exit_code = run_and_capture(submission_dir, command, args.workdir, env_updates)
    if exit_code == 0 and not args.no_update_metrics:
        update_metrics(submission_dir)
    print(submission_dir)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
