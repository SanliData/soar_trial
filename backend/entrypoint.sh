***REMOVED***!/bin/sh
***REMOVED*** python:3.11-slim has only sh, not bash
PORT="${PORT:-8080}"
echo "SOAR B2B: starting uvicorn on 0.0.0.0:${PORT}" >&2
exec python -m uvicorn src.app:app --host 0.0.0.0 --port "$PORT"
