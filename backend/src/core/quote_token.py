"""
CORE: quote_token
PURPOSE: Generate and validate signed quote tokens for query execution
ENCODING: UTF-8 WITHOUT BOM

Implements HMAC-based quote tokens to enforce cost confirmation before query execution.
"""

import os
import hmac
import hashlib
import json
import base64
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from src.config.pricing import QUOTE_TOKEN_EXPIRY_MINUTES, QUOTE_SECRET_ENV_VAR, MAX_RESULTS_PER_QUERY

logger = None
try:
    import logging
    logger = logging.getLogger(__name__)
except:
    pass


def _get_quote_secret() -> str:
    """
    Get quote signing secret from environment.
    Falls back to JWT_SECRET if QUOTE_SECRET not set.
    """
    quote_secret = os.getenv(QUOTE_SECRET_ENV_VAR)
    if not quote_secret:
        # Fallback to JWT_SECRET
        quote_secret = os.getenv("JWT_SECRET")
    if not quote_secret:
        raise ValueError("QUOTE_SECRET or JWT_SECRET must be set for quote token generation")
    return quote_secret


def _create_request_fingerprint(
    include_persona_deepening: bool,
    include_visit_route: bool,
    include_export: bool,
    include_outreach_preparation: bool,
    max_results: int
) -> str:
    """
    Create canonical request fingerprint for quote validation.
    
    Args:
        include_persona_deepening: Persona deepening module flag
        include_visit_route: Visit route module flag
        include_export: Export module flag
        include_outreach_preparation: Outreach preparation module flag
        max_results: Maximum results requested
        
    Returns:
        Canonical fingerprint string
    """
    # Normalize max_results to enforce cap
    normalized_max_results = min(max_results, MAX_RESULTS_PER_QUERY)
    
    # Create canonical string (sorted for consistency)
    fingerprint_data = {
        "persona_deepening": bool(include_persona_deepening),
        "visit_route": bool(include_visit_route),
        "export": bool(include_export),
        "outreach_preparation": bool(include_outreach_preparation),
        "max_results": normalized_max_results
    }
    
    # Sort keys for consistent fingerprint
    canonical = json.dumps(fingerprint_data, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(canonical.encode('utf-8')).hexdigest()


def generate_quote_token(
    total_cost: float,
    include_persona_deepening: bool = False,
    include_visit_route: bool = False,
    include_export: bool = False,
    include_outreach_preparation: bool = False,
    max_results: int = MAX_RESULTS_PER_QUERY
) -> Dict[str, Any]:
    """
    Generate signed quote token for query execution.
    
    Args:
        total_cost: Total cost for the query
        include_persona_deepening: Persona deepening module flag
        include_visit_route: Visit route module flag
        include_export: Export module flag
        include_outreach_preparation: Outreach preparation module flag
        max_results: Maximum results requested (will be clamped to MAX_RESULTS_PER_QUERY)
        
    Returns:
        Dictionary containing quote_token, expires_at, and request_fingerprint
    """
    # Enforce max_results cap
    normalized_max_results = min(max_results, MAX_RESULTS_PER_QUERY)
    
    # Create request fingerprint
    request_fingerprint = _create_request_fingerprint(
        include_persona_deepening=include_persona_deepening,
        include_visit_route=include_visit_route,
        include_export=include_export,
        include_outreach_preparation=include_outreach_preparation,
        max_results=normalized_max_results
    )
    
    # Calculate expiration
    expires_at = datetime.utcnow() + timedelta(minutes=QUOTE_TOKEN_EXPIRY_MINUTES)
    
    # Create payload
    payload = {
        "total_cost": float(total_cost),
        "persona_deepening": bool(include_persona_deepening),
        "visit_route": bool(include_visit_route),
        "export": bool(include_export),
        "outreach_preparation": bool(include_outreach_preparation),
        "max_results": normalized_max_results,
        "request_fingerprint": request_fingerprint,
        "expires_at": expires_at.isoformat(),
        "issued_at": datetime.utcnow().isoformat()
    }
    
    # Encode payload
    payload_json = json.dumps(payload, sort_keys=True, separators=(',', ':'))
    payload_b64 = base64.urlsafe_b64encode(payload_json.encode('utf-8')).decode('utf-8')
    
    # Sign with HMAC
    secret = _get_quote_secret()
    signature = hmac.new(
        secret.encode('utf-8'),
        payload_b64.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    # Create token: payload.signature
    quote_token = f"{payload_b64}.{signature}"
    
    return {
        "quote_token": quote_token,
        "expires_at": expires_at.isoformat(),
        "request_fingerprint": request_fingerprint,
        "max_results": normalized_max_results,
        "total_cost": total_cost
    }


def validate_quote_token(
    quote_token: str,
    include_persona_deepening: bool = False,
    include_visit_route: bool = False,
    include_export: bool = False,
    include_outreach_preparation: bool = False,
    max_results: int = MAX_RESULTS_PER_QUERY
) -> Dict[str, Any]:
    """
    Validate quote token and request fingerprint.
    
    Args:
        quote_token: Quote token from client
        include_persona_deepening: Persona deepening module flag
        include_visit_route: Visit route module flag
        include_export: Export module flag
        include_outreach_preparation: Outreach preparation module flag
        max_results: Maximum results requested
        
    Returns:
        Dictionary with validation result:
        {
            "valid": bool,
            "error": Optional[str],
            "error_code": Optional[str],
            "payload": Optional[dict]
        }
    """
    if not quote_token:
        return {
            "valid": False,
            "error": "Quote token is required",
            "error_code": "QUOTE_TOKEN_MISSING",
            "payload": None
        }
    
    try:
        # Split token into payload and signature
        if '.' not in quote_token:
            return {
                "valid": False,
                "error": "Invalid quote token format",
                "error_code": "QUOTE_TOKEN_INVALID_FORMAT",
                "payload": None
            }
        
        payload_b64, signature = quote_token.rsplit('.', 1)
        
        # Verify signature
        secret = _get_quote_secret()
        expected_signature = hmac.new(
            secret.encode('utf-8'),
            payload_b64.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(signature, expected_signature):
            return {
                "valid": False,
                "error": "Invalid quote token signature",
                "error_code": "QUOTE_TOKEN_INVALID_SIGNATURE",
                "payload": None
            }
        
        # Decode payload
        payload_json = base64.urlsafe_b64decode(payload_b64.encode('utf-8')).decode('utf-8')
        payload = json.loads(payload_json)
        
        # Check expiration
        expires_at_str = payload['expires_at']
        if expires_at_str.endswith('Z'):
            expires_at = datetime.fromisoformat(expires_at_str.replace('Z', '+00:00'))
            expires_at_utc = expires_at.replace(tzinfo=None) if expires_at.tzinfo else expires_at
        else:
            expires_at_utc = datetime.fromisoformat(expires_at_str)
        
        if datetime.utcnow() > expires_at_utc:
            return {
                "valid": False,
                "error": "Quote token has expired",
                "error_code": "QUOTE_TOKEN_EXPIRED",
                "payload": payload
            }
        
        # Validate request fingerprint
        normalized_max_results = min(max_results, MAX_RESULTS_PER_QUERY)
        expected_fingerprint = _create_request_fingerprint(
            include_persona_deepening=include_persona_deepening,
            include_visit_route=include_visit_route,
            include_export=include_export,
            include_outreach_preparation=include_outreach_preparation,
            max_results=normalized_max_results
        )
        
        if payload['request_fingerprint'] != expected_fingerprint:
            return {
                "valid": False,
                "error": "Request fingerprint mismatch. Query parameters do not match quote.",
                "error_code": "QUOTE_TOKEN_FINGERPRINT_MISMATCH",
                "payload": payload
            }
        
        # Validate max_results (enforce cap)
        if max_results > MAX_RESULTS_PER_QUERY:
            return {
                "valid": False,
                "error": f"max_results ({max_results}) exceeds maximum allowed ({MAX_RESULTS_PER_QUERY})",
                "error_code": "MAX_RESULTS_EXCEEDED",
                "payload": payload
            }
        
        # All validations passed
        return {
            "valid": True,
            "error": None,
            "error_code": None,
            "payload": payload
        }
        
    except Exception as e:
        if logger:
            logger.error(f"Error validating quote token: {str(e)}", exc_info=True)
        return {
            "valid": False,
            "error": f"Error validating quote token: {str(e)}",
            "error_code": "QUOTE_TOKEN_VALIDATION_ERROR",
            "payload": None
        }
