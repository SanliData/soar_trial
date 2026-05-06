"""
ROUTER: support_router
PURPOSE: Customer support endpoints (contact form, support messages)
ENCODING: UTF-8 WITHOUT BOM
"""

import os
import json
import uuid
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field, EmailStr
from src.middleware.locale_middleware import get_locale_from_request
from src.core.messages import get_support_received_message

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/support", tags=["support"])

# Data directory
DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)


# Request Models
class SupportMessageRequest(BaseModel):
    """Support message request"""
    name: str = Field(..., description="Contact name")
    email: EmailStr = Field(..., description="Contact email")
    subject: str = Field(..., description="Message subject")
    message: str = Field(..., description="Message content")
    language: Optional[str] = Field("en", description="Language code")


class SupportMessageResponse(BaseModel):
    """Support message response"""
    message_id: str
    status: str
    message: str
    created_at: str


# Endpoints
@router.post("/contact", response_model=SupportMessageResponse)
async def send_support_message(
    request: SupportMessageRequest,
    http_request: Request
):
    """
    Send a support message.
    Stores message to file and returns confirmation.
    """
    message_id = str(uuid.uuid4())
    created_at = datetime.utcnow().isoformat()
    
    # Get client IP
    client_ip = http_request.client.host if http_request.client else "unknown"
    
    # Get referrer
    referrer_url = http_request.headers.get("referer", "unknown")
    
    # Store message
    message_data = {
        "message_id": message_id,
        "name": request.name,
        "email": request.email,
        "subject": request.subject,
        "message": request.message,
        "language": request.language,
        "created_at": created_at,
        "client_ip": client_ip,
        "referrer_url": referrer_url,
        "status": "pending"
    }
    
    # Store to JSONL file
    messages_file = DATA_DIR / "support_messages.jsonl"
    try:
        with open(messages_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(message_data, ensure_ascii=False) + "\n")
    except Exception as e:
        logger.error(f"Failed to store support message: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to process support message"
        )
    
    # Log message
    logger.info(
        json.dumps({
            "event": "support_message_created",
            "message_id": message_id,
            "timestamp": created_at,
            "language": request.language,
            "subject": request.subject,
            "email": request.email
        }, ensure_ascii=False)
    )
    
    # Get locale from request (prefer request locale, fallback to Accept-Language header)
    locale = request.language if request.language and request.language in ["tr", "en", "de", "es", "fr", "ar"] else get_locale_from_request(http_request)
    
    # Get language-aware message
    response_message = get_support_received_message(locale)
    
    return SupportMessageResponse(
        message_id=message_id,
        status="received",
        message=response_message,
        created_at=created_at
    )
