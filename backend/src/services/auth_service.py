"""
SERVICE: auth_service
PURPOSE: Google OAuth2 authentication and JWT token generation
ENCODING: UTF-8 WITHOUT BOM
"""

import os
import logging
from typing import Dict, Optional, Any
from datetime import datetime, timedelta

from src.config.settings import get_int_env

logger = logging.getLogger(__name__)

try:
    from fastapi import Header, Depends, HTTPException
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    from sqlalchemy.orm import Session
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    Header = None
    Depends = None
    HTTPException = None
    HTTPBearer = None
    HTTPAuthorizationCredentials = None
    Session = None

# Import get_db at module level (will be used in dependency)
try:
    from src.db.base import get_db
except ImportError:
    get_db = None

# Import Secret Manager
try:
    from src.core.secret_manager import get_secret_manager
    SECRET_MANAGER_AVAILABLE = True
except ImportError:
    SECRET_MANAGER_AVAILABLE = False
    get_secret_manager = None

try:
    import jwt
    JWT_AVAILABLE = True
except ImportError:
    try:
        import PyJWT as jwt
        JWT_AVAILABLE = True
    except ImportError:
        JWT_AVAILABLE = False
        jwt = None

try:
    from google.oauth2 import id_token
    from google.auth.transport import requests
    GOOGLE_AUTH_AVAILABLE = True
except ImportError:
    GOOGLE_AUTH_AVAILABLE = False


