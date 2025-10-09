"""
Metrics collection and reporting for Insurance Claim Agent microservices.
Provides integration with Prometheus, StatsD, and custom metrics backends.
"""

import os
import time
import threading
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import json


class MetricType(Enum):
    """Types of metrics supported."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


@dataclass
class Metric:
    """Represents a single metric."""
    name: str
    type: MetricType
    value: float
    labels: Dict[str, str] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    description: str = ""


class MetricsRegistry:
    """
    Central registry for all metrics.
    Thread-safe implementation for concurrent metric updates.
    """
    
    def __init__(self):
        self._metrics: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            'value': 0,
            'type': MetricType.COUNTER,
            'labels': {},
            'description': '',
            'samples': []
        })
        self._lock = threading.RLock()
        self._enabled = os.getenv('METRICS_ENABLED', 'true').lower() == 'true'
        
    def increment(self, metric: str, value: float = 1, labels: Dict[str, str] = None):
        """
        Increment a counter metric.
        
        Args:
            metric: Name of the metric
            value: Value to increment by (default: 1)
            labels: Optional labels for the metric
        """
        if not self._enabled:
            return
            
        with self._lock:
            key = self._get_metric_key(metric, labels)
            self._metrics[key]['value'] += value
            self._metrics[key]['type'] = MetricType.COUNTER
            if labels:
                self._metrics[key]['labels'] = labels
                
    def decrement(self, metric: str, value: float = 1, labels: Dict[str, str] = None):
        """
        Decrement a counter metric.
        
        Args:
            metric: Name of the metric
            value: Value to decrement by (default: 1)
            labels: Optional labels for the metric
        """
        self.increment(metric, -value, labels)
        
    def gauge(self, metric: str, value: float, labels: Dict[str, str] = None):
        """
        Set a gauge metric to a specific value.
        
        Args:
            metric: Name of the metric
            value: Value to set
            labels: Optional labels for the metric
        """
        if not self._enabled:
            return
            
        with self._lock:
            key = self._get_metric_key(metric, labels)
            self._metrics[key]['value'] = value
            self._metrics[key]['type'] = MetricType.GAUGE
            if labels:
                self._metrics[key]['labels'] = labels
                
    def histogram(self, metric: str, value: float, labels: Dict[str, str] = None):
        """
        Record a value in a histogram.
        
        Args:
            metric: Name of the metric
            value: Value to record
            labels: Optional labels for the metric
        """
        if not self._enabled:
            return
            
        with self._lock:
            key = self._get_metric_key(metric, labels)
            self._metrics[key]['type'] = MetricType.HISTOGRAM
            self._metrics[key]['samples'].append(value)
            # Keep only last 1000 samples to prevent memory issues
            if len(self._metrics[key]['samples']) > 1000:
                self._metrics[key]['samples'] = self._metrics[key]['samples'][-1000:]
            if labels:
                self._metrics[key]['labels'] = labels
                
    def timer(self, metric: str, labels: Dict[str, str] = None):
        """
        Context manager for timing operations.
        
        Args:
            metric: Name of the metric
            labels: Optional labels for the metric
            
        Usage:
            with metrics.timer('operation.duration'):
                # Do something
                pass
        """
        return MetricTimer(self, metric, labels)
        
    def _get_metric_key(self, metric: str, labels: Dict[str, str] = None) -> str:
        """Generate a unique key for a metric with labels."""
        if not labels:
            return metric
        label_str = ','.join(f'{k}={v}' for k, v in sorted(labels.items()))
        return f"{metric}{{{label_str}}}"
        
    def get_metrics(self) -> Dict[str, Any]:
        """Get all current metrics."""
        with self._lock:
            return dict(self._metrics)
            
    def reset(self):
        """Reset all metrics."""
        with self._lock:
            self._metrics.clear()
            
    def export_prometheus(self) -> str:
        """
        Export metrics in Prometheus format.
        
        Returns:
            Prometheus-formatted metrics string
        """
        lines = []
        with self._lock:
            for key, data in self._metrics.items():
                metric_name = key.split('{')[0]
                
                # Add description as comment
                if data.get('description'):
                    lines.append(f"# HELP {metric_name} {data['description']}")
                    
                # Add type
                lines.append(f"# TYPE {metric_name} {data['type'].value}")
                
                # Add metric value
                if data['type'] in [MetricType.COUNTER, MetricType.GAUGE]:
                    lines.append(f"{key} {data['value']}")
                elif data['type'] == MetricType.HISTOGRAM and data['samples']:
                    # Calculate histogram buckets
                    samples = sorted(data['samples'])
                    lines.append(f"{key}_count {len(samples)}")
                    lines.append(f"{key}_sum {sum(samples)}")
                    # Add percentiles
                    for percentile in [50, 90, 95, 99]:
                        idx = int(len(samples) * percentile / 100)
                        lines.append(f"{key}_p{percentile} {samples[min(idx, len(samples)-1)]}")
                        
        return '\n'.join(lines)
        
    def export_json(self) -> str:
        """
        Export metrics in JSON format.
        
        Returns:
            JSON-formatted metrics string
        """
        metrics_data = []
        with self._lock:
            for key, data in self._metrics.items():
                metric_name = key.split('{')[0]
                metric_entry = {
                    'name': metric_name,
                    'type': data['type'].value,
                    'value': data['value'],
                    'labels': data.get('labels', {}),
                    'timestamp': time.time()
                }
                
                if data['type'] == MetricType.HISTOGRAM and data['samples']:
                    samples = sorted(data['samples'])
                    metric_entry['histogram'] = {
                        'count': len(samples),
                        'sum': sum(samples),
                        'min': samples[0],
                        'max': samples[-1],
                        'p50': samples[int(len(samples) * 0.5)],
                        'p90': samples[int(len(samples) * 0.9)],
                        'p95': samples[int(len(samples) * 0.95)],
                        'p99': samples[min(int(len(samples) * 0.99), len(samples)-1)]
                    }
                    
                metrics_data.append(metric_entry)
                
        return json.dumps(metrics_data, indent=2)


class MetricTimer:
    """Context manager for timing operations."""
    
    def __init__(self, registry: MetricsRegistry, metric: str, labels: Dict[str, str] = None):
        self.registry = registry
        self.metric = metric
        self.labels = labels
        self.start_time = None
        
    def __enter__(self):
        self.start_time = time.perf_counter()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.perf_counter() - self.start_time
        self.registry.histogram(f"{self.metric}.duration_seconds", duration, self.labels)
        return False


# Global metrics registry instance
_metrics_registry = MetricsRegistry()


# Convenience functions that use the global registry
def increment(metric: str, value: float = 1, labels: Dict[str, str] = None):
    """Increment a counter metric."""
    _metrics_registry.increment(metric, value, labels)


def decrement(metric: str, value: float = 1, labels: Dict[str, str] = None):
    """Decrement a counter metric."""
    _metrics_registry.decrement(metric, value, labels)


def gauge(metric: str, value: float, labels: Dict[str, str] = None):
    """Set a gauge metric."""
    _metrics_registry.gauge(metric, value, labels)


def histogram(metric: str, value: float, labels: Dict[str, str] = None):
    """Record a histogram value."""
    _metrics_registry.histogram(metric, value, labels)


def timer(metric: str, labels: Dict[str, str] = None):
    """Create a timer context manager."""
    return _metrics_registry.timer(metric, labels)


def get_metrics() -> Dict[str, Any]:
    """Get all metrics."""
    return _metrics_registry.get_metrics()


def export_prometheus() -> str:
    """Export metrics in Prometheus format."""
    return _metrics_registry.export_prometheus()


def export_json() -> str:
    """Export metrics in JSON format."""
    return _metrics_registry.export_json()


def reset():
    """Reset all metrics."""
    _metrics_registry.reset()


# Decorator for measuring function execution time
def measure_time(metric_name: str = None):
    """
    Decorator to measure function execution time.
    
    Args:
        metric_name: Name of the metric (defaults to function name)
        
    Usage:
        @measure_time()
        def my_function():
            pass
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            name = metric_name or f"function.{func.__name__}"
            with timer(name):
                return func(*args, **kwargs)
        return wrapper
    return decorator


