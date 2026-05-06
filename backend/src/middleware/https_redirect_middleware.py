"""
MIDDLEWARE: https_redirect_middleware
PURPOSE: Redirect HTTP to HTTPS in production
ENCODING: UTF-8 WITHOUT BOM
"""

import os
from fastapi import Request, status
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware


class HTTPSRedirectMiddleware(BaseHTTPMiddleware):
    """
    Middleware to redirect HTTP requests to HTTPS in production.
    Only active when FINDEROS_FORCE_HTTPS is enabled.
    """
    
    async def dispatch(self, request: Request, call_next):
        # Check if HTTPS redirect is enabled
        force_https = os.getenv("FINDEROS_FORCE_HTTPS", "false").lower() == "true"
        
        if force_https:
            # Check if request is HTTP
            if request.url.scheme == "http":
                # Build HTTPS URL
                https_url = request.url.replace(scheme="https")
                return RedirectResponse(
                    url=str(https_url),
                    status_code=status.HTTP_301_MOVED_PERMANENTLY
                )
        
        # Continue with normal request
        response = await call_next(request)
        return response


