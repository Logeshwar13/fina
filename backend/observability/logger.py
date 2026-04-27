"""
Structured Logger
Provides structured logging with context and metadata.
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum


class LogLevel(Enum):
    """Log level enumeration"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class StructuredLogger:
    """
    Structured logger with JSON output and context tracking.
    """
    
    def __init__(self, name: str = "FinA", level: str = "INFO"):
        """
        Initialize structured logger.
        
        Args:
            name: Logger name
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level))
        
        # Create console handler with JSON formatter
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(self._get_formatter())
            self.logger.addHandler(handler)
        
        # Context storage
        self.context = {}
    
    def _get_formatter(self):
        """Get JSON formatter"""
        class JSONFormatter(logging.Formatter):
            def format(self, record):
                log_data = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "level": record.levelname,
                    "logger": record.name,
                    "message": record.getMessage(),
                    "module": record.module,
                    "function": record.funcName,
                    "line": record.lineno
                }
                
                # Add extra fields
                if hasattr(record, "extra"):
                    log_data.update(record.extra)
                
                # Add exception info if present
                if record.exc_info:
                    log_data["exception"] = self.formatException(record.exc_info)
                
                return json.dumps(log_data)
        
        return JSONFormatter()
    
    def set_context(self, **kwargs):
        """
        Set context that will be included in all logs.
        
        Args:
            **kwargs: Context key-value pairs
        """
        self.context.update(kwargs)
    
    def clear_context(self):
        """Clear all context"""
        self.context = {}
    
    def _log(self, level: str, message: str, **kwargs):
        """
        Internal log method.
        
        Args:
            level: Log level
            message: Log message
            **kwargs: Additional fields
        """
        # Merge context and kwargs
        extra = {**self.context, **kwargs}
        
        # Log with extra fields
        log_func = getattr(self.logger, level.lower())
        log_func(message, extra={"extra": extra})
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self._log("DEBUG", message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self._log("INFO", message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self._log("WARNING", message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message"""
        self._log("ERROR", message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message"""
        self._log("CRITICAL", message, **kwargs)
    
    def log_request(self, method: str, path: str, **kwargs):
        """
        Log HTTP request.
        
        Args:
            method: HTTP method
            path: Request path
            **kwargs: Additional fields
        """
        self.info(
            f"{method} {path}",
            event_type="http_request",
            method=method,
            path=path,
            **kwargs
        )
    
    def log_response(self, method: str, path: str, status_code: int, duration_ms: float, **kwargs):
        """
        Log HTTP response.
        
        Args:
            method: HTTP method
            path: Request path
            status_code: Response status code
            duration_ms: Request duration in milliseconds
            **kwargs: Additional fields
        """
        self.info(
            f"{method} {path} - {status_code} ({duration_ms:.2f}ms)",
            event_type="http_response",
            method=method,
            path=path,
            status_code=status_code,
            duration_ms=duration_ms,
            **kwargs
        )
    
    def log_agent_execution(self, agent_name: str, query: str, duration_ms: float, success: bool, **kwargs):
        """
        Log agent execution.
        
        Args:
            agent_name: Name of the agent
            query: User query
            duration_ms: Execution duration
            success: Whether execution succeeded
            **kwargs: Additional fields
        """
        self.info(
            f"Agent {agent_name} executed",
            event_type="agent_execution",
            agent_name=agent_name,
            query=query,
            duration_ms=duration_ms,
            success=success,
            **kwargs
        )
    
    def log_tool_execution(self, tool_name: str, duration_ms: float, success: bool, **kwargs):
        """
        Log tool execution.
        
        Args:
            tool_name: Name of the tool
            duration_ms: Execution duration
            success: Whether execution succeeded
            **kwargs: Additional fields
        """
        self.info(
            f"Tool {tool_name} executed",
            event_type="tool_execution",
            tool_name=tool_name,
            duration_ms=duration_ms,
            success=success,
            **kwargs
        )
    
    def log_rag_query(self, query: str, num_results: int, duration_ms: float, **kwargs):
        """
        Log RAG query.
        
        Args:
            query: Search query
            num_results: Number of results returned
            duration_ms: Query duration
            **kwargs: Additional fields
        """
        self.info(
            f"RAG query executed",
            event_type="rag_query",
            query=query,
            num_results=num_results,
            duration_ms=duration_ms,
            **kwargs
        )
    
    def log_validation_failure(self, validation_type: str, reason: str, **kwargs):
        """
        Log validation failure.
        
        Args:
            validation_type: Type of validation (input, output)
            reason: Failure reason
            **kwargs: Additional fields
        """
        self.warning(
            f"Validation failed: {reason}",
            event_type="validation_failure",
            validation_type=validation_type,
            reason=reason,
            **kwargs
        )
    
    def log_error_with_context(self, error: Exception, context: Dict[str, Any]):
        """
        Log error with full context.
        
        Args:
            error: Exception object
            context: Error context
        """
        self.error(
            f"Error: {str(error)}",
            event_type="error",
            error_type=type(error).__name__,
            error_message=str(error),
            **context
        )


# Global logger instance
_logger = None


def get_logger(name: str = "FinA", level: str = "INFO") -> StructuredLogger:
    """
    Get or create global logger instance.
    
    Args:
        name: Logger name
        level: Log level
        
    Returns:
        StructuredLogger instance
    """
    global _logger
    if _logger is None:
        _logger = StructuredLogger(name, level)
    return _logger
