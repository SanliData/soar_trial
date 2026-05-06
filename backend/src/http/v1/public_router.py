"""
ROUTER: public_router
PURPOSE: Public endpoints (no authentication required, rate limited)
ENCODING: UTF-8 WITHOUT BOM
"""

import os
import json
import uuid
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

from fastapi import APIRouter, Request, HTTPException, UploadFile, File, Depends, Query
from fastapi import Header
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from src.db.base import get_db
from src.models.user import User
from src.middleware.locale_middleware import get_locale_from_request
from src.core.messages import get_onboarding_received_message
from src.security.bot_defense import get_captcha_required_response
from src.security.captcha import verify_captcha_token
from src.services.upload_service import (
    parse_linkedin_profile,
    validate_and_parse_company_target,
    store_upload_record,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["public"])  ***REMOVED*** Prefix app.py'de tanımlı: /api/v1/public

***REMOVED*** Data directory
DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)


def _check_captcha_if_required(request: Request, x_captcha_token: Optional[str] = None) -> Optional[Dict]:
    """
    If bot defense set require_captcha, require valid CAPTCHA token.
    Returns error response dict if CAPTCHA required but invalid; None otherwise.
    """
    require = getattr(request.state, "require_captcha", False)
    if not require:
        return None
    client_ip = request.client.host if request.client else "unknown"
    if not verify_captcha_token(x_captcha_token, client_ip):
        return get_captcha_required_response()
    return None


***REMOVED*** Request Models
class OnboardingIntakeRequest(BaseModel):
    """Public onboarding intake request (limited fields, no sensitive data)"""
    industry: str = Field(..., description="Industry or business type")
    target_region: str = Field(..., description="Target geographic region")
    product_type: str = Field(..., description="Product or service type")
    email: Optional[EmailStr] = Field(None, description="Optional email address")
    hs_code: Optional[str] = Field(None, description="HS / gümrük kodu (opsiyonel; girilmezse AI ile eklenir)")


class OnboardingIntakeResponse(BaseModel):
    """Response for public onboarding intake"""
    intake_id: str
    status: str
    message: str


***REMOVED*** --- Upload: LinkedIn Profile (user-provided only, no scraping) ---
class LinkedInProfileUploadRequest(BaseModel):
    """LinkedIn profile input: URL, PDF base64, or plain text."""
    linkedin_url: Optional[str] = Field(None, description="LinkedIn profile URL (e.g. linkedin.com/in/name)")
    pdf_base64: Optional[str] = Field(None, description="LinkedIn profile export PDF as base64")
    plain_text: Optional[str] = Field(None, description="Copy-paste profile text")


class LinkedInProfileUploadResponse(BaseModel):
    """Parsed persona seed for discovery."""
    upload_id: str
    status: str
    role: Optional[str] = None
    seniority: Optional[str] = None
    department: Optional[str] = None
    company_match: Optional[str] = None
    raw_preview: Optional[str] = None
    message: str = "User-provided data accepted. SOAR does not scrape or access private data."


***REMOVED*** --- Upload: Company Target ---
class CompanyTargetUploadRequest(BaseModel):
    """Company target input: name, domain, Google Maps URL, or CSV rows."""
    company_name: Optional[str] = Field(None, description="Company name")
    domain: Optional[str] = Field(None, description="Company domain (e.g. example.com)")
    google_maps_url: Optional[str] = Field(None, description="Google Maps place URL")
    csv_text: Optional[str] = Field(None, description="CSV with company_name, website, city")


class CompanyTargetUploadResponse(BaseModel):
    """Preview of companies for persona discovery."""
    upload_id: str
    status: str
    companies: List[Dict[str, Any]]
    preview_count: int
    message: str = "Company targets received. Preview ready; confirm to start discovery."


***REMOVED*** --- Şirket e-postası ile kayıt (sign up) — önce kullanıcı oluşturulmalı ---
class CorporateSignupRequest(BaseModel):
    """Sign up with company email (creates user account; then use login link to sign in)."""
    email: EmailStr = Field(..., description="Company email address")
    full_name: Optional[str] = Field(None, description="Full name (optional)")


class CorporateSignupResponse(BaseModel):
    """Response for corporate signup."""
    success: bool
    message: str
    message_tr: Optional[str] = None


***REMOVED*** --- Şirket e-postası ile giriş talebi (zaten hesabı olanlar) ---
class CorporateLoginRequest(BaseModel):
    """Request login link for company email (link sent by support)."""
    email: EmailStr = Field(..., description="Company email address")


class CorporateLoginResponse(BaseModel):
    """Response for corporate login request."""
    success: bool
    message: str
    message_tr: Optional[str] = None


