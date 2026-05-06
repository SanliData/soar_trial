"""
FILE: src/http/v1/livebook_endpoints.py
PURPOSE: Read-only LiveBook exposure (safe, non-invasive)
ENCODING: UTF-8 WITHOUT BOM
"""

import os
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, JSONResponse

router = APIRouter(tags=["livebook"])

BASE_DIR = Path(__file__).resolve().parents[3]
DOCS_DIR = BASE_DIR / "docs"

LIVEBOOK_DIR = DOCS_DIR / "live_book"
MAINBOOK_DIR = DOCS_DIR / "main_book"

LIVEBOOK_ENABLED = os.getenv("FINDEROS_LIVEBOOK_ENABLED", "false").lower() == "true"


def _ensure_enabled():
    if not LIVEBOOK_ENABLED:
        raise HTTPException(status_code=404, detail="LiveBook is disabled")


@router.get("/livebook")
def livebook_index():
    _ensure_enabled()
    return JSONResponse(
        {
            "status": "ok",
            "livebook": {
                "html": "/v1/livebook/html",
                "docx": "/v1/livebook/docx",
            },
            "mainbook": {
                "html": "/v1/mainbook/html",
                "docx": "/v1/mainbook/docx",
            },
        }
    )


@router.get("/livebook/html")
def get_livebook_html():
    _ensure_enabled()
    path = LIVEBOOK_DIR / "FinderOS_LiveBook_2025-12-13.html"
    if not path.exists():
        raise HTTPException(status_code=404, detail="LiveBook HTML not found")
    return FileResponse(path, media_type="text/html")


@router.get("/livebook/docx")
def get_livebook_docx():
    _ensure_enabled()
    path = LIVEBOOK_DIR / "FinderOS_LiveBook_2025-12-13.docx"
    if not path.exists():
        raise HTTPException(status_code=404, detail="LiveBook DOCX not found")
    return FileResponse(
        path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )


@router.get("/mainbook/html")
def get_mainbook_html():
    _ensure_enabled()
    path = MAINBOOK_DIR / "FinderOS_MainBook_v0.1.html"
    if not path.exists():
        raise HTTPException(status_code=404, detail="MainBook HTML not found")
    return FileResponse(path, media_type="text/html")


@router.get("/mainbook/docx")
def get_mainbook_docx():
    _ensure_enabled()
    path = MAINBOOK_DIR / "FinderOS_MainBook_v0.1.docx"
    if not path.exists():
        raise HTTPException(status_code=404, detail="MainBook DOCX not found")
    return FileResponse(
        path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
