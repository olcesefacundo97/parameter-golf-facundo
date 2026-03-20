#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.submission_tools import slugify, VALID_TRACKS


def build_readme(title: str, summary: str, template_path: Path) -> str:
    template = template_path.read_text(encoding="utf-8")
    return template.format(title=title, summary=summary)


def build_submission_json(
    title: str,
    author_name: str,
    github_id: str,
    track: str,
    summary: str,
    run_date: str,
) -> dict:
    return {
        "title": title,
        "author": {
            "name": author_name,
            "github": github_id,
        },
        "track": track,
        "date": run_date,
        "summary": summary,
        "metrics": {
            "val_loss": None,
            "val_bpb": None,
            "artifact_size_bytes": None,
            "num_runs": None,
        },
        "artifacts": {
            "train_log": "train.log",
            "train_script": "train_gpt.py",
            "extra_files": [],
        },
        "notes": [
            "Fill in all placeholders before opening a PR against the official repo.",
            "Include enough evidence to support statistical significance when claiming a new record.",
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a local submission folder scaffold compatible with Parameter Golf records."
    )
    parser.add_argument("--track", choices=VALID_TRACKS, default="track_non_record_16mb")
    parser.add_argument("--slug", required=True, help="Short identifier for the run.")
    parser.add_argument("--author-name", required=True)
    parser.add_argument("--github-id", required=True)
    parser.add_argument("--summary", required=True, help="One-line summary of the approach.")
    parser.add_argument(
        "--date",
        default=dt.date.today().isoformat(),
        help="Run date in YYYY-MM-DD format. Defaults to today.",
    )
    parser.add_argument(
        "--base-dir",
        default="records",
        help="Base directory where the records tree will be created.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    template_path = repo_root / "templates" / "submission" / "README.md.tmpl"

    slug = slugify(args.slug)
    folder_name = f"{args.date}_{slug}"
    submission_dir = Path(args.base_dir) / args.track / folder_name
    submission_dir.mkdir(parents=True, exist_ok=False)

    title = f"{args.date} / {slug.replace('_', ' ')}"

    readme_text = build_readme(title=title, summary=args.summary, template_path=template_path)
    (submission_dir / "README.md").write_text(readme_text, encoding="utf-8")

    submission_payload = build_submission_json(
        title=title,
        author_name=args.author_name,
        github_id=args.github_id,
        track=args.track,
        summary=args.summary,
        run_date=args.date,
    )
    (submission_dir / "submission.json").write_text(
        json.dumps(submission_payload, indent=2) + "\n",
        encoding="utf-8",
    )

    (submission_dir / "train.log").write_text(
        "# Paste the training log for this run here.\n",
        encoding="utf-8",
    )
    (submission_dir / "train_gpt.py").write_text(
        "# Copy the exact training script used for this submission here.\n",
        encoding="utf-8",
    )
    (submission_dir / ".gitignore").write_text(
        "__pycache__/\n*.pyc\n",
        encoding="utf-8",
    )

    print(submission_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
