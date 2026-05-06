***REMOVED***!/bin/bash
***REMOVED*** backend/ dizininden uvicorn çalıştırır (src modülü backend/src olduğu için cwd=backend gerekli)
***REMOVED*** Kullanım: ./scripts/start_uvicorn.sh  veya  backend/ dizininden: scripts/start_uvicorn.sh

set -e
BACKEND_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$BACKEND_DIR"

PORT="${PORT:-8000}"
VENV_UVICORN="$BACKEND_DIR/venv/bin/uvicorn"

if [ ! -x "$VENV_UVICORN" ]; then
  echo "Hata: venv bulunamadi veya uvicorn yok. Once: python -m venv venv && venv/bin/pip install -r requirements.txt" >&2
  exit 1
fi

echo "SOAR B2B: cwd=$BACKEND_DIR, port=$PORT"
exec "$VENV_UVICORN" src.app:app --host 0.0.0.0 --port "$PORT"
