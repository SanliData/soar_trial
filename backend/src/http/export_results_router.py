"""
ROUTER: export_results_router
PURPOSE: Ad-hoc export endpoint for cached query results (CSV/PDF/Maps + LinkedIn/Google Ads)
ENCODING: UTF-8 WITHOUT BOM

Acontext: TOOL_CALL + store_artifact observability for each export.
"""

import csv
import hashlib
import io
import json
import logging
import time
import uuid
import zipfile
from datetime import datetime
from pathlib import Path
from typing import List, Literal, Optional
from urllib.parse import quote_plus

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field, validator
from sqlalchemy.orm import Session
from fpdf import FPDF

from src.db.base import get_db
from src.services.result_service import get_result_service
from src.core.upap import run_upap_gates
from src.models.plan_lifecycle import PlanLifecycle

logger = logging.getLogger(__name__)

# Directory for export evidence artifacts (export_verification.json)
EXPORTS_EVIDENCE_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data" / "exports" / "evidence"


ALLOWED_FORMATS = {"csv", "pdf", "maps", "linkedin_ads", "google_ads", "both_ads"}


class ExportResultsRequest(BaseModel):
    format: Literal["csv", "pdf", "maps", "linkedin_ads", "google_ads", "both_ads"]
    query_id: str = Field(..., min_length=1, description="Unique identifier of the plan / query")
    language: Optional[str] = Field("en", description="Target language for UI hints (defaults to English)")

    @validator("format", pre=True)
    def normalize_format(cls, value: str) -> str:
        if value is None:
            raise ValueError("format is required")
        normalized = value.lower()
        if normalized not in ALLOWED_FORMATS:
            raise ValueError(
                f"Unsupported format '{value}'. Allowed: csv, pdf, maps, linkedin_ads, google_ads, both_ads"
            )
        return normalized

    @validator("language", pre=True, always=True)
    def default_language(cls, value: Optional[str]) -> str:
        if not value:
            return "en"
        return value.lower()


router = APIRouter(prefix="/api", tags=["export"])


def _record_export_observability(
    trace_id: str,
    run_id: str,
    query_id: str,
    export_format: str,
    row_count: int,
) -> None:
    """
    Record TOOL_CALL and store_artifact for Acontext observability.
    Fire-and-forget, best-effort.
    """
    def _run() -> None:
        import asyncio
        try:
            from src.integrations.acontext_client import (
                get_session_id_from_trace,
                store_event,
                store_artifact,
            )
            from src.security.context_guard import extract_tenant_from_context

            tenant_id = extract_tenant_from_context(query_id=query_id)
            session_id = get_session_id_from_trace(trace_id, run_id)
            artifact_type_map = {
                "csv": "CSV",
                "pdf": "PDF",
                "maps": "JSON",
                "linkedin_ads": "CSV",
                "google_ads": "CSV",
                "both_ads": "JSON",   # ZIP contains CSVs
            }
            artifact_type = artifact_type_map.get(export_format, "JSON")
            artifact_id = str(uuid.uuid4())
            meta_str = f"{query_id}:{export_format}:{row_count}"
            hash_sha256 = hashlib.sha256(meta_str.encode()).hexdigest()

            async def _do() -> None:
                await store_event(
                    session_id, tenant_id,
                    "TOOL_CALL",
                    {
                        "tool_name": f"export_{export_format}",
                        "input_schema": {"query_id": query_id, "format": export_format, "row_count": row_count},
                        "output_schema": {"artifact_type": artifact_type, "artifact_id": artifact_id},
                        "duration_ms": 0,
                    },
                    lead_id=None,
                )
                await store_event(
                    session_id, tenant_id,
                    "AGENT_METRIC",
                    {
                        "metric": "agent_reliability_score",
                        "successful_exports": 1,
                        "total_pipeline_runs": 1,
                        "score": 1.0,
                    },
                    lead_id=None,
                )
                await store_artifact(
                    session_id, tenant_id,
                    artifact_type,
                    artifact_id,
                    hash_sha256,
                    metadata={"query_id": query_id, "row_count": row_count},
                )

            asyncio.run(_do())
        except Exception as e:
            logger.debug("Export observability failed: %s", e)

    import threading
    t = threading.Thread(target=_run, daemon=True)
    t.start()


FIELD_ORDER = [
    "company_name",
    "address",
    "city",
    "zip",
    "persona_role",
    "contact_availability",
]

CSV_HEADER_MAP = {
    "company_name": "Company Name",
    "address": "Address",
    "city": "City",
    "zip": "ZIP / Postal Code",
    "persona_role": "Persona Role",
    "contact_availability": "Contact Availability",
}


class ResultsExportPDF(FPDF):
    """Simple PDF template with footer text."""

    def __init__(self, footer_text: str):
        super().__init__()
        self.footer_text = footer_text

    def footer(self) -> None:
        self.set_y(-15)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, self.footer_text, 0, 0, "C")


