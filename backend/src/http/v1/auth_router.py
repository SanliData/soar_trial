"""
ROUTER: auth_router (FIXED VERSION)
PURPOSE: Authentication endpoints for Google OAuth2, LinkedIn OAuth2, proper exception handling
ENCODING: UTF-8 WITHOUT BOM
"""

import os
import secrets
import hmac
import hashlib
import base64
import logging
import time
from typing import Optional
from urllib.parse import urlencode

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import requests

from src.config.settings import get_settings
from src.services.auth_service import get_auth_service
from src.models.user import User
from src.db.base import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])

***REMOVED*** OAuth state: signed with HMAC so we can verify on callback without server-side store
STATE_TTL_SEC = 600  ***REMOVED*** 10 minutes


def _oauth_log(event: str, **kwargs: object) -> None:
    """Structured OAuth log (INFO in production)."""
    logger.info("oauth_flow event=%s %s", event, " ".join(f"{k}={v!r}" for k, v in kwargs.items()))


def _base_url(request: Request) -> str:
    """Backend base URL: from settings in production, else request.base_url (no localhost hardcode)."""
    try:
        s = get_settings()
        if s.ENV == "production" and s.BASE_URL and s.BASE_URL.strip():
            return s.BASE_URL.strip().rstrip("/")
    except Exception:
        pass
    return str(request.base_url).rstrip("/")


def _frontend_redirect_base(request: Request) -> str:
    """Origin/URL for post-login redirect (FRONTEND_ORIGIN or BASE_URL or request)."""
    try:
        s = get_settings()
        if s.FRONTEND_ORIGIN and s.FRONTEND_ORIGIN.strip():
            return s.FRONTEND_ORIGIN.strip().rstrip("/")
        if s.BASE_URL and s.BASE_URL.strip():
            return s.BASE_URL.strip().rstrip("/")
    except Exception:
        pass
    base = str(request.base_url).rstrip("/")
    if "/api" in base:
        return base.replace("/api", "").rstrip("/") or base
    return base


def _make_signed_state() -> str:
    """Create state value with timestamp and HMAC signature (CSRF protection)."""
    raw = f"{time.time():.0f}:{secrets.token_urlsafe(24)}"
    secret = (os.getenv("JWT_SECRET") or "").encode("utf-8") or b"oauth-state-secret"
    sig = base64.urlsafe_b64encode(hmac.new(secret, raw.encode("utf-8"), hashlib.sha256).digest()).decode("ascii").rstrip("=")
    return base64.urlsafe_b64encode(raw.encode("utf-8")).decode("ascii").rstrip("=") + "." + sig


def _verify_signed_state(state: str) -> bool:
    """Verify state signature and TTL. Returns True if valid."""
    if not state or "." not in state:
        return False
    try:
        raw_b64, sig_b64 = state.split(".", 1)
        raw = base64.urlsafe_b64decode(raw_b64 + "==").decode("utf-8")
        ts_str, _ = raw.split(":", 1)
        ts = float(ts_str)
        if time.time() - ts > STATE_TTL_SEC or time.time() - ts < -60:
            return False
        secret = (os.getenv("JWT_SECRET") or "").encode("utf-8") or b"oauth-state-secret"
        expected = base64.urlsafe_b64encode(hmac.new(secret, raw.encode("utf-8"), hashlib.sha256).digest()).decode("ascii").rstrip("=")
        return hmac.compare_digest(sig_b64, expected)
    except Exception:
        return False

***REMOVED*** Google OAuth: frontend sends id_token to POST /v1/auth/google. No server-side redirect/callback endpoint.
LINKEDIN_AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
LINKEDIN_TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
LINKEDIN_USERINFO_URL = "https://api.linkedin.com/v2/userinfo"
LINKEDIN_SCOPES = "openid profile email"


class GoogleAuthRequest(BaseModel):
    id_token: str


class GoogleAuthResponse(BaseModel):
    success: bool
    user: Optional[dict] = None
    token: Optional[str] = None
    expires_at: Optional[str] = None
    expires_in: Optional[int] = None
    error: Optional[str] = None


