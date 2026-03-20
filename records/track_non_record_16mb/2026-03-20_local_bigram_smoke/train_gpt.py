#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import os
from collections import Counter, defaultdict
from pathlib import Path

CORPUS = """
parameter golf rewards compact, clever language modeling systems.
small models can still be useful when the inductive bias is strong.
context length, evaluation tricks, weight sharing and adaptation matter.
we want honest local smoke tests before scaling to expensive hardware.
""".strip().lower()


def build_bigram_model(tokens: list[str]) -> dict[str, dict[str, int]]:
    counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for left, right in zip(tokens, tokens[1:]):
        counts[left][right] += 1
    return {left: dict(rights) for left, rights in counts.items()}


def nll_bits_per_token(model: dict[str, dict[str, int]], train_vocab: set[str], tokens: list[str]) -> tuple[float, float]:
    vocab = sorted(train_vocab | set(tokens))
    vocab_size = max(len(vocab), 1)
    total_nll_nat = 0.0
    steps = 0
    for left, right in zip(tokens, tokens[1:]):
        row = model.get(left, {})
        total = sum(row.values())
        prob = (row.get(right, 0) + 1) / (total + vocab_size)
        total_nll_nat += -math.log(prob)
        steps += 1
    avg_loss = total_nll_nat / max(steps, 1)
    bpb = avg_loss / math.log(2)
    return avg_loss, bpb


def main() -> int:
    tokens = CORPUS.split()
    split = max(8, int(len(tokens) * 0.7))
    train_tokens = tokens[:split]
    val_tokens = tokens[split - 1 :]

    model = build_bigram_model(train_tokens)
    val_loss, val_bpb = nll_bits_per_token(model, set(train_tokens), val_tokens)

    submission_dir = Path(os.environ.get("SUBMISSION_DIR", "."))
    artifact_path = submission_dir / "local_bigram_artifact.json"
    artifact_payload = {
        "model": model,
        "train_token_count": len(train_tokens),
        "val_token_count": len(val_tokens),
        "description": "Deterministic local bigram smoke baseline.",
    }
    artifact_path.write_text(json.dumps(artifact_payload, indent=2) + "\n", encoding="utf-8")
    artifact_size_bytes = artifact_path.stat().st_size

    print(f"train_tokens={len(train_tokens)}")
    print(f"val_tokens={len(val_tokens)}")
    print(f"artifact_path={artifact_path}")
    print(f"val_loss={val_loss:.6f}")
    print(f"val_bpb={val_bpb:.6f}")
    print(f"artifact_size_bytes={artifact_size_bytes}")
    print("num_runs=1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
