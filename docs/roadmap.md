# Roadmap para empezar con Parameter Golf

## Objetivo

Llegar desde un repo vacío a una primera corrida reproducible basada en el proyecto oficial.

## Paso 1: bajar el repo oficial

```bash
./scripts/bootstrap_parameter_golf.sh --dest ./upstream/parameter-golf
```

## Paso 2: preparar entorno

```bash
./scripts/bootstrap_parameter_golf.sh --dest ./upstream/parameter-golf --setup-venv
source ./upstream/parameter-golf/.venv/bin/activate
```

## Paso 3: descargar un subset chico

Dentro del repo oficial:

```bash
cd ./upstream/parameter-golf
python3 data/cached_challenge_fineweb.py --variant sp1024 --train-shards 1
```

## Paso 4: correr un smoke test local

Si estás en Apple Silicon, podés usar la ruta MLX del repo oficial. Si no, usá la ruta estándar CUDA en una máquina remota.

Si querés saltar directo a una máquina remota y arrancar desde el SOTA público actual, podés usar:

```bash
cd /workspace
git clone https://github.com/olcesefacundo97/parameter-golf-facundo.git
cd parameter-golf-facundo
bash scripts/runpod_attack_sota.sh
```

## Paso 5: elegir estrategia

Algunas líneas de exploración razonables:

- parameter tying,
- embeddings comprimidos,
- menor precisión,
- test-time compute,
- contextos más largos,
- cambios de optimizer y schedule,
- variantes de tokenizer solo si podés validar muy bien la métrica.

## Paso 6: guardar evidencia

Para cada run, guardá:

- config usada,
- log de entrenamiento,
- `val_loss`,
- `val_bpb`,
- tamaño final del artefacto,
- y observaciones.

## Paso 7: submission

Si tu idea funciona, prepará una carpeta de submission siguiendo exactamente la estructura del repo oficial en `records/`.