class AuthService:
    """
    Service for Google OAuth2 authentication and JWT token generation.
    """
    
    def __init__(self):
        """
        Initialize Auth Service with configuration from Secret Manager (production) 
        or environment variables (development).
        """
        # Initialize Secret Manager (with fallback to env vars)
        if SECRET_MANAGER_AVAILABLE:
            secret_mgr = get_secret_manager()
            self.google_client_id = secret_mgr.get_secret("GOOGLE_CLIENT_ID")
            self.jwt_secret = secret_mgr.get_secret("JWT_SECRET")
        else:
            # Fallback to environment variables if Secret Manager not available
            self.google_client_id = os.getenv("GOOGLE_CLIENT_ID")
            self.jwt_secret = os.getenv("JWT_SECRET")
        
        # These can remain as env vars (not sensitive). Production: max 24h.
        self.jwt_algorithm = os.getenv("JWT_ALGORITHM") or "HS256"
        _exp = get_int_env("JWT_EXPIRATION_HOURS", 24)
        if (os.getenv("ENV") or "").strip().lower() == "production":
            _exp = min(24, max(1, _exp))
        self.jwt_expiration_hours = _exp
        if self.jwt_secret and len(self.jwt_secret) < 32:
            logger.warning("JWT_SECRET length < 32; consider a stronger secret for production.")
    
    def is_configured(self) -> bool:
        """Check if authentication service is properly configured."""
        return bool(self.google_client_id and self.jwt_secret)
    
    def verify_google_token(self, id_token_string: str) -> Dict[str, Any]:
        """
        Verify Google id_token and extract user information.
        
        Args:
            id_token_string: Google OAuth2 id_token from client
        
        Returns:
            Dictionary containing:
                - success: bool
                - user_info: Dict with email, name, picture, google_id
                - error: Error message if verification fails
        """
        if not GOOGLE_AUTH_AVAILABLE:
            return {
                "success": False,
                "error": "Google Auth library not available. Install: pip install google-auth"
            }
        
        if not self.google_client_id:
            return {
                "success": False,
                "error": "GOOGLE_CLIENT_ID not configured"
            }
        
        try:
            # Verify the token
            request = requests.Request()
            idinfo = id_token.verify_oauth2_token(
                id_token_string,
                request,
                self.google_client_id
            )
            
            # Verify the issuer
            if idinfo.get('iss') not in ('accounts.google.com', 'https://accounts.google.com'):
                return {
                    "success": False,
                    "error": "Invalid token issuer"
                }
            # Explicit audience check: must match GOOGLE_CLIENT_ID (fail clearly on mismatch)
            aud = idinfo.get('aud')
            if aud != self.google_client_id:
                return {
                    "success": False,
                    "error": "Token audience does not match GOOGLE_CLIENT_ID. Check frontend and backend use the same OAuth client."
                }
            
            # Extract user information
            user_info = {
                "google_id": idinfo.get('sub'),
                "email": idinfo.get('email'),
                "email_verified": idinfo.get('email_verified', False),
                "full_name": idinfo.get('name'),
                "given_name": idinfo.get('given_name'),
                "family_name": idinfo.get('family_name'),
                "profile_picture": idinfo.get('picture'),
                "locale": idinfo.get('locale')
            }
            
            return {
                "success": True,
                "user_info": user_info
            }
            
        except ValueError as e:
            return {
                "success": False,
                "error": f"Token verification failed: {str(e)}"
            }
        except Exception as e:
            logger.warning("Google id_token verification error: %s", e, exc_info=False)
            return {
                "success": False,
                "error": "Error verifying token (see server logs for details)."
            }
    
    def generate_jwt_token(
        self,
        user_id: int,
        email: str,
        google_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate JWT token for authenticated user.
        
        Args:
            user_id: User ID from database
            email: User email
            google_id: Google ID (optional)
        
        Returns:
            Dictionary containing:
                - success: bool
                - token: JWT token string
                - expires_at: Token expiration timestamp
                - error: Error message if generation fails
        """
        if not self.jwt_secret:
            return {
                "success": False,
                "error": "JWT_SECRET not configured"
            }
        
        if not JWT_AVAILABLE:
            return {
                "success": False,
                "error": "JWT library not available. Install: pip install PyJWT"
            }
        
        try:
            # Calculate expiration time
            expires_at = datetime.utcnow() + timedelta(hours=self.jwt_expiration_hours)
            
            # Create payload
            payload = {
                "user_id": user_id,
                "email": email,
                "google_id": google_id,
                "exp": expires_at,
                "iat": datetime.utcnow(),
                "type": "access"
            }
            
            # Generate token
            token = jwt.encode(
                payload,
                self.jwt_secret,
                algorithm=self.jwt_algorithm
            )
            
            return {
                "success": True,
                "token": token,
                "expires_at": expires_at.isoformat(),
                "expires_in": self.jwt_expiration_hours * 3600   # seconds
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error generating JWT token: {str(e)}"
            }
    
    def verify_jwt_token(self, token: str) -> Dict[str, Any]:
        """
        Verify and decode JWT token.
        
        Args:
            token: JWT token string
        
        Returns:
            Dictionary containing:
                - success: bool
                - payload: Decoded token payload
                - error: Error message if verification fails
        """
        if not JWT_AVAILABLE:
            return {
                "success": False,
                "error": "JWT library not available. Install: pip install PyJWT"
            }
        
        if not self.jwt_secret:
            return {
                "success": False,
                "error": "JWT_SECRET not configured"
            }
        
        try:
            # Decode and verify token
            payload = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=[self.jwt_algorithm]
            )
            
            return {
                "success": True,
                "payload": payload
            }
            
        except jwt.ExpiredSignatureError:
            return {
                "success": False,
                "error": "Token has expired"
            }
        except jwt.InvalidTokenError as e:
            return {
                "success": False,
                "error": f"Invalid token: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error verifying token: {str(e)}"
            }
    
    def authenticate_google_user(self, id_token_string: str) -> Dict[str, Any]:
        """
        Complete authentication flow: verify Google token and generate JWT.
        
        Args:
            id_token_string: Google OAuth2 id_token
        
        Returns:
            Dictionary containing:
                - success: bool
                - user_info: User information from Google
                - jwt_token: Generated JWT token (if user_id provided)
                - error: Error message if authentication fails
        """
        # Step 1: Verify Google token
        verify_result = self.verify_google_token(id_token_string)
        
        if not verify_result.get("success"):
            return verify_result
        
        user_info = verify_result.get("user_info", {})
        
        # Return user info (JWT will be generated after user is created/retrieved from DB)
        return {
            "success": True,
            "user_info": user_info
        }
    
    def create_auth_response(
        self,
        user_id: int,
        user_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create complete authentication response with JWT token.
        
        Args:
            user_id: User ID from database
            user_info: User information dictionary
        
        Returns:
            Complete authentication response
        """
        # Generate JWT token
        jwt_result = self.generate_jwt_token(
            user_id=user_id,
            email=user_info.get("email", ""),
            google_id=user_info.get("google_id")
        )
        
        if not jwt_result.get("success"):
            return jwt_result
        
        logger.info("jwt_token_issued user_id=%s exp_hours=%s", user_id, self.jwt_expiration_hours)
        return {
            "success": True,
            "user": {
                "id": user_id,
                "email": user_info.get("email"),
                "full_name": user_info.get("full_name"),
                "profile_picture": user_info.get("profile_picture"),
                "google_id": user_info.get("google_id")
            },
            "token": jwt_result.get("token"),
            "expires_at": jwt_result.get("expires_at"),
            "expires_in": jwt_result.get("expires_in")
        }


# Singleton instance
_auth_service_instance = None


def get_auth_service() -> AuthService:
    """Get or create AuthService singleton instance."""
    global _auth_service_instance
    if _auth_service_instance is None:
        _auth_service_instance = AuthService()
    return _auth_service_instance


# Admin emails: SOARB2B_ADMIN_EMAILS (comma-separated) + isanli058@gmail.com
def get_admin_emails() -> list:
    """Return list of emails allowed as admin (env SOARB2B_ADMIN_EMAILS + isanli058@gmail.com)."""
    env_val = os.getenv("SOARB2B_ADMIN_EMAILS", "")
    emails = [e.strip().lower() for e in env_val.split(",") if e.strip()]
    direct = "isanli058@gmail.com"
    if direct not in emails:
        emails.append(direct)
    return emails


def is_admin_email(email: Optional[str]) -> bool:
    """Return True if email is in admin list (payment/quote and plan limits bypass)."""
    if not email or not isinstance(email, str):
        return False
    return email.strip().lower() in get_admin_emails()


def get_email_from_jwt(authorization: Optional[str]) -> Optional[str]:
    """If Authorization is valid Bearer JWT, return payload email; else None. No exception."""
    if not authorization or not authorization.strip().lower().startswith("bearer "):
        return None
    token = authorization[7:].strip()
    if not token:
        return None
    auth_service = get_auth_service()
    if not auth_service.is_configured():
        return None
    result = auth_service.verify_jwt_token(token)
    if not result.get("success"):
        return None
    return (result.get("payload") or {}).get("email")


# Implementation function (called by both dependency wrapper and helper functions)
def get_current_user_impl(
    authorization: Optional[str],
    db: Session
) -> "User":
    """
    FastAPI Dependency function to get current authenticated user from JWT token.
    
    Reads JWT token from 'Authorization' header in format: "Bearer <token>"
    
    Usage:
        from fastapi import Depends
        from src.services.auth_service import get_current_user_dependency
        from src.models.user import User
        from src.db.base import get_db
        
        @router.get("/protected")
        async def protected_route(
            user: User = Depends(get_current_user_dependency)
        ):
            return {"user_id": user.id, "email": user.email}
    
    Args:
        authorization: Authorization header value (from FastAPI Header dependency)
        db: Database session (from FastAPI Depends)
    
    Returns:
        User object if authentication successful
    
    Raises:
        HTTPException: If token is missing, invalid, or user not found
    """
    if not FASTAPI_AVAILABLE:
        raise RuntimeError("FastAPI is required for get_current_user_dependency")
    
    from src.models.user import User
    
    # Check authorization header
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Extract token from "Bearer <token>" format
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header format. Expected: Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    token = authorization.replace("Bearer ", "").strip()
    
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Token missing",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Verify token
    auth_service = get_auth_service()
    
    if not auth_service.is_configured():
        raise HTTPException(
            status_code=503,
            detail="Authentication service is not configured"
        )
    
    verify_result = auth_service.verify_jwt_token(token)
    
    if not verify_result.get("success"):
        raise HTTPException(
            status_code=401,
            detail=verify_result.get("error", "Invalid token"),
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Get user_id from token payload
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
    
    return user


# FastAPI Dependency wrapper (uses Depends for db)
def get_current_user_dependency(
    authorization: Optional[str] = Header(None, alias="Authorization"),
    db: Session = Depends(get_db)
) -> "User":
    """
    FastAPI Dependency function to get current authenticated user from JWT token.
    
    This is the wrapper that should be used with Depends() in route handlers.
    For direct calls with explicit db parameter, use get_current_user_impl instead.
    """
    return get_current_user_impl(authorization, db)

