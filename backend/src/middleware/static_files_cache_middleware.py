"""
MIDDLEWARE: static_files_cache_middleware
PURPOSE: Add cache headers to StaticFiles responses (workaround for StaticFiles bypassing middleware)
ENCODING: UTF-8 WITHOUT BOM
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


class StaticFilesCacheMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add cache headers to static file responses.
    
    NOTE: FastAPI StaticFiles mount may bypass some middleware.
    This middleware runs AFTER StaticFiles and modifies the response.
    """
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        ***REMOVED*** Check if this is a static file response
        path = request.url.path.lower()
        
        ***REMOVED*** Check if this is an HTML file or UI route
        is_html_file = (
            path.endswith('.html') or
            path.startswith('/ui/')
        )
        
        ***REMOVED*** Also check content-type (StaticFiles sets this)
        content_type = response.headers.get('content-type', '')
        is_html_response = content_type.startswith('text/html')
        
        if is_html_file or is_html_response:
            ***REMOVED*** Force no-cache headers
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
            response.headers["CDN-Cache-Control"] = "no-cache"
            
            ***REMOVED*** Remove ETag and Last-Modified (prevent conditional requests)
            if "ETag" in response.headers:
                del response.headers["ETag"]
            if "Last-Modified" in response.headers:
                del response.headers["Last-Modified"]
        
        return response
