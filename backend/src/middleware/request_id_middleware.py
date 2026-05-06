"""
MIDDLEWARE: request_id_middleware
PURPOSE: Generate and attach request ID to every request
ENCODING: UTF-8 WITHOUT BOM
"""

import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        ***REMOVED*** Get or generate request ID
        request_id = request.headers.get("X-Request-ID")
        if not request_id:
            request_id = str(uuid.uuid4())
        
        ***REMOVED*** Attach to request state
        request.state.request_id = request_id
        
        ***REMOVED*** Process request
        response = await call_next(request)
        
        ***REMOVED*** Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        
        return response
