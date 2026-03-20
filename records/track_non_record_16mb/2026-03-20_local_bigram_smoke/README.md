# 2026-03-20 / local bigram smoke

## Summary

Deterministic local bigram smoke baseline executed in this environment.

## Motivation

- This run proves the local workflow end to end with a real executed command and real generated artifacts.
- The hypothesis is not that this model is competitive, but that the repo can now produce an honest non-record submission bundle without fabricating metrics.
- This is explicitly a non-record / exploratory track run.

## Changes vs baseline

- Architecture changes: replaced the full competition model with a deterministic word-level bigram baseline for smoke validation.
- Tokenizer / data changes: tiny embedded text corpus inside the script instead of FineWeb.
- Training / optimizer / schedule changes: no gradient training; bigram counts are estimated directly from the train split.
- Evaluation changes: held-out token negative log-likelihood converted to `val_bpb`.

## Reproduction

### Environment

- Hardware: CPU-only local environment.
- Software: Python 3 standard library only.
- Commit / revision: local repo state when this submission was generated.

### Command

```bash
python3 experiments/local_smoke_train.py
```

## Results

- `val_loss`: `3.688879`
- `val_bpb`: `5.321928`
- Compressed artifact size (bytes): `1241`
- Number of runs / seeds: `1`

## Artifacts

- `submission.json`
- `train.log`
- `train_gpt.py`
- `local_bigram_artifact.json`

## Notes

This is a truthful local smoke submission generated in this repository. It is useful to validate the workflow, but it is not intended to be competitive on the official Parameter Golf leaderboard.
