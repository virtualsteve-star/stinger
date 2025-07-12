"""
Simple metrics collection for API monitoring.

This module provides basic metrics tracking without external dependencies.
For production use, consider integrating with Prometheus, StatsD, or OpenTelemetry.
"""

import json
import logging
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
from threading import Lock
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Simple in-memory metrics collector."""

    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self._metrics_lock = Lock()

        # Counters
        self._counters: Dict[str, int] = defaultdict(int)

        # Histograms (store recent values)
        self._histograms: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_history))

        # Gauges (current values)
        self._gauges: Dict[str, float] = {}

        # Rate tracking
        self._rate_windows: Dict[str, deque] = defaultdict(lambda: deque())

        self.start_time = time.time()

    def increment(self, metric: str, value: int = 1, labels: Optional[Dict[str, str]] = None):
        """Increment a counter metric."""
        key = self._make_key(metric, labels)
        with self._metrics_lock:
            self._counters[key] += value

    def record_value(self, metric: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Record a value for histogram calculation."""
        key = self._make_key(metric, labels)
        with self._metrics_lock:
            self._histograms[key].append((time.time(), value))

    def set_gauge(self, metric: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Set a gauge value."""
        key = self._make_key(metric, labels)
        with self._metrics_lock:
            self._gauges[key] = value

    def record_rate_event(self, metric: str, labels: Optional[Dict[str, str]] = None):
        """Record an event for rate calculation."""
        key = self._make_key(metric, labels)
        now = time.time()
        with self._metrics_lock:
            # Clean old events (older than 5 minutes)
            cutoff = now - 300
            self._rate_windows[key] = deque((t for t in self._rate_windows[key] if t > cutoff))
            self._rate_windows[key].append(now)

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get a summary of all metrics."""
        with self._metrics_lock:
            summary = {
                "uptime_seconds": time.time() - self.start_time,
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
                "histograms": {},
                "rates": {},
            }

            # Calculate histogram stats
            for key, values in self._histograms.items():
                if values:
                    recent_values = [v[1] for v in values]
                    summary["histograms"][key] = {
                        "count": len(recent_values),
                        "min": min(recent_values),
                        "max": max(recent_values),
                        "avg": sum(recent_values) / len(recent_values),
                        "p50": self._percentile(recent_values, 50),
                        "p95": self._percentile(recent_values, 95),
                        "p99": self._percentile(recent_values, 99),
                    }

            # Calculate rates (events per minute)
            now = time.time()
            for key, timestamps in self._rate_windows.items():
                if timestamps:
                    # Count events in last minute
                    one_minute_ago = now - 60
                    recent_count = sum(1 for t in timestamps if t > one_minute_ago)
                    summary["rates"][f"{key}_per_minute"] = recent_count

            return summary

    def _make_key(self, metric: str, labels: Optional[Dict[str, str]] = None) -> str:
        """Create a metric key with labels."""
        if not labels:
            return metric
        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{metric}{{{label_str}}}"

    def _percentile(self, values: List[float], percentile: int) -> float:
        """Calculate percentile of values."""
        if not values:
            return 0.0
        sorted_values = sorted(values)
        index = int(len(sorted_values) * percentile / 100)
        return sorted_values[min(index, len(sorted_values) - 1)]


# Global metrics instance
_metrics = MetricsCollector()


def get_metrics() -> MetricsCollector:
    """Get the global metrics collector instance."""
    return _metrics


# Convenience functions
def increment(metric: str, value: int = 1, labels: Optional[Dict[str, str]] = None):
    """Increment a counter metric."""
    _metrics.increment(metric, value, labels)


def record_value(metric: str, value: float, labels: Optional[Dict[str, str]] = None):
    """Record a value for histogram calculation."""
    _metrics.record_value(metric, value, labels)


def set_gauge(metric: str, value: float, labels: Optional[Dict[str, str]] = None):
    """Set a gauge value."""
    _metrics.set_gauge(metric, value, labels)


def record_request(endpoint: str, method: str, status_code: int, duration_ms: float):
    """Record an API request with common metrics."""
    labels = {"endpoint": endpoint, "method": method, "status": str(status_code)}

    # Increment request counter
    increment("api_requests_total", labels=labels)

    # Record response time
    record_value("api_request_duration_ms", duration_ms, labels=labels)

    # Track error rate
    if status_code >= 400:
        increment("api_errors_total", labels=labels)

    # Track rate
    _metrics.record_rate_event("api_requests", labels={"endpoint": endpoint})


def record_guardrail_check(guardrail: str, pipeline_type: str, blocked: bool, duration_ms: float):
    """Record guardrail check metrics."""
    labels = {"guardrail": guardrail, "pipeline": pipeline_type, "blocked": str(blocked).lower()}

    increment("guardrail_checks_total", labels=labels)
    record_value("guardrail_check_duration_ms", duration_ms, labels=labels)

    if blocked:
        increment("guardrail_blocks_total", labels={"guardrail": guardrail})


def export_metrics(format: str = "json") -> str:
    """Export metrics in various formats."""
    summary = _metrics.get_metrics_summary()

    if format == "json":
        return json.dumps(summary, indent=2)
    elif format == "prometheus":
        # Simple Prometheus text format
        lines = []

        # Add basic info
        lines.append(f"# Stinger API Metrics")
        lines.append(f"# Uptime: {summary['uptime_seconds']:.2f} seconds")
        lines.append("")

        # Counters
        if summary["counters"]:
            for key, value in summary["counters"].items():
                base_name = key.split("{")[0]
                lines.append(f"# TYPE {base_name} counter")
                lines.append(f"{key} {value}")
                lines.append("")

        # Gauges
        if summary["gauges"]:
            for key, value in summary["gauges"].items():
                base_name = key.split("{")[0]
                lines.append(f"# TYPE {base_name} gauge")
                lines.append(f"{key} {value}")
                lines.append("")

        # Histograms (simplified - just show average)
        if summary["histograms"]:
            for key, stats in summary["histograms"].items():
                base_name = key.split("{")[0]
                lines.append(f"# TYPE {base_name} summary")
                lines.append(f"{key}_count {stats['count']}")
                lines.append(f"{key}_sum {stats['avg'] * stats['count']:.2f}")
                lines.append("")

        # Always include at least one metric
        if not lines[3:]:  # If no metrics after headers
            lines.append("# TYPE stinger_up gauge")
            lines.append("stinger_up 1")

        return "\n".join(lines)
    else:
        return str(summary)