***REMOVED*** --- Reklam monetizasyon: sayfa slotları merkezi config ---
def get_ad_config() -> Dict[str, Any]:
    """Reklam aç/kapa ve slot ID'leri (env ile). ADS_ENABLED=1, ADSENSE_CLIENT_ID=ca-pub-xxx, slot ID'ler opsiyonel."""
    enabled = (os.getenv("ADS_ENABLED", "").strip().lower() in ("1", "true", "yes"))
    client_id = os.getenv("ADSENSE_CLIENT_ID", "").strip() or None
    return {
        "enabled": enabled,
        "provider": "adsense" if client_id else "none",
        "client_id": client_id,
        "slots": {
            "home-below-hero": os.getenv("ADS_SLOT_HOME_BELOW_HERO", "").strip() or None,
            "home-mid": os.getenv("ADS_SLOT_HOME_MID", "").strip() or None,
            "home-above-footer": os.getenv("ADS_SLOT_HOME_ABOVE_FOOTER", "").strip() or None,
            "onboarding-mid": os.getenv("ADS_SLOT_ONBOARDING_MID", "").strip() or None,
            "results-below-summary": os.getenv("ADS_SLOT_RESULTS_BELOW_SUMMARY", "").strip() or None,
            "side-left": os.getenv("ADS_SLOT_SIDE_LEFT", "").strip() or None,
            "side-right": os.getenv("ADS_SLOT_SIDE_RIGHT", "").strip() or None,
        },
    }


@router.get("/ad-config")
def ad_config():
    """Public: reklam slotlarının açık olup olmadığı ve sağlayıcı/slot ID'leri (frontend reklam yüklemesi için)."""
    return get_ad_config()


***REMOVED*** --- Address / place validation (country–city, geocode by name) ---
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
NOMINATIM_USER_AGENT = "SOARB2B-Onboarding/1.0 (contact@soarb2b.com)"


@router.get("/validate-address")
async def validate_address(
    q: str = Query(..., min_length=2, max_length=300, description="Address or place name (e.g. Paris France, Istanbul Turkey)")
) -> Dict[str, Any]:
    """
    Validate an address or place name and return structured location (country, city, lat, lng).
    Uses OpenStreetMap Nominatim; no API key required. Rate-limited by Nominatim policy (1 req/sec).
    """
    import urllib.parse
    import urllib.request

    query = (q or "").strip()
    if len(query) < 2:
        return {"valid": False, "error": "Query too short", "country": None, "city": None, "display_name": None, "lat": None, "lng": None}

    params = urllib.parse.urlencode({"q": query, "format": "json", "limit": 1})
    url = f"{NOMINATIM_URL}?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": NOMINATIM_USER_AGENT})

    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode())
    except Exception as e:
        logger.warning(f"Nominatim request failed: {e}")
        return {"valid": False, "error": "Address lookup failed", "country": None, "city": None, "display_name": None, "lat": None, "lng": None}

    if not data or not isinstance(data, list):
        return {"valid": False, "error": "Place not found", "country": None, "city": None, "display_name": None, "lat": None, "lng": None}

    item = data[0]
    addr = item.get("address") or {}
    country = addr.get("country") or addr.get("country_code", "")
    city = (
        addr.get("city")
        or addr.get("town")
        or addr.get("village")
        or addr.get("municipality")
        or addr.get("state")
        or addr.get("county")
        or ""
    )
    lat = item.get("lat")
    lon = item.get("lon")
    display_name = item.get("display_name") or ""

    if lat is not None:
        try:
            lat = float(lat)
        except (TypeError, ValueError):
            lat = None
    if lon is not None:
        try:
            lon = float(lon)
        except (TypeError, ValueError):
            lon = None

    return {
        "valid": True,
        "country": country,
        "city": city,
        "display_name": display_name,
        "lat": lat,
        "lng": lon,
    }


