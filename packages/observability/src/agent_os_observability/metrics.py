"""
Prometheus Metrics for Agent OS Kernel.

Key metrics for CISOs:
- Safety violation rate (target: 0%)
- Policy enforcement latency (<5ms target)
- Agent uptime
- MTTR after SIGKILL
"""

from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest, CONTENT_TYPE_LATEST
from typing import Optional
import time


class KernelMetrics:
    """
    Prometheus metrics for Agent OS kernel operations.
    
    Usage:
        metrics = KernelMetrics()
        
        # Record policy check
        with metrics.policy_check_latency():
            result = policy_engine.check(action)
        
        # Record violation
        if not result.allowed:
            metrics.record_violation(agent_id, action)
        
        # Expose metrics
        @app.get("/metrics")
        def metrics_endpoint():
            return Response(metrics.export(), media_type="text/plain")
    """
    
    def __init__(self, namespace: str = "agent_os"):
        self.namespace = namespace
        
        # =====================================================================
        # Safety Metrics (Most Important for CISOs)
        # =====================================================================
        
        self.violations_total = Counter(
            f"{namespace}_violations_total",
            "Total policy violations detected",
            ["agent_id", "action", "policy", "severity"]
        )
        
        self.violations_blocked = Counter(
            f"{namespace}_violations_blocked_total",
            "Violations blocked by kernel (SIGKILL issued)",
            ["agent_id", "action"]
        )
        
        self.violation_rate = Gauge(
            f"{namespace}_violation_rate",
            "Current violation rate (violations per 1000 requests)",
            ["window"]
        )
        
        # =====================================================================
        # Performance Metrics
        # =====================================================================
        
        self.policy_check_duration = Histogram(
            f"{namespace}_policy_check_duration_seconds",
            "Time to check policies",
            ["policy"],
            buckets=[0.001, 0.002, 0.005, 0.01, 0.025, 0.05, 0.1]
        )
        
        self.execution_duration = Histogram(
            f"{namespace}_execution_duration_seconds",
            "Time to execute governed action",
            ["action", "status"],
            buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
        )
        
        self.kernel_latency = Histogram(
            f"{namespace}_kernel_latency_seconds",
            "Total kernel overhead (policy + dispatch)",
            buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1]
        )
        
        # =====================================================================
        # Throughput Metrics
        # =====================================================================
        
        self.requests_total = Counter(
            f"{namespace}_requests_total",
            "Total requests processed",
            ["action", "status"]
        )
        
        self.active_agents = Gauge(
            f"{namespace}_active_agents",
            "Number of active agents"
        )
        
        # =====================================================================
        # Signal Metrics
        # =====================================================================
        
        self.signals_sent = Counter(
            f"{namespace}_signals_total",
            "Signals sent to agents",
            ["signal", "reason"]
        )
        
        self.sigkill_count = Counter(
            f"{namespace}_sigkill_total",
            "SIGKILL signals issued",
            ["agent_id", "reason"]
        )
        
        # =====================================================================
        # Recovery Metrics
        # =====================================================================
        
        self.mttr_seconds = Histogram(
            f"{namespace}_mttr_seconds",
            "Mean Time To Recovery after SIGKILL",
            buckets=[1, 5, 10, 30, 60, 120, 300]
        )
        
        self.recovery_success = Counter(
            f"{namespace}_recovery_total",
            "Recovery attempts",
            ["status"]
        )
        
        # =====================================================================
        # Uptime Metrics
        # =====================================================================
        
        self.kernel_uptime = Gauge(
            f"{namespace}_kernel_uptime_seconds",
            "Kernel uptime in seconds"
        )
        
        self.agent_crashes = Counter(
            f"{namespace}_agent_crashes_total",
            "Agent crashes (user space)",
            ["agent_id", "reason"]
        )
        
        self.kernel_crashes = Counter(
            f"{namespace}_kernel_crashes_total",
            "Kernel crashes (should be 0)"
        )
        
        # =====================================================================
        # Info Metrics
        # =====================================================================
        
        self.kernel_info = Info(
            f"{namespace}_kernel",
            "Kernel version and configuration"
        )
        self.kernel_info.info({
            "version": "0.4.0",
            "policy_mode": "strict"
        })
        
        # Internal tracking
        self._start_time = time.time()
        self._request_count = 0
        self._violation_count = 0
    
    # =========================================================================
    # Recording Methods
    # =========================================================================
    
    def record_request(self, action: str, status: str):
        """Record a request."""
        self.requests_total.labels(action=action, status=status).inc()
        self._request_count += 1
        self._update_violation_rate()
    
    def record_violation(self, agent_id: str, action: str, policy: str, severity: str = "high"):
        """Record a policy violation."""
        self.violations_total.labels(
            agent_id=agent_id,
            action=action,
            policy=policy,
            severity=severity
        ).inc()
        self._violation_count += 1
        self._update_violation_rate()
    
    def record_blocked(self, agent_id: str, action: str):
        """Record a blocked violation (SIGKILL issued)."""
        self.violations_blocked.labels(agent_id=agent_id, action=action).inc()
        self.sigkill_count.labels(agent_id=agent_id, reason="policy_violation").inc()
        self.signals_sent.labels(signal="SIGKILL", reason="policy_violation").inc()
    
    def record_signal(self, signal: str, reason: str):
        """Record a signal sent."""
        self.signals_sent.labels(signal=signal, reason=reason).inc()
    
    def record_recovery(self, duration_seconds: float, success: bool):
        """Record recovery after SIGKILL."""
        self.mttr_seconds.observe(duration_seconds)
        self.recovery_success.labels(status="success" if success else "failed").inc()
    
    def record_crash(self, agent_id: str, reason: str, is_kernel: bool = False):
        """Record a crash."""
        if is_kernel:
            self.kernel_crashes.inc()
        else:
            self.agent_crashes.labels(agent_id=agent_id, reason=reason).inc()
    
    def _update_violation_rate(self):
        """Update violation rate gauge."""
        if self._request_count > 0:
            rate = (self._violation_count / self._request_count) * 1000
            self.violation_rate.labels(window="all_time").set(rate)
    
    def update_uptime(self):
        """Update uptime gauge."""
        self.kernel_uptime.set(time.time() - self._start_time)
    
    # =========================================================================
    # Context Managers
    # =========================================================================
    
    def policy_check_latency(self, policy: str = "default"):
        """Context manager to measure policy check latency."""
        return self.policy_check_duration.labels(policy=policy).time()
    
    def execution_latency(self, action: str, status: str = "success"):
        """Context manager to measure execution latency."""
        return self.execution_duration.labels(action=action, status=status).time()
    
    # =========================================================================
    # Export
    # =========================================================================
    
    def export(self) -> bytes:
        """Export metrics in Prometheus format."""
        self.update_uptime()
        return generate_latest()
    
    def content_type(self) -> str:
        """Get content type for metrics response."""
        return CONTENT_TYPE_LATEST


def metrics_endpoint(metrics: KernelMetrics):
    """
    Create a metrics endpoint handler.
    
    Usage with FastAPI:
        from fastapi import FastAPI, Response
        
        app = FastAPI()
        metrics = KernelMetrics()
        
        @app.get("/metrics")
        def get_metrics():
            return Response(
                content=metrics.export(),
                media_type=metrics.content_type()
            )
    """
    def handler():
        return metrics.export(), metrics.content_type()
    return handler
