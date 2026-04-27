"""
Global Error Handler Middleware
Handles all exceptions and provides consistent error responses.
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import traceback
from typing import Union
import time

from observability import get_logger, get_metrics

logger = get_logger()
metrics = get_metrics()


class ErrorHandlerMiddleware:
    """Global error handler middleware"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        """Handle requests"""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        
        try:
            await self.app(scope, receive, send)
        except Exception as exc:
            response = await self.handle_exception(request, exc)
            await response(scope, receive, send)
    
    async def handle_exception(self, request: Request, exc: Exception) -> JSONResponse:
        """
        Handle exception and return appropriate response.
        
        Args:
            request: Request object
            exc: Exception that occurred
            
        Returns:
            JSONResponse with error details
        """
        # Log the error
        logger.error(
            f"Error handling request: {request.method} {request.url.path}",
            error_type=type(exc).__name__,
            error_message=str(exc),
            path=request.url.path,
            method=request.method
        )
        
        # Track error metrics
        metrics.increment("errors.total", tags={
            "error_type": type(exc).__name__,
            "path": request.url.path,
            "method": request.method
        })
        
        # Handle different exception types
        if isinstance(exc, RequestValidationError):
            return self._handle_validation_error(exc)
        elif isinstance(exc, StarletteHTTPException):
            return self._handle_http_exception(exc)
        elif isinstance(exc, ValueError):
            return self._handle_value_error(exc)
        elif isinstance(exc, KeyError):
            return self._handle_key_error(exc)
        elif isinstance(exc, TimeoutError):
            return self._handle_timeout_error(exc)
        else:
            return self._handle_generic_error(exc)
    
    def _handle_validation_error(self, exc: RequestValidationError) -> JSONResponse:
        """Handle validation errors"""
        errors = []
        for error in exc.errors():
            errors.append({
                "field": ".".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "type": error["type"]
            })
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "Validation Error",
                "message": "Request validation failed",
                "details": errors,
                "timestamp": time.time()
            }
        )
    
    def _handle_http_exception(self, exc: StarletteHTTPException) -> JSONResponse:
        """Handle HTTP exceptions"""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "HTTP Error",
                "message": exc.detail,
                "status_code": exc.status_code,
                "timestamp": time.time()
            }
        )
    
    def _handle_value_error(self, exc: ValueError) -> JSONResponse:
        """Handle value errors"""
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "Invalid Value",
                "message": str(exc),
                "timestamp": time.time()
            }
        )
    
    def _handle_key_error(self, exc: KeyError) -> JSONResponse:
        """Handle key errors"""
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "Missing Key",
                "message": f"Required key not found: {str(exc)}",
                "timestamp": time.time()
            }
        )
    
    def _handle_timeout_error(self, exc: TimeoutError) -> JSONResponse:
        """Handle timeout errors"""
        return JSONResponse(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            content={
                "error": "Timeout",
                "message": "Request timed out",
                "details": str(exc),
                "timestamp": time.time()
            }
        )
    
    def _handle_generic_error(self, exc: Exception) -> JSONResponse:
        """Handle generic errors"""
        # Log full traceback for debugging
        logger.error(
            "Unhandled exception",
            error_type=type(exc).__name__,
            error_message=str(exc),
            traceback=traceback.format_exc()
        )
        
        # Don't expose internal errors in production
        from config import settings
        
        if settings.is_production:
            message = "An internal error occurred"
            details = None
        else:
            message = str(exc)
            details = traceback.format_exc()
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal Server Error",
                "message": message,
                "details": details,
                "timestamp": time.time()
            }
        )


def setup_error_handlers(app):
    """
    Setup error handlers for FastAPI app.
    
    Args:
        app: FastAPI application
    """
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle validation errors"""
        logger.warning(
            "Validation error",
            path=request.url.path,
            errors=exc.errors()
        )
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "Validation Error",
                "message": "Request validation failed",
                "details": exc.errors(),
                "timestamp": time.time()
            }
        )
    
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """Handle HTTP exceptions"""
        logger.warning(
            "HTTP exception",
            path=request.url.path,
            status_code=exc.status_code,
            detail=exc.detail
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "HTTP Error",
                "message": exc.detail,
                "status_code": exc.status_code,
                "timestamp": time.time()
            }
        )
    
    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        """Handle all other exceptions"""
        logger.error(
            "Unhandled exception",
            path=request.url.path,
            error_type=type(exc).__name__,
            error_message=str(exc),
            traceback=traceback.format_exc()
        )
        
        metrics.increment("errors.unhandled")
        
        from config import settings
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal Server Error",
                "message": str(exc) if not settings.is_production else "An internal error occurred",
                "timestamp": time.time()
            }
        )
    
    logger.info("Error handlers configured")
