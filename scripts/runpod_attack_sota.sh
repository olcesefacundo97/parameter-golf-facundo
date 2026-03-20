#!/usr/bin/env bash
set -euo pipefail

WORKSPACE_DIR="/workspace"
REPO_DIR="$WORKSPACE_DIR/parameter-golf-facundo"
UPSTREAM_DIR="$REPO_DIR/upstream/parameter-golf"
REPO_URL="https://github.com/olcesefacundo97/parameter-golf-facundo.git"
AUTHOR_NAME="Facundo Olcese"
GITHUB_ID="olcesefacundo97"
SLUG="attack-sota-seed1"
SUMMARY="Starter run from current public SOTA script"
TRAIN_SHARDS=1
SKIP_DATASET=0

usage() {
  cat <<'USAGE'
Usage: ./scripts/runpod_attack_sota.sh [options]

Options:
  --workspace-dir PATH   Base workspace directory on the remote machine (default: /workspace)
  --repo-url URL         Git URL for your wrapper repo
  --author-name NAME     Author name to write in the local submission
  --github-id ID         GitHub handle to write in the local submission
  --slug SLUG            Slug for the local run folder
  --summary TEXT         Summary for the local submission
  --train-shards N       FineWeb train shards to download for local iteration (default: 1)
  --skip-dataset         Skip dataset/tokenizer download if already present
  -h, --help             Show this help
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --workspace-dir)
      WORKSPACE_DIR="$2"
      shift 2
      ;;
    --repo-url)
      REPO_URL="$2"
      shift 2
      ;;
    --author-name)
      AUTHOR_NAME="$2"
      shift 2
      ;;
    --github-id)
      GITHUB_ID="$2"
      shift 2
      ;;
    --slug)
      SLUG="$2"
      shift 2
      ;;
    --summary)
      SUMMARY="$2"
      shift 2
      ;;
    --train-shards)
      TRAIN_SHARDS="$2"
      shift 2
      ;;
    --skip-dataset)
      SKIP_DATASET=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

REPO_DIR="$WORKSPACE_DIR/parameter-golf-facundo"
UPSTREAM_DIR="$REPO_DIR/upstream/parameter-golf"

mkdir -p "$WORKSPACE_DIR"
cd "$WORKSPACE_DIR"

if [[ -d "$REPO_DIR/.git" ]]; then
  echo "[runpod] Updating wrapper repo at $REPO_DIR"
  git -C "$REPO_DIR" pull --ff-only
else
  echo "[runpod] Cloning wrapper repo to $REPO_DIR"
  git clone "$REPO_URL" "$REPO_DIR"
fi

if [[ -d "$UPSTREAM_DIR/.git" ]]; then
  echo "[runpod] Updating upstream repo at $UPSTREAM_DIR"
  git -C "$UPSTREAM_DIR" pull --ff-only
else
  echo "[runpod] Cloning upstream repo to $UPSTREAM_DIR"
  mkdir -p "$(dirname "$UPSTREAM_DIR")"
  git clone https://github.com/openai/parameter-golf.git "$UPSTREAM_DIR"
fi

cd "$UPSTREAM_DIR"

if [[ "$SKIP_DATASET" -eq 0 ]]; then
  echo "[runpod] Downloading FineWeb cache (train_shards=$TRAIN_SHARDS)"
  python3 data/cached_challenge_fineweb.py --variant sp1024 --train-shards "$TRAIN_SHARDS"
fi

cd "$REPO_DIR"

echo "[runpod] Launching attack-sota starter campaign"
python3 scripts/run_campaign.py \
  --campaign campaigns/attack_sota_record_starter.env \
  --upstream-repo "$UPSTREAM_DIR" \
  --slug "$SLUG" \
  --author-name "$AUTHOR_NAME" \
  --github-id "$GITHUB_ID" \
  --summary "$SUMMARY"
