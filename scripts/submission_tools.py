from __future__ import annotations

import json
import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

VALID_TRACKS = (
    "track_10min_16mb",
    "track_non_record_16mb",
)

TRACK_TO_JSON = {
    "track_10min_16mb": "10min_16mb",
    "track_non_record_16mb": "non_record_16mb",
}

JSON_TO_TRACK = {value: key for key, value in TRACK_TO_JSON.items()}

REQUIRED_FILES = (
    "README.md",
    "submission.json",
    "train.log",
    "train_gpt.py",
)

README_PLACEHOLDERS = (
    "Explain why this run is interesting.",
    "Describe what hypothesis you tested.",
    "Replace with the exact command used for the run.",
    "Add any caveats, failure modes, or verification notes here.",
)

TRAIN_LOG_PLACEHOLDER = "# Paste the training log for this run here."
TRAIN_SCRIPT_PLACEHOLDER = "# Copy the exact training script used for this submission here."

METRIC_PATTERNS = {
    "val_loss": (
        re.compile(r"val_loss\s*[=:]\s*([0-9]+(?:\.[0-9]+)?)"),
        re.compile(r"loss\s*[=:]\s*([0-9]+(?:\.[0-9]+)?)"),
    ),
    "val_bpb": (
        re.compile(r"val_bpb\s*[=:]\s*([0-9]+(?:\.[0-9]+)?)"),
        re.compile(r"bpb\s*[=:]\s*([0-9]+(?:\.[0-9]+)?)"),
    ),
    "bytes_total": (
        re.compile(r"bytes_total\s*[=:]\s*([0-9]+)"),
        re.compile(r"artifact_size_bytes\s*[=:]\s*([0-9]+)"),
        re.compile(r"artifact_bytes\s*[=:]\s*([0-9]+)"),
        re.compile(r"compressed(?:\s+artifact)?\s+size(?:\s+bytes)?\s*[=:]\s*([0-9]+)", re.IGNORECASE),
        re.compile(r"size_bytes\s*[=:]\s*([0-9]+)"),
    ),
    "bytes_code": (
        re.compile(r"bytes_code\s*[=:]\s*([0-9]+)"),
        re.compile(r"code_bytes\s*[=:]\s*([0-9]+)"),
    ),
    "bytes_model_int8_zlib": (
        re.compile(r"bytes_model_int8_zlib\s*[=:]\s*([0-9]+)"),
    ),
    "num_runs": (
        re.compile(r"num_runs\s*[=:]\s*([0-9]+)"),
        re.compile(r"runs\s*[=:]\s*([0-9]+)"),
    ),
    "p_value": (
        re.compile(r"p_value\s*[=:]\s*([0-9]+(?:\.[0-9]+)?)"),
    ),
}


@dataclass
class ValidationResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def add(self, message: str, *, error: bool) -> None:
        if error:
            self.errors.append(message)
        else:
            self.warnings.append(message)

    @property
    def ok(self) -> bool:
        return not self.errors


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_") or "submission"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_submission_json(path: Path) -> dict[str, Any]:
    return json.loads(read_text(path))


def write_submission_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def infer_track_dir(payload: dict[str, Any], submission_dir: Path | None = None) -> str | None:
    raw_track = payload.get("track")
    if raw_track in VALID_TRACKS:
        return raw_track
    if raw_track in JSON_TO_TRACK:
        return JSON_TO_TRACK[raw_track]
    if submission_dir and submission_dir.parent.name in VALID_TRACKS:
        return submission_dir.parent.name
    return None


def infer_json_track(payload: dict[str, Any], submission_dir: Path | None = None) -> str | None:
    raw_track = payload.get("track")
    if raw_track in JSON_TO_TRACK:
        return raw_track
    if raw_track in VALID_TRACKS:
        return TRACK_TO_JSON[raw_track]
    track_dir = infer_track_dir(payload, submission_dir)
    if track_dir:
        return TRACK_TO_JSON[track_dir]
    return None


def get_submission_field(payload: dict[str, Any], field: str) -> Any:
    metrics = payload.get("metrics", {})
    if field == "name":
        return payload.get("name") or payload.get("title")
    if field == "author":
        author = payload.get("author")
        if isinstance(author, dict):
            return author.get("name")
        return author
    if field == "github_id":
        author = payload.get("author")
        if isinstance(author, dict) and author.get("github"):
            return author.get("github")
        return payload.get("github_id")
    if field == "blurb":
        return payload.get("blurb") or payload.get("summary")
    if field == "val_loss":
        return payload.get("mean_val_loss", payload.get("val_loss", metrics.get("val_loss")))
    if field == "val_bpb":
        return payload.get("mean_val_bpb", payload.get("val_bpb", metrics.get("val_bpb")))
    if field == "bytes_total":
        return payload.get("bytes_total", payload.get("artifact_bytes", metrics.get("artifact_size_bytes")))
    if field == "bytes_code":
        return payload.get("bytes_code", payload.get("code_bytes"))
    return payload.get(field)


def extract_metrics_from_text(text: str) -> dict[str, float | int]:
    extracted: dict[str, float | int] = {}
    for metric_name, patterns in METRIC_PATTERNS.items():
        matches: list[str] = []
        for pattern in patterns:
            matches.extend(pattern.findall(text))
        if matches:
            raw_value = matches[-1]
            if metric_name in {"bytes_total", "bytes_code", "bytes_model_int8_zlib", "num_runs"}:
                extracted[metric_name] = int(raw_value)
            else:
                extracted[metric_name] = float(raw_value)
    return extracted


def add_issue(result: ValidationResult, message: str, mode: str) -> None:
    result.add(message, error=(mode == "submission"))


