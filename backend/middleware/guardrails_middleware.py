"""
Guardrails Middleware
Applies input validation and output filtering to all API requests/responses.
"""

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import json
import time

from guardrails.input_validator import InputValidator
from guardrails.output_validator import OutputValidator


class GuardrailsMiddleware(BaseHTTPMiddleware):
    """
    Middleware that applies guardrails to all requests and responses.
    """
    
    def __init__(self, app: ASGIApp, enable_input_validation: bool = True, enable_output_validation: bool = True):
        """
        Initialize guardrails middleware.
        
        Args:
            app: ASGI application
            enable_input_validation: Whether to validate inputs
            enable_output_validation: Whether to validate outputs
        """
        super().__init__(app)
        self.enable_input_validation = enable_input_validation
        self.enable_output_validation = enable_output_validation
        self.input_validator = InputValidator()
        self.output_validator = OutputValidator()
        
        # Paths to skip validation
        self.skip_paths = [
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health",
            "/",
            "/favicon.ico"
        ]
    
    async def dispatch(self, request: Request, call_next):
        """
        Process request and response with guardrails.
        
        Args:
            request: Incoming request
            call_next: Next middleware/handler
            
        Returns:
            Response with guardrails applied
        """
        # Skip validation for certain paths
        if request.url.path in self.skip_paths:
            return await call_next(request)
        
        # Skip validation for GET requests (read-only)
        if request.method == "GET":
            return await call_next(request)
        
        start_time = time.time()
        
        # INPUT VALIDATION
        if self.enable_input_validation and request.method in ["POST", "PUT", "PATCH"]:
            try:
                # Get request body
                body = await request.body()
                
                if body:
                    try:
                        data = json.loads(body)
                        
                        # Validate query if present
                        if "query" in data:
                            is_valid, error, sanitized = self.input_validator.validate_and_sanitize(
                                data["query"],
                                {"user_id": data.get("user_id", "")}
                            )
                            
                            if not is_valid:
                                return JSONResponse(
                                    status_code=400,
                                    content={
                                        "error": "Input validation failed",
                                        "detail": error,
                                        "type": "validation_error"
                                    }
                                )
                            
                            # Replace with sanitized query
                            data["query"] = sanitized
                        
                        # Validate amounts if present
                        for field in ["amount", "limit", "coverage_amount", "premium"]:
                            if field in data:
                                is_valid, error, parsed = self.input_validator.validate_amount(
                                    data[field],
                                    field_name=field
                                )
                                
                                if not is_valid:
                                    return JSONResponse(
                                        status_code=400,
                                        content={
                                            "error": "Amount validation failed",
                                            "detail": error,
                                            "field": field,
                                            "type": "validation_error"
                                        }
                                    )
                        
                        # Recreate request with sanitized data
                        request._body = json.dumps(data).encode()
                        
                    except json.JSONDecodeError:
                        pass  # Not JSON, skip validation
                
            except Exception as e:
                # Log error but don't block request
                print(f"Guardrails middleware error: {e}")
        
        # Process request
        response = await call_next(request)
        
        # OUTPUT VALIDATION
        if self.enable_output_validation and response.status_code == 200:
            try:
                # Get response body
                response_body = b""
                async for chunk in response.body_iterator:
                    response_body += chunk
                
                if response_body:
                    try:
                        data = json.loads(response_body)
                        
                        # Validate response if present
                        if "response" in data and isinstance(data["response"], str):
                            is_valid, error, enhanced = self.output_validator.validate_and_enhance(
                                data["response"],
                                response_type="general",
                                context={"has_data": True}
                            )
                            
                            if is_valid:
                                data["response"] = enhanced
                            else:
                                # Use safe fallback
                                data["response"] = "I apologize, but I couldn't generate a safe response."
                                data["validation_warning"] = error
                        
                        # Filter sensitive data
                        if "response" in data:
                            data["response"] = self.output_validator.filter_sensitive_data(
                                data["response"]
                            )
                        
                        # Create new response
                        response_body = json.dumps(data).encode()
                        
                    except json.JSONDecodeError:
                        pass  # Not JSON, skip validation
                
                # Calculate processing time
                process_time = time.time() - start_time
                
                # Create new response with updated body and correct headers
                headers = dict(response.headers)
                headers["Content-Length"] = str(len(response_body))
                headers["X-Process-Time"] = str(process_time)
                
                return Response(
                    content=response_body,
                    status_code=response.status_code,
                    headers=headers,
                    media_type=response.media_type
                )
                
            except Exception as e:
                # Log error but return original response
                print(f"Output validation error: {e}")
                return response
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple rate limiting middleware.
    """
    
    def __init__(self, app: ASGIApp, max_requests: int = 100, window_seconds: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            app: ASGI application
            max_requests: Maximum requests per window
            window_seconds: Time window in seconds
        """
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}  # user_id -> [(timestamp, count)]
    
    async def dispatch(self, request: Request, call_next):
        """
        Check rate limit and process request.
        
        Args:
            request: Incoming request
            call_next: Next middleware/handler
            
        Returns:
            Response or rate limit error
        """
        # Get user ID from request (you may need to adjust this)
        user_id = request.headers.get("X-User-ID", request.client.host)
        
        # Check rate limit
        current_time = time.time()
        
        if user_id not in self.requests:
            self.requests[user_id] = []
        
        # Remove old requests
        self.requests[user_id] = [
            (ts, count) for ts, count in self.requests[user_id]
            if current_time - ts < self.window_seconds
        ]
        
        # Count requests in window
        total_requests = sum(count for _, count in self.requests[user_id])
        
        if total_requests >= self.max_requests:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "detail": f"Maximum {self.max_requests} requests per {self.window_seconds} seconds",
                    "retry_after": self.window_seconds
                }
            )
        
        # Add current request
        self.requests[user_id].append((current_time, 1))
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(self.max_requests - total_requests - 1)
        response.headers["X-RateLimit-Reset"] = str(int(current_time + self.window_seconds))
        
        return response
