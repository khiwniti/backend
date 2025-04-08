from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time
import json
from ..logging.config import logging_config

logger = logging_config.get_logger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        """Log request and response data"""
        start_time = time.time()
        
        # Log request
        request_data = {
            "method": request.method,
            "url": str(request.url),
            "headers": dict(request.headers),
            "query_params": dict(request.query_params),
            "path_params": request.path_params,
            "client": {
                "host": request.client.host if request.client else None,
                "port": request.client.port if request.client else None
            }
        }
        
        # Log request body if present
        try:
            body = await request.body()
            if body:
                request_data["body"] = body.decode()
        except Exception:
            pass
        
        logger.info("Request: %s", json.dumps(request_data, default=str))
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log response
        response_data = {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "process_time": process_time
        }
        
        logger.info("Response: %s", json.dumps(response_data, default=str))
        
        return response

# Create a singleton instance
logging_middleware = LoggingMiddleware() 