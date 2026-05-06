"""
ROUTER: chat_router
PURPOSE: Public AI chat endpoint for SOAR B2B Assistant
ENCODING: UTF-8 WITHOUT BOM
"""

import os
import logging
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel, Field

# OpenAI import
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    openai = None

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["chat"])

# Rate limiting: 10 messages per minute per IP
from collections import defaultdict
from time import time

_rate_limit_store = defaultdict(list)
RATE_LIMIT_WINDOW = 60   # 60 seconds
RATE_LIMIT_MAX = 10   # 10 messages per window


def check_rate_limit(client_ip: str) -> bool:
    """Check if client IP is within rate limit"""
    now = time()
    # Clean old entries
    _rate_limit_store[client_ip] = [
        ts for ts in _rate_limit_store[client_ip] if now - ts < RATE_LIMIT_WINDOW
    ]
    # Check limit
    if len(_rate_limit_store[client_ip]) >= RATE_LIMIT_MAX:
        return False
    # Add current request
    _rate_limit_store[client_ip].append(now)
    return True


class ChatMessageRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="User message")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for history")


class ChatMessageResponse(BaseModel):
    reply: str
    conversation_id: str
    timestamp: str


def get_client_ip(request: Request) -> str:
    """Get client IP address"""
    # Check for forwarded headers (Cloud Run, load balancers)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    if request.client:
        return request.client.host
    
    return "unknown"


@router.post("", response_model=ChatMessageResponse)
async def chat(
    request_data: ChatMessageRequest,
    http_request: Request
):
    """
    Public AI chat endpoint.
    No authentication required, but rate limited.
    """
    # Rate limiting
    client_ip = get_client_ip(http_request)
    if not check_rate_limit(client_ip):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please wait a moment before sending another message."
        )
    
    # Validate message length
    message = request_data.message.strip()
    if not message or len(message) > 2000:
        raise HTTPException(
            status_code=400,
            detail="Message must be between 1 and 2000 characters."
        )
    
    # Check OpenAI availability
    if not OPENAI_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Chat service is temporarily unavailable. Please try again later."
        )
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.warning("OPENAI_API_KEY not configured")
        raise HTTPException(
            status_code=503,
            detail="Chat service is not configured."
        )
    
    # Initialize OpenAI client
    try:
        client = openai.OpenAI(api_key=api_key)
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI client: {e}")
        raise HTTPException(
            status_code=503,
            detail="Chat service initialization failed."
        )
    
    # System prompt
    system_prompt = """You are SOAR B2B Assistant, a helpful AI assistant for B2B growth, sales, SaaS, marketing, and automation.

Your role:
- Answer questions about B2B growth strategies
- Provide insights on sales and marketing
- Help with SaaS business development
- Suggest automation solutions
- Guide users on B2B best practices

Keep responses concise, professional, and actionable. Focus on practical B2B advice."""
    
    # Generate conversation ID if not provided
    conversation_id = request_data.conversation_id or f"conv_{int(datetime.utcnow().timestamp())}"
    
    try:
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        reply = response.choices[0].message.content
        
        logger.info(f"Chat request processed: IP={client_ip}, length={len(message)}")
        
        return ChatMessageResponse(
            reply=reply,
            conversation_id=conversation_id,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except openai.RateLimitError:
        logger.warning(f"OpenAI rate limit exceeded for IP: {client_ip}")
        raise HTTPException(
            status_code=503,
            detail="Chat service is temporarily overloaded. Please try again in a moment."
        )
    except openai.APIError as e:
        logger.error(f"OpenAI API error: {e}")
        raise HTTPException(
            status_code=503,
            detail="Chat service encountered an error. Please try again later."
        )
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred. Please try again later."
        )


@router.get("/health")
async def chat_health():
    """Health check for chat service"""
    api_key = os.getenv("OPENAI_API_KEY")
    available = OPENAI_AVAILABLE and bool(api_key)
    
    return {
        "status": "ok" if available else "unavailable",
        "openai_configured": available,
        "service": "chat"
    }
