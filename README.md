# parameter-golf-facundo

Starter en español para participar en el challenge **OpenAI Model Craft Challenge: Parameter Golf**.

Este repo no reemplaza al proyecto oficial; te deja un punto de partida más simple para:

- entender de qué se trata el challenge,
- bajar el repositorio oficial,
- preparar un entorno local,
- y tener un checklist claro para empezar a iterar.

## Qué es Parameter Golf

El challenge oficial busca entrenar el mejor modelo de lenguaje que entre en un artefacto de **16 MB** y que entrene en menos de **10 minutos en 8xH100**, evaluado sobre FineWeb con un criterio de compresión (`bits per byte`).

Repositorio oficial:

- https://github.com/openai/parameter-golf

## Qué incluye este repo

- `scripts/bootstrap_parameter_golf.sh`: clona o actualiza el repo oficial y, opcionalmente, prepara un `venv` con dependencias base.
- `scripts/init_submission.py`: genera una carpeta local de submission con `README.md`, `submission.json`, `train.log` y `train_gpt.py`.
- `docs/roadmap.md`: roadmap corto para pasar de cero a una primera corrida.
- `docs/submission-workflow.md`: guía para preparar una submission reproducible antes de llevarla al repo oficial.
- `scripts/validate_submission.py`: valida una submission en modo `draft` o `submission` para detectar placeholders, métricas faltantes y problemas de estructura.
- `scripts/update_submission_metrics.py`: extrae métricas desde `train.log` y actualiza `submission.json`, con overrides manuales opcionales.
- `scripts/export_submission.py`: copia una submission validada al árbol `records/` de un clon local del repo oficial.
- `scripts/report_submissions.py`: recorre submissions locales y muestra un reporte ordenable por métricas para comparar runs.
- `scripts/run_submission.py`: crea un scaffold, ejecuta un comando real, captura `train.log` y sincroniza métricas automáticamente.
- `scripts/run_campaign.py`: lanza presets de campaña contra un clon local de `openai/parameter-golf`.
- `campaigns/*.env`: presets de experimentos inspirados por ideas públicas competitivas (baseline, long context, sliding eval, LoRA TTT).
- `records/track_non_record_16mb/2026-03-20_local_bigram_smoke`: example of a truthful local non-record submission generated in this repo.

## Uso rápido

### 1. Clonar este repo

```bash
git clone <tu-repo>
cd parameter-golf-facundo
```

### 2. Traer el repo oficial

```bash
./scripts/bootstrap_parameter_golf.sh --dest ./upstream/parameter-golf
```

### 3. Preparar un entorno Python

```bash
./scripts/bootstrap_parameter_golf.sh --dest ./upstream/parameter-golf --setup-venv
```

### 4. Siguientes pasos

Seguí el roadmap local:

```bash
cat docs/roadmap.md
cat docs/submission-workflow.md
```

Corré una campaña/preset competitivo:

```bash
python3 scripts/run_campaign.py \
  --campaign campaigns/long_context_2048.env \
  --upstream-repo ./upstream/parameter-golf \
  --slug long-context-2048 \
  --author-name "Tu Nombre" \
  --github-id tu_github \
  --summary "Long context + smoke run local"
```

Corré una submission local de punta a punta:

```bash
python3 scripts/run_submission.py \
  --track track_non_record_16mb \
  --slug smoke-test \
  --author-name "Tu Nombre" \
  --github-id tu_github \
  --summary "Smoke test local" \
  -- python3 -c "print('val_loss=1.23 val_bpb=0.98 artifact_size_bytes=12345678 num_runs=1')"
```

Completá o sincronizá métricas desde el log:

```bash
python3 scripts/update_submission_metrics.py records/<track>/<fecha_slug>
```

Validá la carpeta antes de moverla al repo oficial:

```bash
python3 scripts/validate_submission.py records/<track>/<fecha_slug> --mode submission
```

Compará tus runs locales rápidamente:

```bash
python3 scripts/report_submissions.py --base-dir records --sort-by val_bpb
```

Y exportala al clon local del repo oficial:

```bash
python3 scripts/export_submission.py records/<track>/<fecha_slug> ./upstream/parameter-golf
```

### 5. Crear una carpeta de submission local

```bash
python3 scripts/init_submission.py \
  --track track_non_record_16mb \
  --slug mi-primer-intento \
  --author-name "Tu Nombre" \
  --github-id tu_github \
  --summary "Hipótesis resumida de la corrida"
```

## Recomendación práctica

Si querés avanzar rápido:

1. hacé smoke tests locales,
2. ejecutá corridas baratas en una sola GPU,
3. registrá cada experimento,
4. y recién después prepará una submission seria para el leaderboard.

## Nota

El código, reglas y leaderboard viven en el repo oficial de OpenAI. Este repo es solo un wrapper liviano para arrancar con menos fricción.
