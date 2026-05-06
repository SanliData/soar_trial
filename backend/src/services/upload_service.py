"""
SERVICE: upload_service
PURPOSE: LinkedIn profile and company target parsing — user-provided data only, no scraping.
ENCODING: UTF-8 WITHOUT BOM
"""

import re
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path
import json

logger = logging.getLogger(__name__)

***REMOVED*** backend/data (same as public_router)
DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
UPLOADS_FILE = DATA_DIR / "uploads.jsonl"


def _ensure_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _extract_text_from_pdf_base64(pdf_base64: str) -> Optional[str]:
    """Extract text from PDF base64 content. Optional: requires pypdf or PyPDF2."""
    try:
        import base64
        raw = base64.b64decode(pdf_base64, validate=True)
    except Exception:
        return None
    try:
        from pypdf import PdfReader
        from io import BytesIO
        reader = PdfReader(BytesIO(raw))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except ImportError:
        try:
            from PyPDF2 import PdfReader
            from io import BytesIO
            reader = PdfReader(BytesIO(raw))
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        except ImportError:
            logger.warning("PDF parsing requires pypdf or PyPDF2")
            return None
    except Exception as e:
        logger.warning("PDF extract failed: %s", e)
        return None


def _parse_linkedin_url(url: str) -> Dict[str, Optional[str]]:
    """
    From LinkedIn profile URL we do NOT scrape. We only normalize and optionally
    extract /in/ slug for display. Company/role come from user-provided PDF or text.
    """
    url = (url or "").strip()
    if not url or "linkedin.com" not in url.lower():
        return {"url": url, "slug": None, "company_from_url": None}
    slug = None
    m = re.search(r"linkedin\.com/in/([a-zA-Z0-9_-]+)", url, re.I)
    if m:
        slug = m.group(1)
    return {"url": url, "slug": slug, "company_from_url": None}


def _parse_profile_text(text: str) -> Dict[str, Any]:
    """
    Heuristic extraction from plain text (copy-paste or PDF export).
    Look for role, seniority, department, company.
    """
    text = (text or "").strip()
    role = seniority = department = company = None
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    ***REMOVED*** Common patterns: "Title at Company", "Department · Company", "Senior X at Y"
    seniority_keywords = ["senior", "lead", "head", "director", "vp", "ceo", "cto", "cfo", "manager", "associate", "junior", "intern"]
    for line in lines:
        line_lower = line.lower()
        if " at " in line:
            parts = line.split(" at ", 1)
            if not role and len(parts[0]) < 120:
                role = parts[0].strip()
            if not company and len(parts) > 1 and len(parts[1]) < 120:
                company = parts[1].strip()
        if not department and any(k in line_lower for k in ["engineering", "sales", "marketing", "operations", "procurement", "hr", "finance", "product"]):
            department = line[:80].strip()
        if not seniority and any(s in line_lower for s in seniority_keywords):
            for s in seniority_keywords:
                if s in line_lower:
                    seniority = s.capitalize()
                    break
    if not role and lines:
        role = lines[0][:120] if len(lines[0]) > 0 else None
    return {
        "role": role,
        "seniority": seniority,
        "department": department,
        "company_match": company,
        "raw_preview": text[:500] if text else None,
    }


def parse_linkedin_profile(
    linkedin_url: Optional[str] = None,
    pdf_base64: Optional[str] = None,
    plain_text: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Parse user-provided LinkedIn input. No scraping.
    Returns: role, seniority, department, company_match, seed for persona enrichment.
    """
    url_info = _parse_linkedin_url(linkedin_url or "")
    text = plain_text
    if not text and pdf_base64:
        text = _extract_text_from_pdf_base64(pdf_base64)
    parsed = _parse_profile_text(text) if text else {}
    return {
        "linkedin_url": url_info.get("url"),
        "linkedin_slug": url_info.get("slug"),
        "role": parsed.get("role"),
        "seniority": parsed.get("seniority"),
        "department": parsed.get("department"),
        "company_match": parsed.get("company_match"),
        "raw_preview": parsed.get("raw_preview"),
    }


def validate_and_parse_company_target(
    company_name: Optional[str] = None,
    domain: Optional[str] = None,
    google_maps_url: Optional[str] = None,
    csv_text: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Validate and normalize company target input. No external lookup required for P0.
    Returns: list of {company_name, domain, city?} for preview.
    """
    companies: List[Dict[str, str]] = []
    if company_name or domain:
        companies.append({
            "company_name": (company_name or "").strip() or None,
            "domain": (domain or "").strip().lower() or None,
            "source": "form",
        })
    if google_maps_url:
        url = (google_maps_url or "").strip()
        ***REMOVED*** Extract place name from URL if possible (e.g. place name in query)
        name = None
        if "place/" in url:
            m = re.search(r"place/([^/]+)", url)
            if m:
                name = m.group(1).replace("+", " ").strip()
        companies.append({
            "company_name": name,
            "google_maps_url": url,
            "source": "google_maps",
        })
    if csv_text:
        for line in csv_text.strip().splitlines()[1:]:  ***REMOVED*** skip header if present
            parts = [p.strip() for p in line.split(",")]
            if len(parts) >= 1:
                companies.append({
                    "company_name": parts[0] if parts[0] else None,
                    "domain": parts[1].lower() if len(parts) > 1 and parts[1] else None,
                    "city": parts[2] if len(parts) > 2 else None,
                    "source": "csv",
                })
    return {
        "companies": companies,
        "preview_count": len(companies),
    }


def store_upload_record(
    upload_id: str,
    upload_type: str,
    client_ip: str,
    payload_sanitized: Dict[str, Any],
    preview: Optional[Dict[str, Any]] = None,
    abuse_suspicion: bool = False,
    user_agent: Optional[str] = None,
) -> None:
    """Append one upload record to JSONL for admin visibility."""
    _ensure_data_dir()
    from datetime import datetime
    record = {
        "upload_id": upload_id,
        "type": upload_type,
        "client_ip": client_ip,
        "created_at": datetime.utcnow().isoformat(),
        "payload": payload_sanitized,
        "preview": preview,
        "abuse_suspicion": abuse_suspicion,
        "user_agent": (user_agent or "")[:500],
    }
    try:
        with open(UPLOADS_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception as e:
        logger.error("Failed to store upload record: %s", e)


def list_uploads(limit: int = 100, upload_type: Optional[str] = None, abuse_only: bool = False) -> List[Dict[str, Any]]:
    """Read recent uploads for admin. Optional filter by type or abuse_suspicion."""
    if not UPLOADS_FILE.exists():
        return []
    records = []
    try:
        with open(UPLOADS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    r = json.loads(line)
                    if upload_type and r.get("type") != upload_type:
                        continue
                    if abuse_only and not r.get("abuse_suspicion"):
                        continue
                    records.append(r)
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        logger.error("Failed to read uploads: %s", e)
        return []
    records.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return records[:limit]
