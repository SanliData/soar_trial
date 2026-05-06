"""
MIDDLEWARE: locale_middleware
PURPOSE: Extract and provide locale information from Accept-Language header
ENCODING: UTF-8 WITHOUT BOM
"""

import os
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Optional


class LocaleMiddleware(BaseHTTPMiddleware):
    """
    Middleware to extract locale from Accept-Language header.
    Stores locale in request.state for use in services.
    """
    
    SUPPORTED_LANGUAGES = ['tr', 'en', 'de', 'es']
    DEFAULT_LANGUAGE = 'en'
    
    async def dispatch(self, request: Request, call_next):
        ***REMOVED*** Extract Accept-Language header
        accept_language = request.headers.get('Accept-Language', '')
        
        ***REMOVED*** Parse locale (e.g., "tr-TR,tr;q=0.9,en;q=0.8" -> "tr")
        locale = self._parse_locale(accept_language)
        
        ***REMOVED*** Store in request state for use in services
        request.state.locale = locale
        
        response = await call_next(request)
        return response
    
    def _parse_locale(self, accept_language: str) -> str:
        """
        Parse Accept-Language header and return the best match.
        
        Args:
            accept_language: Accept-Language header value (e.g., "tr-TR,tr;q=0.9,en;q=0.8")
        
        Returns:
            Locale code (tr, en, de, es) or default
        """
        if not accept_language:
            return self.DEFAULT_LANGUAGE
        
        ***REMOVED*** Parse language preferences (simple implementation)
        ***REMOVED*** Format: "lang1,lang2;q=0.9,lang3;q=0.8"
        languages = []
        for part in accept_language.split(','):
            part = part.strip()
            if ';' in part:
                lang, q = part.split(';', 1)
                q_value = float(q.split('=')[1]) if '=' in q else 1.0
            else:
                lang = part
                q_value = 1.0
            
            ***REMOVED*** Extract base language (e.g., "tr-TR" -> "tr")
            base_lang = lang.split('-')[0].lower()
            if base_lang in self.SUPPORTED_LANGUAGES:
                languages.append((base_lang, q_value))
        
        ***REMOVED*** Sort by quality value (highest first)
        languages.sort(key=lambda x: x[1], reverse=True)
        
        ***REMOVED*** Return first supported language
        if languages:
            return languages[0][0]
        
        return self.DEFAULT_LANGUAGE


def get_locale_from_request(request: Request) -> str:
    """
    Helper function to get locale from request state.
    
    Args:
        request: FastAPI Request object
    
    Returns:
        Locale code (tr, en, de, es)
    """
    return getattr(request.state, 'locale', LocaleMiddleware.DEFAULT_LANGUAGE)