def validate_structure(submission_dir: Path, result: ValidationResult) -> None:
    if not submission_dir.exists():
        result.add(f"Directory does not exist: {submission_dir}", error=True)
        return
    if not submission_dir.is_dir():
        result.add(f"Path is not a directory: {submission_dir}", error=True)
        return
    for filename in REQUIRED_FILES:
        if not (submission_dir / filename).exists():
            result.add(f"Missing required file: {filename}", error=True)


def validate_metadata(submission_dir: Path, result: ValidationResult, mode: str) -> None:
    json_path = submission_dir / "submission.json"
    if not json_path.exists():
        return

    try:
        payload = json.loads(read_text(json_path))
    except json.JSONDecodeError as exc:
        result.add(f"Invalid JSON in submission.json: {exc}", error=True)
        return

    for key in ("name", "author", "github_id", "date", "blurb"):
        if key == "date":
            if not str(payload.get("date", "")).strip():
                add_issue(result, "submission.json date is empty.", mode)
            continue
        if not str(get_submission_field(payload, key) or "").strip():
            add_issue(result, f"submission.json {key} is empty.", mode)

    track_dir = infer_track_dir(payload, submission_dir)
    json_track = infer_json_track(payload, submission_dir)
    if track_dir is None:
        allowed_tracks = sorted([*VALID_TRACKS, *JSON_TO_TRACK.keys()])
        result.add(
            f"submission.json track must map to one of: {', '.join(allowed_tracks)}",
            error=True,
        )

    for metric_name in ("val_loss", "val_bpb", "bytes_total", "bytes_code"):
        if get_submission_field(payload, metric_name) is None:
            add_issue(result, f"submission.json {metric_name} is null or missing.", mode)

    expected_track = submission_dir.parent.name
    if track_dir and expected_track in VALID_TRACKS and track_dir != expected_track:
        result.add(
            f"submission.json track '{json_track or track_dir}' does not match parent directory '{expected_track}'.",
            error=True,
        )

    expected_date_prefix = submission_dir.name.split("_", 1)[0]
    json_date = str(payload.get("date", ""))
    if json_date:
        normalized_json_date = json_date.split("T", 1)[0]
        if expected_date_prefix != normalized_json_date:
            add_issue(
                result,
                f"submission.json date '{json_date}' does not match directory prefix '{expected_date_prefix}'.",
                mode,
            )

    seed_results = payload.get("seed_results")
    if seed_results is not None and not isinstance(seed_results, dict):
        add_issue(
            result,
            "submission.json seed_results must be an object when provided.",
            mode,
        )


def validate_content(submission_dir: Path, result: ValidationResult, mode: str) -> None:
    readme_path = submission_dir / "README.md"
    if readme_path.exists():
        readme = read_text(readme_path)
        for placeholder in README_PLACEHOLDERS:
            if placeholder in readme:
                add_issue(result, f"README.md still contains placeholder text: {placeholder}", mode)

    train_log_path = submission_dir / "train.log"
    if train_log_path.exists() and read_text(train_log_path).strip() == TRAIN_LOG_PLACEHOLDER:
        add_issue(result, "train.log still contains the placeholder stub.", mode)

    train_script_path = submission_dir / "train_gpt.py"
    if train_script_path.exists() and read_text(train_script_path).strip() == TRAIN_SCRIPT_PLACEHOLDER:
        add_issue(result, "train_gpt.py still contains the placeholder stub.", mode)


def validate_submission_dir(submission_dir: Path, mode: str) -> ValidationResult:
    result = ValidationResult()
    validate_structure(submission_dir, result)
    if result.errors:
        return result
    validate_metadata(submission_dir, result, mode)
    validate_content(submission_dir, result, mode)
    return result



def collect_submission_rows(base_dir: Path, track: str | None = None) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not base_dir.exists():
        return rows

    for json_path in sorted(base_dir.glob("*/**/submission.json")):
        submission_dir = json_path.parent
        payload = read_submission_json(json_path)
        row_track = infer_track_dir(payload, submission_dir) or submission_dir.parent.name
        if track and row_track != track:
            continue
        rows.append(
            {
                "path": str(submission_dir),
                "track": row_track,
                "date": payload.get("date"),
                "title": get_submission_field(payload, "name"),
                "summary": get_submission_field(payload, "blurb"),
                "author": get_submission_field(payload, "author"),
                "github_id": get_submission_field(payload, "github_id"),
                "val_loss": get_submission_field(payload, "val_loss"),
                "val_bpb": get_submission_field(payload, "val_bpb"),
                "artifact_size_bytes": get_submission_field(payload, "bytes_total"),
                "bytes_code": get_submission_field(payload, "bytes_code"),
                "num_runs": payload.get("num_runs")
                or payload.get("metrics", {}).get("num_runs")
                or (len(payload.get("seed_results", {})) or None),
            }
        )
    return rows

def export_submission(
    submission_dir: Path,
    upstream_repo: Path,
    *,
    mode: str,
    force: bool,
) -> Path:
    result = validate_submission_dir(submission_dir, mode)
    if not result.ok:
        joined = "\n".join(result.errors + result.warnings)
        raise ValueError(f"Submission did not pass validation:\n{joined}")

    payload = read_submission_json(submission_dir / "submission.json")
    track = infer_track_dir(payload, submission_dir)
    if track is None:
        raise ValueError("Could not determine submission track from submission.json or directory structure.")
    records_dir = upstream_repo / "records"
    if not records_dir.exists():
        raise ValueError(f"Upstream repo does not look valid (missing records/): {upstream_repo}")

    target_dir = records_dir / track / submission_dir.name
    if target_dir.exists():
        if not force:
            raise ValueError(f"Destination already exists: {target_dir}")
        shutil.rmtree(target_dir)

    shutil.copytree(submission_dir, target_dir)
    return target_dir