***REMOVED*** Endpoints
@router.post("/onboarding-intake", response_model=OnboardingIntakeResponse)
async def create_onboarding_intake(
    request: OnboardingIntakeRequest,
    http_request: Request
):
    """
    Public onboarding intake endpoint.
    
    Accepts basic information from public users and stores as pending intake.
    No analysis or enrichment is performed.
    A SOAR strategist will activate the plan after review.
    """
    intake_id = str(uuid.uuid4())
    created_at = datetime.utcnow().isoformat()
    
    ***REMOVED*** Get locale from request (uses Accept-Language header)
    locale = get_locale_from_request(http_request)
    language = locale  ***REMOVED*** Keep for backward compatibility in stored data
    
    ***REMOVED*** Get referrer URL
    referrer_url = http_request.headers.get("Referer") or http_request.headers.get("Referrer") or ""
    
    ***REMOVED*** Arşiv: her kayıtta HS/gümrük kodu olsun (kullanıcı girmezse AI ile)
    intake_data = {
        "intake_id": intake_id,
        "status": "pending_intake",
        "created_at": created_at,
        "industry": request.industry,
        "target_region": request.target_region,
        "product_type": request.product_type,
        "email": request.email,
        "language": language,
        "referrer_url": referrer_url,
        "ip_address": http_request.client.host if http_request.client else None,
        "user_agent": http_request.headers.get("User-Agent"),
    }
    if request.hs_code and (request.hs_code or "").strip():
        intake_data["hs_code"] = (request.hs_code or "").strip()
        intake_data["hs_code_source"] = "user"
        intake_data["product_customs_description"] = f"User-provided HS {request.hs_code}"
    else:
        from src.services.hs_code_service import ensure_hs_code_in_onboarding
        onboarding_style = {
            "product_service": request.product_type,
            "target_type": request.industry,
            "geography": request.target_region,
            "industry": request.industry,
        }
        enriched = ensure_hs_code_in_onboarding(onboarding_style)
        intake_data["hs_code"] = enriched.get("hs_code")
        intake_data["hs_code_source"] = enriched.get("hs_code_source", "ai")
        intake_data["product_customs_description"] = enriched.get("product_customs_description")
    
    ***REMOVED*** Store to JSONL file (P0: file-based storage)
    intakes_file = DATA_DIR / "onboarding_intakes.jsonl"
    try:
        with open(intakes_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(intake_data, ensure_ascii=False) + "\n")
    except Exception as e:
        logger.error(f"Failed to store onboarding intake: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to process intake request"
        )
    
    ***REMOVED*** Log intake
    logger.info(
        json.dumps({
            "event": "onboarding_intake_created",
            "intake_id": intake_id,
            "timestamp": created_at,
            "language": language,
            "referrer_url": referrer_url,
            "industry": request.industry,
            "target_region": request.target_region,
        }, ensure_ascii=False)
    )
    
    ***REMOVED*** Get language-aware message
    response_message = get_onboarding_received_message(locale)
    
    return OnboardingIntakeResponse(
        intake_id=intake_id,
        status="received",
        message=response_message
    )


***REMOVED*** --- Upload endpoints (bot defense + optional CAPTCHA) ---
@router.post("/upload/linkedin-profile", response_model=LinkedInProfileUploadResponse)
async def upload_linkedin_profile(
    body: LinkedInProfileUploadRequest,
    http_request: Request,
    x_captcha_token: Optional[str] = Header(None, alias="X-Captcha-Token"),
):
    """
    Upload target persona from user-provided LinkedIn data.
    Supports: LinkedIn profile URL, LinkedIn export PDF (base64), or plain text copy-paste.
    SOAR does not scrape or access private data; all input is user-provided.
    """
    err = _check_captcha_if_required(http_request, x_captcha_token)
    if err:
        raise HTTPException(status_code=403, detail=err)

    if not body.linkedin_url and not body.pdf_base64 and not body.plain_text:
        raise HTTPException(
            status_code=422,
            detail="Provide at least one of: linkedin_url, pdf_base64, or plain_text",
        )

    upload_id = str(uuid.uuid4())
    client_ip = http_request.client.host if http_request.client else "unknown"
    user_agent = http_request.headers.get("User-Agent")
    risk = getattr(http_request.state, "bot_risk_score", 0.0)

    result = parse_linkedin_profile(
        linkedin_url=body.linkedin_url,
        pdf_base64=body.pdf_base64,
        plain_text=body.plain_text,
    )
    payload_sanitized = {
        "linkedin_url": body.linkedin_url[:200] if body.linkedin_url else None,
        "has_pdf": bool(body.pdf_base64),
        "plain_text_len": len(body.plain_text) if body.plain_text else 0,
    }
    store_upload_record(
        upload_id=upload_id,
        upload_type="linkedin_profile",
        client_ip=client_ip,
        payload_sanitized=payload_sanitized,
        preview=result,
        abuse_suspicion=risk >= 0.7,
        user_agent=user_agent,
    )
    return LinkedInProfileUploadResponse(
        upload_id=upload_id,
        status="received",
        role=result.get("role"),
        seniority=result.get("seniority"),
        department=result.get("department"),
        company_match=result.get("company_match"),
        raw_preview=result.get("raw_preview"),
        message="You can upload a LinkedIn profile you already have access to. SOAR does not scrape or access private data.",
    )


