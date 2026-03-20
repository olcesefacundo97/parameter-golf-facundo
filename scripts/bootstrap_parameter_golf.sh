#!/usr/bin/env bash
set -euo pipefail

DEST="./upstream/parameter-golf"
SETUP_VENV=0
PYTHON_BIN="python3"

usage() {
  cat <<USAGE
Uso: $0 [opciones]

Opciones:
  --dest PATH         Ruta destino del repo oficial (default: ./upstream/parameter-golf)
  --setup-venv        Crea .venv e instala dependencias base en el repo oficial
  --python BIN        Intérprete de Python a usar (default: python3)
  -h, --help          Mostrar esta ayuda
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dest)
      DEST="$2"
      shift 2
      ;;
    --setup-venv)
      SETUP_VENV=1
      shift
      ;;
    --python)
      PYTHON_BIN="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Opción desconocida: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

mkdir -p "$(dirname "$DEST")"

if [[ -d "$DEST/.git" ]]; then
  echo "[bootstrap] Actualizando repo existente en $DEST"
  git -C "$DEST" pull --ff-only
else
  echo "[bootstrap] Clonando repo oficial en $DEST"
  git clone https://github.com/openai/parameter-golf.git "$DEST"
fi

if [[ "$SETUP_VENV" -eq 1 ]]; then
  echo "[bootstrap] Creando entorno virtual con $PYTHON_BIN"
  "$PYTHON_BIN" -m venv "$DEST/.venv"
  # shellcheck disable=SC1091
  source "$DEST/.venv/bin/activate"
  python -m pip install --upgrade pip
  pip install mlx numpy sentencepiece huggingface-hub datasets tqdm
fi

cat <<EOF2

Listo.

Próximos pasos sugeridos:
  cd "$DEST"
  python3 data/cached_challenge_fineweb.py --variant sp1024 --train-shards 1

Si preparaste el venv:
  source "$DEST/.venv/bin/activate"
EOF2
