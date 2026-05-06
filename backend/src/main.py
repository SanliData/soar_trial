"""
MAIN: main
PURPOSE: Application entry point (DigitalOcean PM2 or Cloud Run / PaaS)
ENCODING: UTF-8 WITHOUT BOM
"""

import os
import sys
import uvicorn
from pathlib import Path
from dotenv import load_dotenv

***REMOVED*** Load .env from backend/ (override=True so .env wins over existing env)
_backend_dir = Path(__file__).resolve().parent.parent
load_dotenv(_backend_dir / ".env", override=True)

from src.config.settings import get_settings, get_int_env

if __name__ == "__main__":
    settings = get_settings()
    ***REMOVED*** PORT from env (Cloud Run/Heroku) overrides FINDEROS_PORT
    _default_port = int(settings.FINDEROS_PORT or "8000")
    port = get_int_env("PORT", _default_port)
    host = settings.FINDEROS_HOST
    skip_port_check = settings.SKIP_PORT_CHECK or (settings.K_SERVICE is not None)

    from src.app import app
    from src.core.port_check import check_port_and_exit

    if not skip_port_check:
        check_port_and_exit(host, port)

    reload = (os.getenv("FINDEROS_RELOAD") or "").strip().lower() in ("1", "true", "yes")
    if settings.ENV == "production":
        reload = False
        host = "0.0.0.0"
    if sys.platform == "win32" and not os.getenv("FINDEROS_RELOAD"):
        reload = False

    use_https = settings.FINDEROS_USE_HTTPS and settings.FINDEROS_SSL_CERTFILE and settings.FINDEROS_SSL_KEYFILE
    ssl_config = None
    if use_https:
        ssl_config = {
            "ssl_certfile": settings.FINDEROS_SSL_CERTFILE,
            "ssl_keyfile": settings.FINDEROS_SSL_KEYFILE,
        }
        print(f"Starting FinderOS with HTTPS on {host}:{port}")
    else:
        print(f"Starting FinderOS with HTTP on {host}:{port}")

    uvicorn_config = {"host": host, "port": port, "reload": reload}
    if reload:
        uvicorn_config["reload_dirs"] = ["src"]
    uvicorn.run("src.app:app", **uvicorn_config, **(ssl_config or {}))