@router.post("/export/results")
def export_results(
    http_request: Request,
    request: ExportResultsRequest,
    db: Session = Depends(get_db)
):
    """Export cached query results as CSV, PDF, or Google Maps payload. UPAP: hard filters enforced; PASS evidence required."""
    trace_id = getattr(http_request.state, "request_id", None) or str(uuid.uuid4())
    run_id = str(uuid.uuid4())
    export_format = request.format
    query_id = request.query_id

    result_service = get_result_service(db)
    try:
        rows = result_service.get_export_rows(query_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    # Query params for UPAP (regulated, simulation_mode, limits, etc.) from plan
    query_params = {}
    plan = db.query(PlanLifecycle).filter(PlanLifecycle.plan_id == query_id).first()
    if plan and getattr(plan, "onboarding_data", None):
        query_params = dict(plan.onboarding_data) if isinstance(plan.onboarding_data, dict) else {}
    if plan:
        if getattr(plan, "simulation_mode", None) is not None:
            query_params["simulation_mode"] = plan.simulation_mode
        if getattr(plan, "regulated_domain", None) is not None:
            query_params["regulated_domain"] = plan.regulated_domain

    # UPAP gates: single entry point; fail-fast on any FAIL; evidence written on PASS
    filtered_rows, upap_evidence, gate_status = run_upap_gates(
        stage="EXPORT",
        trace_id=trace_id,
        run_id=run_id,
        query_id=query_id,
        query_params=query_params,
        leads=rows,
        evidence_dir=EXPORTS_EVIDENCE_DIR,
    )
    if gate_status == "FAIL":
        logger.warning(
            "UPAP export FAIL trace_id=%s run_id=%s query_id=%s reason=%s",
            trace_id, run_id, query_id, upap_evidence.get("reason"),
        )
        raise HTTPException(
            status_code=422,
            detail={
                "error": "UPAP export validation failed",
                "error_code": "UPAP_EXPORT_FAIL",
                "trace_id": trace_id,
                "run_id": run_id,
                "reason": upap_evidence.get("reason"),
                "status": upap_evidence.get("status"),
                "regulated_domain": upap_evidence.get("regulated_domain"),
                "simulation_mode": upap_evidence.get("simulation_mode"),
                "rows_before": upap_evidence.get("rows_before"),
                "rows_after": upap_evidence.get("rows_after"),
                "rejected_counts": upap_evidence.get("rejected_counts"),
                "timestamp": upap_evidence.get("timestamp"),
            },
        )

    generated_at = datetime.utcnow()
    logger.info(
        "export_results trace_id=%s run_id=%s format=%s query_id=%s row_count=%s",
        trace_id, run_id, export_format, query_id, len(filtered_rows),
    )

    # Acontext: TOOL_CALL + store_artifact observability
    _record_export_observability(
        trace_id=trace_id,
        run_id=run_id,
        query_id=query_id,
        export_format=export_format,
        row_count=len(filtered_rows),
    )

    if request.format == "csv":
        return _export_as_csv(filtered_rows, query_id, generated_at)
    if request.format == "pdf":
        return _export_as_pdf(filtered_rows, query_id, generated_at)
    if request.format == "maps":
        return _export_for_maps(filtered_rows, query_id, generated_at, request.language)
    if request.format == "linkedin_ads":
        return _export_linkedin_ads(filtered_rows, query_id, generated_at)
    if request.format == "google_ads":
        return _export_google_ads(filtered_rows, query_id, generated_at)
    if request.format == "both_ads":
        return _export_both_ads(filtered_rows, query_id, generated_at)
    return _export_for_maps(filtered_rows, query_id, generated_at, request.language)


def _export_as_csv(rows: List[dict], query_id: str, generated_at: datetime) -> StreamingResponse:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=[CSV_HEADER_MAP[field] for field in FIELD_ORDER])
    writer.writeheader()
    for row in rows:
        csv_row = {}
        for field in FIELD_ORDER:
            header = CSV_HEADER_MAP[field]
            value = row.get(field, "N/A")
            if value is None or value == "":
                value = "N/A"
            csv_row[header] = str(value)
        writer.writerow(csv_row)

    buffer.seek(0)
    timestamp = generated_at.strftime("%Y%m%d_%H%M%S")
    filename = f"soar_results_{query_id}_{timestamp}.csv"
    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"'
    }
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers=headers
    )


