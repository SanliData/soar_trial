"""
MIDDLEWARE: cache_control_middleware
PURPOSE: Force no-cache headers for HTML files to bypass Cloudflare cache
ENCODING: UTF-8 WITHOUT BOM
"""

import os
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class CacheControlMiddleware(BaseHTTPMiddleware):
    """
    Middleware to force no-cache headers for HTML files.
    Prevents Cloudflare and browser caching of UI files.
    """
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        ***REMOVED*** Force no-cache for HTML files and UI routes
        path = request.url.path.lower()
        
        ***REMOVED*** Check if this is an HTML file or UI route
        is_html_file = (
            path.endswith('.html') or
            path.startswith('/ui/') or
            response.headers.get('content-type', '').startswith('text/html')
        )
        
        if is_html_file:
            ***REMOVED*** HARD FIX: Force no-cache headers
            ***REMOVED*** Note: CF-Cache-Status is set by Cloudflare edge, not origin
            ***REMOVED*** We set Cache-Control to signal Cloudflare to bypass cache
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
            
            ***REMOVED*** CDN-Cache-Control (Cloudflare respects this)
            response.headers["CDN-Cache-Control"] = "no-cache"
            
            ***REMOVED*** ETag removal (prevent conditional requests)
            if "ETag" in response.headers:
                del response.headers["ETag"]
            if "Last-Modified" in response.headers:
                del response.headers["Last-Modified"]
        
        return response
