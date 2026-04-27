"""
Metrics Collector
Tracks performance metrics and system statistics.
"""

import time
from typing import Dict, List, Any, Optional
from collections import defaultdict, deque
from datetime import datetime
import statistics


class MetricsCollector:
    """
    Collects and aggregates system metrics.
    """
    
    def __init__(self, max_history: int = 1000):
        """
        Initialize metrics collector.
        
        Args:
            max_history: Maximum number of data points to keep
        """
        self.max_history = max_history
        
        # Metric storage
        self.counters = defaultdict(int)
        self.gauges = defaultdict(float)
        self.histograms = defaultdict(lambda: deque(maxlen=max_history))
        self.timers = {}
        
        # Start time
        self.start_time = time.time()
    
    def increment(self, metric_name: str, value: int = 1, tags: Optional[Dict[str, str]] = None):
        """
        Increment a counter.
        
        Args:
            metric_name: Name of the metric
            value: Value to increment by
            tags: Optional tags
        """
        key = self._make_key(metric_name, tags)
        self.counters[key] += value
    
    def set_gauge(self, metric_name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """
        Set a gauge value.
        
        Args:
            metric_name: Name of the metric
            value: Gauge value
            tags: Optional tags
        """
        key = self._make_key(metric_name, tags)
        self.gauges[key] = value
    
    def record_value(self, metric_name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """
        Record a value in histogram.
        
        Args:
            metric_name: Name of the metric
            value: Value to record
            tags: Optional tags
        """
        key = self._make_key(metric_name, tags)
        self.histograms[key].append(value)
    
    def start_timer(self, timer_name: str) -> str:
        """
        Start a timer.
        
        Args:
            timer_name: Name of the timer
            
        Returns:
            Timer ID
        """
        timer_id = f"{timer_name}_{time.time()}"
        self.timers[timer_id] = time.time()
        return timer_id
    
    def stop_timer(self, timer_id: str, metric_name: str, tags: Optional[Dict[str, str]] = None):
        """
        Stop a timer and record duration.
        
        Args:
            timer_id: Timer ID from start_timer
            metric_name: Metric name to record duration
            tags: Optional tags
        """
        if timer_id in self.timers:
            duration = (time.time() - self.timers[timer_id]) * 1000  # Convert to ms
            self.record_value(metric_name, duration, tags)
            del self.timers[timer_id]
    
    def _make_key(self, metric_name: str, tags: Optional[Dict[str, str]] = None) -> str:
        """Create metric key with tags"""
        if tags:
            tag_str = ",".join(f"{k}={v}" for k, v in sorted(tags.items()))
            return f"{metric_name}[{tag_str}]"
        return metric_name
    
    def get_counter(self, metric_name: str, tags: Optional[Dict[str, str]] = None) -> int:
        """Get counter value"""
        key = self._make_key(metric_name, tags)
        return self.counters.get(key, 0)
    
    def get_gauge(self, metric_name: str, tags: Optional[Dict[str, str]] = None) -> float:
        """Get gauge value"""
        key = self._make_key(metric_name, tags)
        return self.gauges.get(key, 0.0)
    
    def get_histogram_stats(self, metric_name: str, tags: Optional[Dict[str, str]] = None) -> Dict[str, float]:
        """
        Get histogram statistics.
        
        Args:
            metric_name: Name of the metric
            tags: Optional tags
            
        Returns:
            Dictionary with min, max, mean, median, p50, p95, p99
        """
        key = self._make_key(metric_name, tags)
        values = list(self.histograms.get(key, []))
        
        if not values:
            return {
                "count": 0,
                "min": 0,
                "max": 0,
                "mean": 0,
                "median": 0,
                "p50": 0,
                "p95": 0,
                "p99": 0
            }
        
        sorted_values = sorted(values)
        count = len(sorted_values)
        
        return {
            "count": count,
            "min": sorted_values[0],
            "max": sorted_values[-1],
            "mean": statistics.mean(sorted_values),
            "median": statistics.median(sorted_values),
            "p50": self._percentile(sorted_values, 50),
            "p95": self._percentile(sorted_values, 95),
            "p99": self._percentile(sorted_values, 99)
        }
    
    def _percentile(self, sorted_values: List[float], percentile: int) -> float:
        """Calculate percentile"""
        if not sorted_values:
            return 0.0
        index = int((percentile / 100) * len(sorted_values))
        return sorted_values[min(index, len(sorted_values) - 1)]
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """
        Get all metrics.
        
        Returns:
            Dictionary with all metrics
        """
        metrics = {
            "uptime_seconds": time.time() - self.start_time,
            "timestamp": datetime.utcnow().isoformat(),
            "counters": dict(self.counters),
            "gauges": dict(self.gauges),
            "histograms": {}
        }
        
        # Add histogram stats
        for key in self.histograms.keys():
            metrics["histograms"][key] = self.get_histogram_stats(key.split("[")[0], None)
        
        return metrics
    
    def reset(self):
        """Reset all metrics"""
        self.counters.clear()
        self.gauges.clear()
        self.histograms.clear()
        self.timers.clear()
        self.start_time = time.time()
    
    # Convenience methods for common metrics
    
    def record_request(self, method: str, path: str, status_code: int, duration_ms: float):
        """Record HTTP request metrics"""
        self.increment("http.requests.total", tags={"method": method, "path": path})
        self.increment(f"http.requests.status.{status_code}")
        self.record_value("http.request.duration_ms", duration_ms, tags={"method": method})
    
    def record_agent_execution(self, agent_name: str, duration_ms: float, success: bool):
        """Record agent execution metrics"""
        self.increment("agent.executions.total", tags={"agent": agent_name})
        self.increment(f"agent.executions.{'success' if success else 'failure'}", tags={"agent": agent_name})
        self.record_value("agent.execution.duration_ms", duration_ms, tags={"agent": agent_name})
    
    def record_tool_execution(self, tool_name: str, duration_ms: float, success: bool):
        """Record tool execution metrics"""
        self.increment("tool.executions.total", tags={"tool": tool_name})
        self.increment(f"tool.executions.{'success' if success else 'failure'}", tags={"tool": tool_name})
        self.record_value("tool.execution.duration_ms", duration_ms, tags={"tool": tool_name})
    
    def record_rag_query(self, duration_ms: float, num_results: int):
        """Record RAG query metrics"""
        self.increment("rag.queries.total")
        self.record_value("rag.query.duration_ms", duration_ms)
        self.record_value("rag.query.results_count", num_results)
    
    def record_validation_failure(self, validation_type: str):
        """Record validation failure"""
        self.increment("validation.failures.total", tags={"type": validation_type})
    
    def record_token_usage(self, tokens: int, model: str):
        """Record token usage"""
        self.increment("llm.tokens.total", value=tokens, tags={"model": model})
        self.record_value("llm.tokens.per_request", tokens, tags={"model": model})
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get metrics summary.
        
        Returns:
            Summary dictionary
        """
        return {
            "uptime_seconds": time.time() - self.start_time,
            "total_requests": self.get_counter("http.requests.total"),
            "total_agent_executions": self.get_counter("agent.executions.total"),
            "total_tool_executions": self.get_counter("tool.executions.total"),
            "total_rag_queries": self.get_counter("rag.queries.total"),
            "total_validation_failures": self.get_counter("validation.failures.total"),
            "request_latency": self.get_histogram_stats("http.request.duration_ms"),
            "agent_latency": self.get_histogram_stats("agent.execution.duration_ms"),
            "tool_latency": self.get_histogram_stats("tool.execution.duration_ms"),
            "rag_latency": self.get_histogram_stats("rag.query.duration_ms")
        }


# Global metrics instance
_metrics = None


def get_metrics() -> MetricsCollector:
    """
    Get or create global metrics collector.
    
    Returns:
        MetricsCollector instance
    """
    global _metrics
    if _metrics is None:
        _metrics = MetricsCollector()
    return _metrics
