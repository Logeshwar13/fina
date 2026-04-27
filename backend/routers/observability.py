"""
Observability Router
Provides endpoints for metrics, logs, and traces.
"""

from fastapi import APIRouter, HTTPException
from typing import Optional
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from observability.logger import get_logger
from observability.metrics import get_metrics
from observability.tracer import get_tracer


router = APIRouter(prefix="/observability", tags=["Observability"])

# Get global instances
logger = get_logger()
metrics = get_metrics()
tracer = get_tracer()


@router.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "service": "FinA",
        "version": "1.0.0"
    }


@router.get("/metrics")
async def get_all_metrics():
    """
    Get all system metrics.
    
    Returns:
        All metrics
    """
    return metrics.get_all_metrics()


@router.get("/metrics/summary")
async def get_metrics_summary():
    """
    Get metrics summary.
    
    Returns:
        Metrics summary
    """
    return metrics.get_summary()


@router.get("/metrics/{metric_name}")
async def get_specific_metric(metric_name: str):
    """
    Get a specific metric.
    
    Args:
        metric_name: Name of the metric
        
    Returns:
        Metric value or stats
    """
    # Try counter
    counter_value = metrics.get_counter(metric_name)
    if counter_value > 0:
        return {"metric": metric_name, "type": "counter", "value": counter_value}
    
    # Try gauge
    gauge_value = metrics.get_gauge(metric_name)
    if gauge_value != 0:
        return {"metric": metric_name, "type": "gauge", "value": gauge_value}
    
    # Try histogram
    histogram_stats = metrics.get_histogram_stats(metric_name)
    if histogram_stats["count"] > 0:
        return {"metric": metric_name, "type": "histogram", "stats": histogram_stats}
    
    raise HTTPException(status_code=404, detail=f"Metric '{metric_name}' not found")


@router.post("/metrics/reset")
async def reset_metrics():
    """
    Reset all metrics.
    
    Returns:
        Success message
    """
    metrics.reset()
    return {"message": "Metrics reset successfully"}


@router.get("/traces")
async def get_all_traces():
    """
    Get all traces.
    
    Returns:
        All traces
    """
    traces = tracer.get_all_traces()
    
    # Get summaries
    summaries = []
    for trace_id in traces.keys():
        summary = tracer.get_trace_summary(trace_id)
        if summary:
            summaries.append(summary)
    
    return {
        "count": len(summaries),
        "traces": summaries
    }


@router.get("/traces/{trace_id}")
async def get_trace(trace_id: str):
    """
    Get a specific trace.
    
    Args:
        trace_id: Trace ID
        
    Returns:
        Trace spans
    """
    trace = tracer.get_trace(trace_id)
    
    if trace is None:
        raise HTTPException(status_code=404, detail=f"Trace '{trace_id}' not found")
    
    return {
        "trace_id": trace_id,
        "spans": trace,
        "summary": tracer.get_trace_summary(trace_id)
    }


@router.post("/traces/clear")
async def clear_traces():
    """
    Clear all traces.
    
    Returns:
        Success message
    """
    tracer.clear_traces()
    return {"message": "Traces cleared successfully"}


@router.get("/stats")
async def get_system_stats():
    """
    Get comprehensive system statistics.
    
    Returns:
        System statistics
    """
    metrics_summary = metrics.get_summary()
    all_traces = tracer.get_all_traces()
    
    return {
        "metrics": metrics_summary,
        "traces": {
            "total_traces": len(all_traces),
            "active_spans": len(tracer.active_spans)
        },
        "system": {
            "uptime_seconds": metrics_summary["uptime_seconds"]
        }
    }


@router.get("/performance")
async def get_performance_metrics():
    """
    Get performance-specific metrics.
    
    Returns:
        Performance metrics
    """
    return {
        "http_requests": {
            "total": metrics.get_counter("http.requests.total"),
            "latency": metrics.get_histogram_stats("http.request.duration_ms")
        },
        "agents": {
            "total_executions": metrics.get_counter("agent.executions.total"),
            "latency": metrics.get_histogram_stats("agent.execution.duration_ms")
        },
        "tools": {
            "total_executions": metrics.get_counter("tool.executions.total"),
            "latency": metrics.get_histogram_stats("tool.execution.duration_ms")
        },
        "rag": {
            "total_queries": metrics.get_counter("rag.queries.total"),
            "latency": metrics.get_histogram_stats("rag.query.duration_ms")
        }
    }


@router.get("/errors")
async def get_error_metrics():
    """
    Get error-related metrics.
    
    Returns:
        Error metrics
    """
    return {
        "validation_failures": metrics.get_counter("validation.failures.total"),
        "agent_failures": metrics.get_counter("agent.executions.failure"),
        "tool_failures": metrics.get_counter("tool.executions.failure"),
        "http_errors": {
            "4xx": metrics.get_counter("http.requests.status.400") + 
                   metrics.get_counter("http.requests.status.404"),
            "5xx": metrics.get_counter("http.requests.status.500")
        }
    }
