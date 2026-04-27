"""
Execution Tracer
Tracks execution flow and creates trace spans for debugging.
"""

import time
import uuid
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class SpanStatus(Enum):
    """Span status enumeration"""
    OK = "ok"
    ERROR = "error"
    PENDING = "pending"


@dataclass
class Span:
    """Represents a trace span"""
    span_id: str
    trace_id: str
    parent_id: Optional[str]
    name: str
    start_time: float
    end_time: Optional[float] = None
    duration_ms: Optional[float] = None
    status: SpanStatus = SpanStatus.PENDING
    attributes: Dict[str, Any] = field(default_factory=dict)
    events: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert span to dictionary"""
        return {
            "span_id": self.span_id,
            "trace_id": self.trace_id,
            "parent_id": self.parent_id,
            "name": self.name,
            "start_time": datetime.fromtimestamp(self.start_time).isoformat(),
            "end_time": datetime.fromtimestamp(self.end_time).isoformat() if self.end_time else None,
            "duration_ms": self.duration_ms,
            "status": self.status.value,
            "attributes": self.attributes,
            "events": self.events
        }


class ExecutionTracer:
    """
    Traces execution flow through the system.
    """
    
    def __init__(self, max_traces: int = 100):
        """
        Initialize execution tracer.
        
        Args:
            max_traces: Maximum number of traces to keep in memory
        """
        self.max_traces = max_traces
        self.traces: Dict[str, List[Span]] = {}
        self.active_spans: Dict[str, Span] = {}
    
    def start_trace(self, trace_name: str, **attributes) -> str:
        """
        Start a new trace.
        
        Args:
            trace_name: Name of the trace
            **attributes: Trace attributes
            
        Returns:
            Trace ID
        """
        trace_id = str(uuid.uuid4())
        self.traces[trace_id] = []
        
        # Create root span
        self.start_span(trace_id, trace_name, None, **attributes)
        
        return trace_id
    
    def start_span(
        self,
        trace_id: str,
        span_name: str,
        parent_id: Optional[str] = None,
        **attributes
    ) -> str:
        """
        Start a new span.
        
        Args:
            trace_id: Trace ID
            span_name: Name of the span
            parent_id: Parent span ID
            **attributes: Span attributes
            
        Returns:
            Span ID
        """
        span_id = str(uuid.uuid4())
        
        span = Span(
            span_id=span_id,
            trace_id=trace_id,
            parent_id=parent_id,
            name=span_name,
            start_time=time.time(),
            attributes=attributes
        )
        
        # Store span
        if trace_id not in self.traces:
            self.traces[trace_id] = []
        
        self.traces[trace_id].append(span)
        self.active_spans[span_id] = span
        
        # Cleanup old traces
        if len(self.traces) > self.max_traces:
            oldest_trace = min(self.traces.keys(), key=lambda k: self.traces[k][0].start_time)
            del self.traces[oldest_trace]
        
        return span_id
    
    def end_span(self, span_id: str, status: SpanStatus = SpanStatus.OK, **attributes):
        """
        End a span.
        
        Args:
            span_id: Span ID
            status: Span status
            **attributes: Additional attributes
        """
        if span_id in self.active_spans:
            span = self.active_spans[span_id]
            span.end_time = time.time()
            span.duration_ms = (span.end_time - span.start_time) * 1000
            span.status = status
            span.attributes.update(attributes)
            
            del self.active_spans[span_id]
    
    def add_event(self, span_id: str, event_name: str, **attributes):
        """
        Add an event to a span.
        
        Args:
            span_id: Span ID
            event_name: Event name
            **attributes: Event attributes
        """
        if span_id in self.active_spans:
            span = self.active_spans[span_id]
            span.events.append({
                "name": event_name,
                "timestamp": datetime.utcnow().isoformat(),
                "attributes": attributes
            })
    
    def set_attribute(self, span_id: str, key: str, value: Any):
        """
        Set a span attribute.
        
        Args:
            span_id: Span ID
            key: Attribute key
            value: Attribute value
        """
        if span_id in self.active_spans:
            self.active_spans[span_id].attributes[key] = value
    
    def get_trace(self, trace_id: str) -> Optional[List[Dict[str, Any]]]:
        """
        Get a trace by ID.
        
        Args:
            trace_id: Trace ID
            
        Returns:
            List of span dictionaries or None
        """
        if trace_id in self.traces:
            return [span.to_dict() for span in self.traces[trace_id]]
        return None
    
    def get_all_traces(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get all traces.
        
        Returns:
            Dictionary of trace_id -> spans
        """
        return {
            trace_id: [span.to_dict() for span in spans]
            for trace_id, spans in self.traces.items()
        }
    
    def get_trace_summary(self, trace_id: str) -> Optional[Dict[str, Any]]:
        """
        Get trace summary.
        
        Args:
            trace_id: Trace ID
            
        Returns:
            Summary dictionary or None
        """
        if trace_id not in self.traces:
            return None
        
        spans = self.traces[trace_id]
        
        if not spans:
            return None
        
        root_span = spans[0]
        total_duration = root_span.duration_ms if root_span.duration_ms else 0
        
        # Count spans by status
        status_counts = {}
        for span in spans:
            status = span.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "trace_id": trace_id,
            "name": root_span.name,
            "start_time": datetime.fromtimestamp(root_span.start_time).isoformat(),
            "duration_ms": total_duration,
            "span_count": len(spans),
            "status_counts": status_counts,
            "attributes": root_span.attributes
        }
    
    def clear_traces(self):
        """Clear all traces"""
        self.traces.clear()
        self.active_spans.clear()
    
    # Context manager support
    
    class SpanContext:
        """Context manager for spans"""
        
        def __init__(self, tracer: 'ExecutionTracer', trace_id: str, span_name: str, parent_id: Optional[str] = None, **attributes):
            self.tracer = tracer
            self.trace_id = trace_id
            self.span_name = span_name
            self.parent_id = parent_id
            self.attributes = attributes
            self.span_id = None
        
        def __enter__(self):
            self.span_id = self.tracer.start_span(
                self.trace_id,
                self.span_name,
                self.parent_id,
                **self.attributes
            )
            return self.span_id
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            if exc_type is not None:
                self.tracer.end_span(
                    self.span_id,
                    status=SpanStatus.ERROR,
                    error_type=exc_type.__name__,
                    error_message=str(exc_val)
                )
            else:
                self.tracer.end_span(self.span_id, status=SpanStatus.OK)
            return False
    
    def span(self, trace_id: str, span_name: str, parent_id: Optional[str] = None, **attributes):
        """
        Create a span context manager.
        
        Args:
            trace_id: Trace ID
            span_name: Span name
            parent_id: Parent span ID
            **attributes: Span attributes
            
        Returns:
            SpanContext
        """
        return self.SpanContext(self, trace_id, span_name, parent_id, **attributes)


# Global tracer instance
_tracer = None


def get_tracer() -> ExecutionTracer:
    """
    Get or create global tracer instance.
    
    Returns:
        ExecutionTracer instance
    """
    global _tracer
    if _tracer is None:
        _tracer = ExecutionTracer()
    return _tracer
