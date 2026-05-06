"""
MIDDLEWARE: structured_logging_middleware
PURPOSE: Log requests in structured JSON format
ENCODING: UTF-8 WITHOUT BOM
"""

import time
import json
import logging
from fastapi import Request

logger = logging.getLogger("soarb2b.requests")


class StructuredLoggingMiddleware:
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        start_time = time.time()
        
        ***REMOVED*** Create response wrapper
        response_body = b""
        status_code = 200
        
        async def send_wrapper(message):
            nonlocal response_body, status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            elif message["type"] == "http.response.body":
                if message.get("body"):
                    response_body += message["body"]
            await send(message)
        
        try:
            await self.app(scope, receive, send_wrapper)
        except Exception as e:
            status_code = 500
            logger.error(f"Request failed: {str(e)}", exc_info=True)
            raise
        finally:
            latency_ms = int((time.time() - start_time) * 1000)
            request_id = getattr(request.state, "request_id", "unknown")
            
            ***REMOVED*** Get API key (masked) for observability
            api_key = request.headers.get("X-API-Key")
            masked_api_key = None
            if api_key:
                if len(api_key) > 10:
                    masked_api_key = f"{api_key[:5]}***{api_key[-5:]}"
                else:
                    masked_api_key = "***"
            
            log_data = {
                "path": request.url.path,
                "method": request.method,
                "status": status_code,
                "latency_ms": latency_ms,
                "request_id": request_id,
                "client_ip": request.client.host if request.client else "unknown",
                "api_key_masked": masked_api_key,
                "endpoint": request.url.path,
                "query_params": str(request.query_params) if request.query_params else None
            }
            
            ***REMOVED*** Only log body for small requests (avoid logging large uploads)
            if request.headers.get("content-length"):
                content_length = int(request.headers.get("content-length", 0))
                if content_length < 1024:  ***REMOVED*** Only log if < 1KB
                    try:
                        body = await request.body()
                        if body:
                            log_data["body_size"] = len(body)
                    except Exception:
                        pass
            
            logger.info(json.dumps(log_data, ensure_ascii=False))