def _export_as_pdf(rows: List[dict], query_id: str, generated_at: datetime) -> StreamingResponse:
    timestamp_str = generated_at.strftime("%Y-%m-%d %H:%M:%SZ")
    footer_text = f"Query ID: {query_id} • Generated at {timestamp_str}"
    pdf = ResultsExportPDF(footer_text=footer_text)
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 12, "SOAR B2B Results Export", 0, 1)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, f"Generated: {timestamp_str}", 0, 1)
    pdf.cell(0, 8, f"Query ID: {query_id}", 0, 1)
    pdf.ln(4)

    for index, row in enumerate(rows, start=1):
        pdf.set_font("Helvetica", "B", 11)
        pdf.multi_cell(0, 7, f"{index}. {row.get('company_name', 'N/A')}")
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 6, f"Address: {row.get('address', 'N/A')}")
        pdf.multi_cell(0, 6, f"City / ZIP: {row.get('city', 'N/A')} / {row.get('zip', 'N/A')}")
        pdf.multi_cell(0, 6, f"Persona Role: {row.get('persona_role', 'N/A')}")
        pdf.multi_cell(0, 6, f"Contact Availability: {row.get('contact_availability', 'Not available')}")
        pdf.ln(3)

    pdf_bytes = pdf.output(dest="S").encode("latin-1")
    timestamp = generated_at.strftime("%Y%m%d_%H%M%S")
    filename = f"soar_results_{query_id}_{timestamp}.pdf"
    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"'
    }
    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers=headers
    )


def _export_for_maps(
    rows: List[dict],
    query_id: str,
    generated_at: datetime,
    language: str
) -> JSONResponse:
    mappable = []
    for row in rows:
        has_coordinates = row.get("latitude") is not None and row.get("longitude") is not None
        has_address = row.get("address") and row.get("address") != "N/A"
        if not (has_coordinates or has_address):
            continue
        mappable.append({
            "company_name": row.get("company_name", "N/A"),
            "address": row.get("address", "N/A"),
            "city": row.get("city", "N/A"),
            "zip": row.get("zip", "N/A"),
            "persona_role": row.get("persona_role", "N/A"),
            "contact_availability": row.get("contact_availability", "Not available"),
            "latitude": row.get("latitude"),
            "longitude": row.get("longitude")
        })

    limited = mappable[:20]
    if not limited:
        raise HTTPException(status_code=400, detail="No mappable locations available for export")

    map_segments = []
    for location in limited:
        if location["latitude"] is not None and location["longitude"] is not None:
            segment = f"{location['latitude']},{location['longitude']}"
        else:
            parts = [location.get("company_name", ""), location.get("address", ""), location.get("city", ""), location.get("zip", "")]
            query = " ".join(part for part in parts if part)
            segment = quote_plus(query)
        map_segments.append(segment)

    map_url = "https://www.google.com/maps/dir/" + "/".join(map_segments)

    payload = {
        "query_id": query_id,
        "language": language,
        "generated_at": generated_at.replace(microsecond=0).isoformat() + "Z",
        "limit": 20,
        "returned": len(limited),
        "total_mappable": len(mappable),
        "map_url": map_url,
        "locations": limited
    }
    return JSONResponse(payload)


# Protocol: Company Name, Company Domain, Location (City/Country), Company Size, Industry, Job Function
LINKEDIN_ADS_HEADERS = [
    "Company Name",
    "Company Domain",
    "City",
    "Country",
    "Company Size",
    "Industry",
    "Job Function",
    "Address",
    "ZIP",
]


def _row_to_linkedin_ads(row: dict) -> dict:
    return {
        "Company Name": (row.get("company_name") or "").strip() or "N/A",
        "Company Domain": (row.get("company_domain") or "").strip() or "",
        "City": (row.get("city") or "").strip() or "",
        "Country": (row.get("country") or "").strip() or "",
        "Company Size": (row.get("company_size") or "").strip() or "",
        "Industry": (row.get("industry") or "").strip() or "",
        "Job Function": (row.get("persona_role") or "").strip() or "N/A",
        "Address": (row.get("address") or "").strip() or "",
        "ZIP": (row.get("zip") or "").strip() or "",
    }


