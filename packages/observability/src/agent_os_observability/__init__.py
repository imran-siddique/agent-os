"""
Agent OS Observability - Production monitoring for AI agent systems.

Provides:
- OpenTelemetry traces for kernel operations
- Prometheus metrics for safety, latency, throughput
- Pre-built Grafana dashboards
"""

from agent_os_observability.tracer import KernelTracer, trace_operation
from agent_os_observability.metrics import KernelMetrics, metrics_endpoint
from agent_os_observability.dashboards import get_grafana_dashboard

__version__ = "0.1.0"
__all__ = [
    "KernelTracer",
    "trace_operation",
    "KernelMetrics",
    "metrics_endpoint",
    "get_grafana_dashboard",
]
