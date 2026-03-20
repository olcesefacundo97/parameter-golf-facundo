# Campaigns para atacar Parameter Golf

Estos presets están pensados para correr sobre un clon local de `openai/parameter-golf` usando `scripts/run_campaign.py`.

## Presets incluidos

- `baseline_sp1024.env`: baseline simple para smoke tests o punto de partida.
- `long_context_2048.env`: empuja contexto largo, inspirado por los runs públicos que mejoraron usando secuencias más largas.
- `sliding_eval.env`: deja preparado un run orientado a evaluar con sliding window / stride.
- `lora_ttt.env`: preset orientado a test-time training con LoRA.

## Uso

```bash
python3 scripts/run_campaign.py \
  --campaign campaigns/long_context_2048.env \
  --upstream-repo ./upstream/parameter-golf \
  --slug long-context-2048 \
  --author-name "Tu Nombre" \
  --github-id tu_github \
  --summary "Long context + smoke run local"
```
