"""
ROUTER: auth_router (FIXED VERSION)
PURPOSE: Authentication endpoints for Google OAuth2 with proper exception handling
ENCODING: UTF-8 WITHOUT BOM
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import logging

from src.services.auth_service import get_auth_service
from src.models.user import User
from src.db.base import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])


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
    Authenticate user with Google OAuth2 id_token.
    Creates new user if doesn't exist, otherwise returns existing user.
    Returns JWT token for application authentication.
    """
    try:
        # Ensure database tables exist (lazy initialization)
        try:
            from src.db.base import Base, engine
            Base.metadata.create_all(bind=engine, checkfirst=True)
        except Exception as db_init_error:
            logger.warning(f"Database initialization warning: {str(db_init_error)}")
        
        auth_service = get_auth_service()
        
        if not auth_service.is_configured():
            return GoogleAuthResponse(
                success=False,
                error="Authentication service is not configured. Please set GOOGLE_CLIENT_ID and JWT_SECRET."
            )
        
        # Step 1: Verify Google token
        verify_result = auth_service.verify_google_token(request.id_token)
        
        if not verify_result.get("success"):
            logger.warning(f"Token verification failed: {verify_result.get('error')}")
            return GoogleAuthResponse(
                success=False,
                error=verify_result.get("error", "Token verification failed")
            )
        
        user_info = verify_result.get("user_info", {})
        google_id = user_info.get("google_id")
        email = user_info.get("email")
        
        if not email:
            return GoogleAuthResponse(
                success=False,
                error="Email not found in Google token"
            )
        
        # Step 2: Find or create user
        user = None
        
        try:
            # Try to find by google_id first
            if google_id:
                user = db.query(User).filter(User.google_id == google_id).first()
            
            # If not found, try by email
            if not user:
                user = db.query(User).filter(User.email == email).first()
            
            # Create new user if doesn't exist
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
                    logger.info(f"Created new user: {email}")
                except IntegrityError as e:
                    db.rollback()
                    logger.info(f"User already exists (IntegrityError), fetching: {email}")
                    # User might have been created by another request, try to fetch again
                    if google_id:
                        user = db.query(User).filter(User.google_id == google_id).first()
                    if not user:
                        user = db.query(User).filter(User.email == email).first()
                    if not user:
                        logger.error(f"Failed to fetch user after IntegrityError: {email}")
                        return GoogleAuthResponse(
                            success=False,
                            error="Database error: Failed to create or retrieve user"
                        )
            else:
                # Update existing user with latest Google info
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
            
            # Step 3: Generate JWT token
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
            
            logger.info(f"Successfully authenticated user: {email}")
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
            logger.error(f"Database error in authenticate_google: {str(db_error)}", exc_info=True)
            return GoogleAuthResponse(
                success=False,
                error="Database error: Unable to process authentication. Please try again."
            )
    except Exception as e:
        logger.error(f"Unexpected error in authenticate_google: {str(e)}", exc_info=True)
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
    
    # Verify token
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
    
    # Get user from database
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


@router.get("/config")
def get_auth_config():
    """
    Get public authentication configuration (Client ID for Google Sign-In).
    This endpoint is public and only returns non-sensitive configuration.
    """
    auth_service = get_auth_service()
    
    if not auth_service.is_configured():
        raise HTTPException(
            status_code=503,
            detail="Authentication service is not configured"
        )
    
    return {
        "google_client_id": auth_service.google_client_id,
        "oauth_enabled": True
    }
