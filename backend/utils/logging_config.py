import logging
import sys
import time
from datetime import datetime
from typing import Dict, Any
from functools import wraps
import json
import os


class MetricsCollector:
    """Collect metrics for agents"""

    def __init__(self):
        self.metrics = {
            "requests": {},
            "latencies": {},
            "errors": {},
            "agent_calls": {}
        }
        self.start_time = time.time()

    def record_request(self, endpoint: str):
        """Record an API request"""
        if endpoint not in self.metrics["requests"]:
            self.metrics["requests"][endpoint] = 0
        self.metrics["requests"][endpoint] += 1

    def record_latency(self, operation: str, duration: float):
        """Record operation latency"""
        if operation not in self.metrics["latencies"]:
            self.metrics["latencies"][operation] = []
        self.metrics["latencies"][operation].append(duration)

    def record_error(self, error_type: str):
        """Record an error"""
        if error_type not in self.metrics["errors"]:
            self.metrics["errors"][error_type] = 0
        self.metrics["errors"][error_type] += 1

    def record_agent_call(self, agent_name: str, method: str):
        """Record an agent method call"""
        key = f"{agent_name}.{method}"
        if key not in self.metrics["agent_calls"]:
            self.metrics["agent_calls"][key] = 0
        self.metrics["agent_calls"][key] += 1

    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        uptime = time.time() - self.start_time

        # Calculate average latencies
        avg_latencies = {}
        for operation, latencies in self.metrics["latencies"].items():
            if latencies:
                avg_latencies[operation] = {
                    "avg": sum(latencies) / len(latencies),
                    "min": min(latencies),
                    "max": max(latencies),
                    "count": len(latencies)
                }

        return {
            "uptime_seconds": uptime,
            "timestamp": datetime.now().isoformat(),
            "requests": self.metrics["requests"],
            "latencies": avg_latencies,
            "errors": self.metrics["errors"],
            "agent_calls": self.metrics["agent_calls"]
        }

    def export_metrics(self, file_path: str = "data/metrics.json"):
        """Export metrics to a file"""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            json.dump(self.get_metrics(), f, indent=2)


class TraceLogger:
    """Logger with trace support"""

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.traces = []

    def trace(self, trace_id: str, agent: str, action: str, details: Dict[str, Any] = None):
        """Log a trace event"""
        trace_event = {
            "timestamp": datetime.now().isoformat(),
            "trace_id": trace_id,
            "agent": agent,
            "action": action,
            "details": details or {}
        }
        self.traces.append(trace_event)
        self.logger.info(f"[TRACE:{trace_id}] [{agent}] {action}: {details}")

    def get_traces(self, trace_id: str = None):
        """Get traces, optionally filtered by trace_id"""
        if trace_id:
            return [t for t in self.traces if t["trace_id"] == trace_id]
        return self.traces

    def export_traces(self, file_path: str = "data/traces.json"):
        """Export traces to a file"""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            json.dump(self.traces, f, indent=2)


def setup_logging(log_level: str = "INFO", log_file: str = None):
    """Setup logging configuration"""
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    handlers = [logging.StreamHandler(sys.stdout)]

    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=handlers
    )

    # Reduce noise from external libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


def measure_time(operation_name: str, metrics_collector: MetricsCollector):
    """Decorator to measure execution time"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start
                metrics_collector.record_latency(operation_name, duration)
                return result
            except Exception as e:
                duration = time.time() - start
                metrics_collector.record_latency(operation_name, duration)
                metrics_collector.record_error(type(e).__name__)
                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start
                metrics_collector.record_latency(operation_name, duration)
                return result
            except Exception as e:
                duration = time.time() - start
                metrics_collector.record_latency(operation_name, duration)
                metrics_collector.record_error(type(e).__name__)
                raise

        # Return the appropriate wrapper based on whether the function is async
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


# Global instances
metrics_collector = MetricsCollector()
trace_logger = TraceLogger("timestable-tutor")

# Setup logging
setup_logging(log_level="INFO", log_file="data/app.log")