class VerifyTokenRequest(BaseModel):
    token: str


class VerifyTokenResponse(BaseModel):
    success: bool
    payload: Optional[dict] = None
    error: Optional[str] = None


@router.post("/google", response_model=GoogleAuthResponse)
async def authenticate_google(
    request: GoogleAuthRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user with Google OAuth2 id_token (from frontend Sign in with Google).
    Creates new user if doesn't exist, otherwise returns existing user.
    Returns JWT token for application authentication.
    """
    _oauth_log("google_login_started")
    try:
        ***REMOVED*** Ensure database tables exist (lazy initialization)
        try:
            from src.db.base import Base, engine
            Base.metadata.create_all(bind=engine, checkfirst=True)
        except Exception as db_init_error:
            logger.warning("Database initialization warning: %s", db_init_error)
        
        auth_service = get_auth_service()
        
        if not auth_service.is_configured():
            _oauth_log("google_login_failed", reason="auth_not_configured")
            return GoogleAuthResponse(
                success=False,
                error="Authentication service is not configured. Please set GOOGLE_CLIENT_ID and JWT_SECRET."
            )
        
        _oauth_log("google_id_token_received")
        ***REMOVED*** Step 1: Verify Google token (audience == GOOGLE_CLIENT_ID enforced in auth_service)
        verify_result = auth_service.verify_google_token(request.id_token)
        
        if not verify_result.get("success"):
            _oauth_log("google_login_failed", reason="token_verification_failed", error=verify_result.get("error"))
            logger.warning("Token verification failed: %s", verify_result.get("error"))
            return GoogleAuthResponse(
                success=False,
                error=verify_result.get("error", "Token verification failed")
            )
        
        _oauth_log("google_token_verified")
        user_info = verify_result.get("user_info", {})
        google_id = user_info.get("google_id")
        email = user_info.get("email")
        
        if not email:
            _oauth_log("google_login_failed", reason="email_not_in_token")
            return GoogleAuthResponse(
                success=False,
                error="Email not found in Google token"
            )
        
        ***REMOVED*** Step 2: Find or create user
        user = None
        
        try:
            ***REMOVED*** Try to find by google_id first
            if google_id:
                user = db.query(User).filter(User.google_id == google_id).first()
            
            ***REMOVED*** If not found, try by email
            if not user:
                user = db.query(User).filter(User.email == email).first()
            
            ***REMOVED*** Create new user if doesn't exist
            if not user:
                try:
                    user = User(
                        email=email,
                        full_name=user_info.get("full_name"),
                        google_id=google_id,
                        profile_picture=user_info.get("profile_picture"),
                        is_active=True
                    )
                    db.add(user)
                    db.commit()
                    db.refresh(user)
                    _oauth_log("google_user_created", email=email)
                    logger.info("Created new user: %s", email)
                except IntegrityError as e:
                    db.rollback()
                    logger.info(f"User already exists (IntegrityError), fetching: {email}")
                    ***REMOVED*** User might have been created by another request, try to fetch again
                    if google_id:
                        user = db.query(User).filter(User.google_id == google_id).first()
                    if not user:
                        user = db.query(User).filter(User.email == email).first()
                    if not user:
                        _oauth_log("google_login_failed", reason="db_fetch_after_integrity")
                        logger.error("Failed to fetch user after IntegrityError: %s", email)
                        return GoogleAuthResponse(
                            success=False,
                            error="Database error: Failed to create or retrieve user"
                        )
            else:
                ***REMOVED*** Update existing user with latest Google info
                updated = False
                if google_id and not user.google_id:
                    user.google_id = google_id
                    updated = True
                if user_info.get("full_name") and not user.full_name:
                    user.full_name = user_info.get("full_name")
                    updated = True
                if user_info.get("profile_picture") and user.profile_picture != user_info.get("profile_picture"):
                    user.profile_picture = user_info.get("profile_picture")
                    updated = True
                if not user.is_active:
                    user.is_active = True
                    updated = True
                
                if updated:
                    try:
                        db.commit()
                        db.refresh(user)
                    except IntegrityError as e:
                        db.rollback()
                        logger.error(f"Failed to update user: {str(e)}")
                        return GoogleAuthResponse(
                            success=False,
                            error="Database error: Failed to update user"
                        )
            
            if not user:
                return GoogleAuthResponse(
                    success=False,
                    error="Failed to create or retrieve user"
                )
            
            ***REMOVED*** Step 3: Generate JWT token
            jwt_result = auth_service.create_auth_response(
                user_id=user.id,
                user_info={
                    "email": user.email,
                    "full_name": user.full_name,
                    "profile_picture": user.profile_picture,
                    "google_id": user.google_id
                }
            )
            
            if not jwt_result.get("success"):
                logger.error(f"JWT generation failed: {jwt_result.get('error')}")
                return GoogleAuthResponse(
                    success=False,
                    error=jwt_result.get("error", "Failed to generate token")
                )
            
            _oauth_log("google_user_logged_in", email=email)
            logger.info("Successfully authenticated user: %s", email)
            return GoogleAuthResponse(
                success=True,
                user={
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "profile_picture": user.profile_picture,
                    "google_id": user.google_id,
                    "is_active": user.is_active
                },
                token=jwt_result.get("token"),
                expires_at=jwt_result.get("expires_at"),
                expires_in=jwt_result.get("expires_in")
            )
        except Exception as db_error:
            db.rollback()
            _oauth_log("google_login_failed", reason="database_error")
            is_prod = (os.getenv("ENV") or "").strip().lower() == "production"
            logger.error("Database error in authenticate_google: %s%s", db_error, "" if is_prod else " (see trace)", exc_info=not is_prod)
            return GoogleAuthResponse(
                success=False,
                error="Database error: Unable to process authentication. Please try again."
            )
    except Exception as e:
        _oauth_log("google_login_failed", reason="unexpected")
        is_prod = (os.getenv("ENV") or "").strip().lower() == "production"
        logger.error("Unexpected error in authenticate_google: %s%s", e, "" if is_prod else " (see trace)", exc_info=not is_prod)
        return GoogleAuthResponse(
            success=False,
            error="Internal server error. Please try again later."
        )


@router.post("/verify", response_model=VerifyTokenResponse)
async def verify_token(request: VerifyTokenRequest):
    """
    Verify JWT token and return payload.
    """
    auth_service = get_auth_service()
    
    if not auth_service.is_configured():
        raise HTTPException(
            status_code=503,
            detail="Authentication service is not configured"
        )
    
    result = auth_service.verify_jwt_token(request.token)
    
    if not result.get("success"):
        return VerifyTokenResponse(
            success=False,
            error=result.get("error", "Token verification failed")
        )
    
    return VerifyTokenResponse(
        success=True,
        payload=result.get("payload")
    )


@router.get("/me")
async def get_current_user(
    token: str,
    db: Session = Depends(get_db)
):
    """
    Get current user information from JWT token.
    """
    auth_service = get_auth_service()
    
    if not auth_service.is_configured():
        raise HTTPException(
            status_code=503,
            detail="Authentication service is not configured"
        )
    
    ***REMOVED*** Verify token
    verify_result = auth_service.verify_jwt_token(token)
    
    if not verify_result.get("success"):
        raise HTTPException(
            status_code=401,
            detail=verify_result.get("error", "Invalid token")
        )
    
    payload = verify_result.get("payload", {})
    user_id = payload.get("user_id")
    
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid token payload"
        )
    
    ***REMOVED*** Get user from database
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="User account is inactive"
        )
    
    return {
        "success": True,
        "user": user.to_dict()
    }


@router.get("/health")
def health():
    """Check health status of authentication service."""
    auth_service = get_auth_service()
    
    return {
        "status": "ok",
        "domain": "authentication",
        "configured": auth_service.is_configured(),
        "google_client_id_set": bool(auth_service.google_client_id),
        "jwt_secret_set": bool(auth_service.jwt_secret)
    }


@router.get("/debug-config")
def debug_config(request: Request):
    """
    Production-safe debug: base_url, frontend_origin, google_client_id_present.
    No secrets or token content returned.
    """
    try:
        s = get_settings()
        base_url = (s.BASE_URL or "").strip() or str(request.base_url).rstrip("/")
        frontend_origin = (s.FRONTEND_ORIGIN or "").strip() or base_url
        google_client_id_present = bool((s.GOOGLE_CLIENT_ID or "").strip())
    except Exception:
        base_url = str(request.base_url).rstrip("/")
        frontend_origin = base_url
        google_client_id_present = bool(os.getenv("GOOGLE_CLIENT_ID", "").strip())
    return {
        "base_url": base_url,
        "frontend_origin": frontend_origin,
        "google_client_id_present": google_client_id_present,
    }


@router.get("/config")
def get_auth_config(request: Request):
    """
    Get public authentication configuration (Google Client ID, LinkedIn auth URL).
    Uses BASE_URL in production for consistent redirect URIs.
    """
    auth_service = get_auth_service()
    base = _base_url(request)
    linkedin_client_id = os.getenv("LINKEDIN_CLIENT_ID", "").strip()
    linkedin_enabled = bool(linkedin_client_id and auth_service.jwt_secret)
    linkedin_auth_url = f"{base}/v1/auth/linkedin" if linkedin_enabled else None

    if not auth_service.is_configured():
        is_production = (os.getenv("ENV") or "").strip().lower() == "production"
        if is_production:
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=503,
                content={
                    "error": "Authentication service is not configured",
                    "google_client_id": None,
                    "oauth_enabled": False,
                    "linkedin_enabled": False,
                    "linkedin_auth_url": None,
                }
            )
        return {
            "enabled": False,
            "google_client_id": None,
            "oauth_enabled": False,
            "linkedin_enabled": linkedin_enabled,
            "linkedin_auth_url": linkedin_auth_url,
        }

    return {
        "enabled": True,
        "provider": "google",
        "google_client_id": auth_service.google_client_id,
        "oauth_enabled": True,
        "linkedin_enabled": linkedin_enabled,
        "linkedin_auth_url": linkedin_auth_url,
    }


@router.get("/linkedin")
async def linkedin_login(request: Request):
    """Redirect to LinkedIn OAuth2 authorization. Requires LINKEDIN_CLIENT_ID and JWT_SECRET."""
    _oauth_log("login_start", provider="linkedin")
    client_id = os.getenv("LINKEDIN_CLIENT_ID", "").strip()
    if not client_id:
        _oauth_log("failure_reason", reason="linkedin_not_configured", provider="linkedin")
        raise HTTPException(status_code=503, detail="LinkedIn login is not configured (LINKEDIN_CLIENT_ID).")
    base = _base_url(request)
    redirect_uri = f"{base}/v1/auth/linkedin/callback"
    state = _make_signed_state()
    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "state": state,
        "scope": LINKEDIN_SCOPES,
    }
    url = f"{LINKEDIN_AUTH_URL}?{urlencode(params)}"
    return RedirectResponse(url=url)


@router.get("/linkedin/callback")
async def linkedin_callback(
    request: Request,
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Exchange LinkedIn code for token, get profile, create/find user, redirect with JWT."""
    base_ui = _frontend_redirect_base(request)
    _oauth_log("callback_received", provider="linkedin", has_code=bool(code), has_state=bool(state), error=error)
    if error:
        _oauth_log("failure_reason", reason="oauth_error", error=error, provider="linkedin")
        logger.warning("LinkedIn OAuth error: %s", error)
        return RedirectResponse(url=f"{base_ui}/ui/tr/soarb2b_home.html?linkedin_error=1")
    if not code:
        _oauth_log("failure_reason", reason="missing_code", provider="linkedin")
        raise HTTPException(status_code=400, detail="Missing code from LinkedIn")
    if not state or not _verify_signed_state(state):
        _oauth_log("failure_reason", reason="invalid_state", provider="linkedin")
        logger.warning("LinkedIn callback: invalid or expired state")
        return RedirectResponse(url=f"{base_ui}/ui/tr/soarb2b_home.html?linkedin_error=6")
    client_id = os.getenv("LINKEDIN_CLIENT_ID", "").strip()
    client_secret = os.getenv("LINKEDIN_CLIENT_SECRET", "").strip()
    if not client_id or not client_secret:
        _oauth_log("failure_reason", reason="linkedin_not_configured", provider="linkedin")
        raise HTTPException(status_code=503, detail="LinkedIn login is not configured.")
    base = _base_url(request)
    redirect_uri = f"{base}/v1/auth/linkedin/callback"
    try:
        token_resp = requests.post(
            LINKEDIN_TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri,
                "client_id": client_id,
                "client_secret": client_secret,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10,
        )
    except Exception as e:
        _oauth_log("failure_reason", reason="token_request_error", provider="linkedin")
        logger.warning("LinkedIn token request failed: %s", e)
        return RedirectResponse(url=f"{base_ui}/ui/tr/soarb2b_home.html?linkedin_error=2")
    if not token_resp.ok:
        _oauth_log("failure_reason", reason="token_exchange_failed", status=token_resp.status_code, provider="linkedin")
        logger.warning("LinkedIn token error: %s %s", token_resp.status_code, token_resp.text[:200])
        return RedirectResponse(url=f"{base_ui}/ui/tr/soarb2b_home.html?linkedin_error=2")
    token_data = token_resp.json()
    access_token = token_data.get("access_token")
    if not access_token:
        _oauth_log("failure_reason", reason="no_access_token", provider="linkedin")
        return RedirectResponse(url=f"{base_ui}/ui/tr/soarb2b_home.html?linkedin_error=3")
    _oauth_log("token_exchanged", provider="linkedin")
    try:
        user_resp = requests.get(
            LINKEDIN_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10,
        )
    except Exception as e:
        _oauth_log("failure_reason", reason="userinfo_request_error", provider="linkedin")
        logger.warning("LinkedIn userinfo request failed: %s", e)
        return RedirectResponse(url=f"{base_ui}/ui/tr/soarb2b_home.html?linkedin_error=4")
    if not user_resp.ok:
        _oauth_log("failure_reason", reason="userinfo_failed", status=user_resp.status_code, provider="linkedin")
        logger.warning("LinkedIn userinfo error: %s", user_resp.status_code)
        return RedirectResponse(url=f"{base_ui}/ui/tr/soarb2b_home.html?linkedin_error=4")
    user_info_linkedin = user_resp.json()
    email = (user_info_linkedin.get("email") or "").strip()
    name = (user_info_linkedin.get("name") or "").strip()
    if not email:
        _oauth_log("failure_reason", reason="no_email", provider="linkedin")
        return RedirectResponse(url=f"{base_ui}/ui/tr/soarb2b_home.html?linkedin_error=5")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        try:
            user = User(email=email, full_name=name or None, google_id=None, is_active=True)
            db.add(user)
            db.commit()
            db.refresh(user)
            _oauth_log("user_created", email=email, provider="linkedin")
            logger.info("LinkedIn signup: user created for %s", email)
        except IntegrityError:
            db.rollback()
            user = db.query(User).filter(User.email == email).first()
    if not user:
        _oauth_log("failure_reason", reason="user_creation_failed", provider="linkedin")
        raise HTTPException(status_code=500, detail="User could not be created")
    auth_service = get_auth_service()
    user_info = {"email": user.email, "full_name": user.full_name, "google_id": None}
    response_data = auth_service.create_auth_response(user.id, user_info)
    jwt_token = response_data.get("token")
    if not jwt_token:
        _oauth_log("failure_reason", reason="jwt_failed", provider="linkedin")
        raise HTTPException(status_code=500, detail="JWT could not be generated")
    _oauth_log("user_logged_in", email=email, provider="linkedin")
    redirect_to = f"{base_ui}/ui/tr/soarb2b_home.html?token={jwt_token}"
    return RedirectResponse(url=redirect_to)