@router.post("/upload/company-target", response_model=CompanyTargetUploadResponse)
async def upload_company_target(
    body: CompanyTargetUploadRequest,
    http_request: Request,
    x_captcha_token: Optional[str] = Header(None, alias="X-Captcha-Token"),
):
    """
    Upload company target(s): firm name, domain, Google Maps link, or CSV.
    Produces preview; user confirms to start persona discovery (no auto-query).
    """
    err = _check_captcha_if_required(http_request, x_captcha_token)
    if err:
        raise HTTPException(status_code=403, detail=err)

    if not body.company_name and not body.domain and not body.google_maps_url and not body.csv_text:
        raise HTTPException(
            status_code=422,
            detail="Provide at least one of: company_name, domain, google_maps_url, or csv_text",
        )

    upload_id = str(uuid.uuid4())
    client_ip = http_request.client.host if http_request.client else "unknown"
    user_agent = http_request.headers.get("User-Agent")
    risk = getattr(http_request.state, "bot_risk_score", 0.0)

    result = validate_and_parse_company_target(
        company_name=body.company_name,
        domain=body.domain,
        google_maps_url=body.google_maps_url,
        csv_text=body.csv_text,
    )
    payload_sanitized = {
        "company_name": body.company_name[:200] if body.company_name else None,
        "domain": body.domain[:200] if body.domain else None,
        "has_google_maps": bool(body.google_maps_url),
        "csv_rows": len((body.csv_text or "").strip().splitlines()) if body.csv_text else 0,
    }
    store_upload_record(
        upload_id=upload_id,
        upload_type="company_target",
        client_ip=client_ip,
        payload_sanitized=payload_sanitized,
        preview=result,
        abuse_suspicion=risk >= 0.7,
        user_agent=user_agent,
    )
    return CompanyTargetUploadResponse(
        upload_id=upload_id,
        status="received",
        companies=result.get("companies", []),
        preview_count=result.get("preview_count", 0),
        message="Company targets received. Preview ready; confirm to start discovery.",
    )


@router.post("/corporate-signup", response_model=CorporateSignupResponse)
async def corporate_signup(
    body: CorporateSignupRequest,
    http_request: Request,
    db: Session = Depends(get_db),
    x_captcha_token: Optional[str] = Header(None, alias="X-Captcha-Token"),
):
    """
    Şirket e-postası ile kayıt (sign up). Önce kullanıcı oluşturulur; sonra "Giriş linki iste" ile giriş yapılır.
    """
    err = _check_captcha_if_required(http_request, x_captcha_token)
    if err:
        raise HTTPException(status_code=403, detail=err)
    email = (body.email or "").strip().lower()
    if not email:
        raise HTTPException(status_code=422, detail="E-posta gerekli.")
    try:
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            return CorporateSignupResponse(
                success=True,
                message="This email is already registered. Use 'Request login link' to sign in.",
                message_tr="Bu e-posta zaten kayıtlı. Giriş yapmak için 'Giriş linki iste' kullanın.",
            )
        user = User(
            email=email,
            full_name=(body.full_name or "").strip() or None,
            google_id=None,
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info("Corporate signup: user created for %s", email)
    except IntegrityError:
        db.rollback()
        return CorporateSignupResponse(
            success=True,
            message="This email is already registered. Use 'Request login link' to sign in.",
            message_tr="Bu e-posta zaten kayıtlı. Giriş linki iste ile giriş yapın.",
        )
    except Exception as e:
        logger.error("Corporate signup failed: %s", e, exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail="Kayıt işlemi başarısız.")
    return CorporateSignupResponse(
        success=True,
        message="Account created. Use 'Request login link' to receive a sign-in link.",
        message_tr="Hesabınız oluşturuldu. Giriş yapmak için 'Giriş linki iste' butonunu kullanın.",
    )


@router.post("/corporate-login-request", response_model=CorporateLoginResponse)
async def corporate_login_request(
    body: CorporateLoginRequest,
    http_request: Request,
    x_captcha_token: Optional[str] = Header(None, alias="X-Captcha-Token"),
):
    """
    Kullanıcılar şirket e-postası ile giriş talebinde bulunur (zaten kayıtlı olanlar).
    Talep kaydedilir; e-posta ile giriş bilgisi gönderilir (manuel veya otomasyon).
    """
    err = _check_captcha_if_required(http_request, x_captcha_token)
    if err:
        raise HTTPException(status_code=403, detail=err)

    request_id = str(uuid.uuid4())
    client_ip = http_request.client.host if http_request.client else "unknown"
    record = {
        "request_id": request_id,
        "email": body.email,
        "created_at": datetime.utcnow().isoformat(),
        "client_ip": client_ip,
        "status": "pending",
    }
    corp_file = DATA_DIR / "corporate_login_requests.jsonl"
    try:
        corp_file.parent.mkdir(parents=True, exist_ok=True)
        with open(corp_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception as e:
        logger.error("Failed to store corporate login request: %s", e)
        raise HTTPException(status_code=500, detail="Request could not be saved")

    return CorporateLoginResponse(
        success=True,
        message="Request received. We will send you login information to your email.",
        message_tr="Talebiniz alındı. E-posta adresinize giriş bilgisi göndereceğiz.",
    )