def _export_linkedin_ads(
    rows: List[dict], query_id: str, generated_at: datetime
) -> StreamingResponse:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=LINKEDIN_ADS_HEADERS)
    writer.writeheader()
    for row in rows:
        writer.writerow(_row_to_linkedin_ads(row))
    buffer.seek(0)
    timestamp = generated_at.strftime("%Y%m%d_%H%M%S")
    filename = f"soar_linkedin_ads_{query_id}_{timestamp}.csv"
    return StreamingResponse(
        iter([buffer.getvalue().encode("utf-8")]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# Protocol: Business Name, Latitude, Longitude, City, Country, Keyword Intent (+ optional Customer Match)
GOOGLE_ADS_HEADERS = [
    "Business Name",
    "Latitude",
    "Longitude",
    "City",
    "Country",
    "Keyword Intent",
    "Address",
    "ZIP",
]


def _row_to_google_ads(row: dict) -> dict:
    lat = row.get("latitude")
    lng = row.get("longitude")
    if lat is not None and not isinstance(lat, str):
        lat = "" if lat is None else str(lat)
    else:
        lat = (lat or "").strip() if isinstance(lat, str) else ""
    if lng is not None and not isinstance(lng, str):
        lng = "" if lng is None else str(lng)
    else:
        lng = (lng or "").strip() if isinstance(lng, str) else ""
    return {
        "Business Name": (row.get("company_name") or "").strip() or "N/A",
        "Latitude": lat,
        "Longitude": lng,
        "City": (row.get("city") or "").strip() or "",
        "Country": (row.get("country") or "").strip() or "",
        "Keyword Intent": (row.get("keyword_intent") or "").strip() or "",
        "Address": (row.get("address") or "").strip() or "",
        "ZIP": (row.get("zip") or "").strip() or "",
    }


def _export_google_ads(
    rows: List[dict], query_id: str, generated_at: datetime
) -> StreamingResponse:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=GOOGLE_ADS_HEADERS)
    writer.writeheader()
    for row in rows:
        writer.writerow(_row_to_google_ads(row))
    buffer.seek(0)
    timestamp = generated_at.strftime("%Y%m%d_%H%M%S")
    filename = f"soar_google_ads_{query_id}_{timestamp}.csv"
    return StreamingResponse(
        iter([buffer.getvalue().encode("utf-8")]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _campaign_setup_txt(query_id: str, generated_at: datetime) -> str:
    return f"""SOAR B2B - Campaign setup (LinkedIn Ads + Google Ads)
Query ID: {query_id}
Generated: {generated_at.strftime("%Y-%m-%d %H:%M:%SZ")}

=== WHERE TO UPLOAD ===

LINKEDIN ADS:
  - Where: LinkedIn Campaign Manager > Audiences > Create audience > Upload a list
  - File to upload: linkedin_ads.csv (from this ZIP)
  - Purpose: Target companies and job functions for Sponsored Content / Message Ads

GOOGLE ADS:
  - Where: Google Ads > Tools & Settings > Shared library > Audience manager > Custom audiences > Customer list (or use location/campaign targeting with Business Name + City/Country)
  - File to upload: google_ads.csv (from this ZIP)
  - Purpose: Location-based or customer list targeting; Keyword Intent can inform search/display themes

=== WHAT EACH FILE CONTAINS ===

linkedin_ads.csv:
  - Company Name: Business name (required for Matched Audiences)
  - Company Domain: Website domain for matching
  - City, Country: Location for targeting
  - Company Size, Industry: For audience filters
  - Job Function: Decision-maker role (title hint)
  - Address, ZIP: Additional location fields

google_ads.csv:
  - Business Name: Company name
  - Latitude, Longitude: For location targeting (use when present)
  - City, Country: Location
  - Keyword Intent: Verified services / intent (use for search or display themes)
  - Address, ZIP: For address-based audience match if supported

=== LINKEDIN VS GOOGLE ===
  - LinkedIn: B2B professional targeting; use Company Name + Job Function.
  - Google: Broader reach; use locations (Lat/Lng or City/Country) and optionally Keyword Intent for creative alignment.
"""


# ZIP must contain exactly these names (protocol)
ZIP_LINKEDIN_CSV_NAME = "linkedin_ads.csv"
ZIP_GOOGLE_CSV_NAME = "google_ads.csv"
ZIP_CAMPAIGN_SETUP_NAME = "campaign_setup.txt"


def _export_both_ads(
    rows: List[dict], query_id: str, generated_at: datetime
) -> StreamingResponse:
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        li_buf = io.StringIO()
        li_writer = csv.DictWriter(li_buf, fieldnames=LINKEDIN_ADS_HEADERS)
        li_writer.writeheader()
        for row in rows:
            li_writer.writerow(_row_to_linkedin_ads(row))
        zf.writestr(ZIP_LINKEDIN_CSV_NAME, li_buf.getvalue().encode("utf-8"))
        go_buf = io.StringIO()
        go_writer = csv.DictWriter(go_buf, fieldnames=GOOGLE_ADS_HEADERS)
        go_writer.writeheader()
        for row in rows:
            go_writer.writerow(_row_to_google_ads(row))
        zf.writestr(ZIP_GOOGLE_CSV_NAME, go_buf.getvalue().encode("utf-8"))
        zf.writestr(
            ZIP_CAMPAIGN_SETUP_NAME,
            _campaign_setup_txt(query_id, generated_at).encode("utf-8"),
        )
    zip_buffer.seek(0)
    timestamp = generated_at.strftime("%Y%m%d_%H%M%S")
    filename = f"soar_ads_both_{query_id}_{timestamp}.zip"
    return StreamingResponse(
        iter([zip_buffer.getvalue()]),
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
