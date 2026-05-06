***REMOVED***!/usr/bin/env python3
"""
Generate openapi.json at build time. Writes to backend/docs/openapi.json (or path from env).
Usage: from backend/ run: python scripts/generate_openapi.py
"""

import json
import os
import sys
from pathlib import Path

***REMOVED*** backend/ as cwd
_backend = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_backend))
os.chdir(_backend)

from dotenv import load_dotenv
load_dotenv(_backend / ".env")

***REMOVED*** Ensure minimal env so app can load (for build without full .env)
for key, val in (
    ("ENV", "development"),
    ("DATABASE_URL", "sqlite:///./finderos.db"),
    ("JWT_SECRET", "generate-openapi-secret"),
    ("SOARB2B_API_KEYS", "generate-openapi-key"),
    ("FINDEROS_CORS_ORIGINS", "http://localhost"),
    ("ENABLE_DOCS", "true"),
):
    if not os.environ.get(key):
        os.environ[key] = val

from src.app import app

out_dir = Path(os.environ.get("OPENAPI_OUT_DIR", _backend / "docs"))
out_dir.mkdir(parents=True, exist_ok=True)
out_file = out_dir / "openapi.json"
schema = app.openapi()
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(schema, f, indent=2, ensure_ascii=False)
print(f"Wrote {out_file}")
