# Workflow para preparar una submission de Parameter Golf

Este repo ahora incluye un generador local de carpetas de submission para no arrancar desde cero cada vez.

## 1. Crear un scaffold de submission

Ejemplo para una corrida no-record:

```bash
python3 scripts/init_submission.py \
  --track track_non_record_16mb \
  --slug lora-ttt-exploracion \
  --author-name "Tu Nombre" \
  --github-id tu_github \
  --summary "Prueba de LoRA + test-time training en track no-record"
```

Eso crea una carpeta con esta estructura:

```text
records/
  track_non_record_16mb/
    YYYY-MM-DD_lora_ttt_exploracion/
      README.md
      submission.json
      train.log
      train_gpt.py
      .gitignore
```

## 2. Completar los placeholders

Antes de subir nada al repo oficial:

- reemplazá los placeholders de `README.md`,
- pegá el `train.log` real,
- copiá el `train_gpt.py` exacto usado para la corrida,
- completá métricas y metadatos en `submission.json`.

## 3. Validar contenido mínimo

La idea es que cada submission tenga, como mínimo:

- descripción clara del enfoque,
- comando reproducible,
- logs suficientes,
- métricas finales,
- script exacto usado,
- y contexto para que otra persona pueda reproducirla.

## 4. Llevarlo al repo oficial

Cuando la carpeta esté bien armada, copiala o recreala en el árbol `records/` del repo oficial de OpenAI respetando exactamente el track correcto.



## 5. Sincronizar métricas desde el log

Si tu `train.log` ya contiene líneas como `val_loss=...`, `val_bpb=...`, `artifact_size_bytes=...` o `num_runs=...`, podés actualizar `submission.json` automáticamente:

```bash
python3 scripts/update_submission_metrics.py records/<track>/<fecha_slug>
```

También podés forzar valores manualmente:

```bash
python3 scripts/update_submission_metrics.py records/<track>/<fecha_slug> \
  --val-loss 1.23 \
  --val-bpb 0.98 \
  --artifact-size-bytes 12345678 \
  --num-runs 3
```

## 6. Validar antes de subir

Podés validar el scaffold en modo borrador:

```bash
python3 scripts/validate_submission.py records/<track>/<fecha_slug> --mode draft
```

Y validar la versión final antes de abrir un PR contra el repo oficial:

```bash
python3 scripts/validate_submission.py records/<track>/<fecha_slug> --mode submission
```

En modo `submission`, placeholders, métricas nulas o stubs sin reemplazar pasan a ser errores.

## 7. Exportar al clon local del repo oficial

Una vez que la submission pasa la validación final, podés copiarla al árbol `records/` de tu clon local del repo oficial:

```bash
python3 scripts/export_submission.py records/<track>/<fecha_slug> ./upstream/parameter-golf
```

Si el destino ya existe y querés reemplazarlo:

```bash
python3 scripts/export_submission.py records/<track>/<fecha_slug> ./upstream/parameter-golf --force
```


## 8. Comparar submissions locales

Si ya tenés varias submissions o borradores en `records/`, podés listarlas y ordenarlas por métrica:

```bash
python3 scripts/report_submissions.py --base-dir records --sort-by val_bpb
```

También podés filtrar por track o sacar JSON:

```bash
python3 scripts/report_submissions.py --base-dir records --track track_non_record_16mb --format json
```


## 9. Ejecutar una submission local en un solo comando

Si querés automatizar scaffold + ejecución + captura de log + sync de métricas, podés usar:

```bash
python3 scripts/run_submission.py \
  --track track_non_record_16mb \
  --slug smoke-test \
  --author-name "Tu Nombre" \
  --github-id tu_github \
  --summary "Smoke test local" \
  -- python3 -c "print('val_loss=1.23 val_bpb=0.98 artifact_size_bytes=12345678 num_runs=1')"
```

Si querés preservar el script exacto usado, agregá `--train-script path/al/train_gpt.py`.


## 10. Lanzar campañas con presets competitivos

Si ya tenés un clon local del repo oficial, podés usar presets listos para atacar ideas públicas prometedoras:

```bash
python3 scripts/run_campaign.py \
  --campaign campaigns/long_context_2048.env \
  --upstream-repo ./upstream/parameter-golf \
  --slug long-context-2048 \
  --author-name "Tu Nombre" \
  --github-id tu_github \
  --summary "Long context + smoke run local"
```

Mirá `campaigns/README.md` para ver los presets incluidos.
