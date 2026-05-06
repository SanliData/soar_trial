***REMOVED***!/bin/bash
***REMOVED*** Run Uvicorn locally with reload (Windows git-bash compatible).
***REMOVED*** Usage (from backend/): scripts/run_uvicorn_reload_local.sh

set -euo pipefail

BACKEND_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$BACKEND_DIR"

HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8000}"

PYTHON_BIN="${PYTHON_BIN:-python}"

UVICORN_BIN=""
if [ -x "$BACKEND_DIR/.venv/Scripts/uvicorn.exe" ]; then
  UVICORN_BIN="$BACKEND_DIR/.venv/Scripts/uvicorn.exe"
elif [ -x "$BACKEND_DIR/venv/Scripts/uvicorn.exe" ]; then
  UVICORN_BIN="$BACKEND_DIR/venv/Scripts/uvicorn.exe"
elif [ -x "$BACKEND_DIR/venv/bin/uvicorn" ]; then
  UVICORN_BIN="$BACKEND_DIR/venv/bin/uvicorn"
fi

echo "SOAR B2B local dev"
echo "  cwd=$BACKEND_DIR"
echo "  host=$HOST"
echo "  port=$PORT"
echo "  reload=true"

export PYTHONPATH="$BACKEND_DIR"
export ENV="${ENV:-development}"

if [ -n "$UVICORN_BIN" ]; then
  exec "$UVICORN_BIN" src.app:app --host "$HOST" --port "$PORT" --reload
fi

exec "$PYTHON_BIN" -m uvicorn src.app:app --host "$HOST" --port "$PORT" --reload