# Common metric names for standardization
class StandardMetrics:
    """Standard metric names used across the application."""
    
    # API metrics
    API_REQUEST_COUNT = "api.request.count"
    API_REQUEST_DURATION = "api.request.duration"
    API_ERROR_COUNT = "api.error.count"
    
    # Database metrics
    DB_CONNECTION_COUNT = "db.connection.count"
    DB_QUERY_COUNT = "db.query.count"
    DB_QUERY_DURATION = "db.query.duration"
    DB_ERROR_COUNT = "db.error.count"
    
    # Claims processing metrics
    CLAIM_SUBMITTED = "claim.submitted"
    CLAIM_PROCESSED = "claim.processed"
    CLAIM_APPROVED = "claim.approved"
    CLAIM_REJECTED = "claim.rejected"
    CLAIM_PROCESSING_TIME = "claim.processing.time"
    
    # Document metrics
    DOCUMENT_UPLOADED = "document.uploaded"
    DOCUMENT_PROCESSED = "document.processed"
    DOCUMENT_SIZE = "document.size"
    OCR_PROCESSING_TIME = "ocr.processing.time"
    
    # System metrics
    MEMORY_USAGE = "system.memory.usage"
    CPU_USAGE = "system.cpu.usage"
    THREAD_COUNT = "system.thread.count"


# Example usage and testing
if __name__ == '__main__':
    # Test counter metrics
    increment('test.counter', labels={'service': 'test'})
    increment('test.counter', labels={'service': 'test'})
    increment('test.counter', 3, labels={'service': 'test'})
    
    # Test gauge metrics
    gauge('test.gauge', 42.5, labels={'type': 'example'})
    
    # Test histogram metrics
    for i in range(100):
        histogram('test.histogram', i * 0.1, labels={'bucket': 'test'})
    
    # Test timer context manager
    with timer('test.operation'):
        time.sleep(0.1)
    
    # Test decorator
    @measure_time('test.decorated_function')
    def sample_function():
        time.sleep(0.05)
        return "done"
    
    sample_function()
    
    # Export metrics
    print("=== Prometheus Format ===")
    print(export_prometheus())
    
    print("\n=== JSON Format ===")
    print(export_json())
    
    print("\n✅ Metrics module test complete!")