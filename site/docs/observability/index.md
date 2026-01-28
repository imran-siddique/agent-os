---
layout: default
title: Observability
parent: Documentation
nav_order: 6
permalink: /docs/observability/
description: "Set up Prometheus metrics, OpenTelemetry tracing, and Grafana dashboards for Agent OS."
---

# Observability
{: .fs-9 }

See everything your agents do. Prometheus metrics, OpenTelemetry tracing, and pre-built dashboards.
{: .fs-6 .fw-300 }

---

## Overview

Agent OS provides full observability out of the box:

| Component | Purpose | Export |
|:----------|:--------|:-------|
| **Metrics** | Counters, gauges, histograms | Prometheus |
| **Tracing** | Distributed traces | OpenTelemetry → Jaeger |
| **Logging** | Structured logs | JSON → any log aggregator |
| **Audit** | Policy decisions | Immutable audit trail |

---

## Quick Start

```python
from agent_os import KernelSpace
from agent_os.observability import enable_metrics, enable_tracing

# Enable Prometheus metrics on port 9090
enable_metrics(port=9090)

# Enable OpenTelemetry tracing
enable_tracing(
    service_name="my-agent-service",
    exporter="jaeger",
    endpoint="http://localhost:14268/api/traces"
)

# Create kernel - observability is automatic
kernel = KernelSpace(policy="strict")
```

---

## Prometheus Metrics

### Available Metrics

#### Kernel Metrics

| Metric | Type | Description |
|:-------|:-----|:------------|
| `agent_os_actions_total` | Counter | Total actions processed |
| `agent_os_violations_total` | Counter | Total policy violations |
| `agent_os_actions_blocked_total` | Counter | Actions blocked by policy |
| `agent_os_action_duration_seconds` | Histogram | Action execution time |
| `agent_os_active_agents` | Gauge | Currently running agents |

#### Policy Metrics

| Metric | Type | Description |
|:-------|:-----|:------------|
| `agent_os_policy_evaluations_total` | Counter | Policy rule evaluations |
| `agent_os_policy_evaluation_duration_seconds` | Histogram | Policy check latency |
| `agent_os_policy_cache_hits_total` | Counter | Policy cache hits |

#### Memory Metrics (EMK)

| Metric | Type | Description |
|:-------|:-----|:------------|
| `agent_os_episodes_total` | Counter | Episodes stored |
| `agent_os_memory_size_bytes` | Gauge | Memory storage size |
| `agent_os_retrieval_duration_seconds` | Histogram | Memory retrieval time |

#### Verification Metrics (CMVK)

| Metric | Type | Description |
|:-------|:-----|:------------|
| `agent_os_verifications_total` | Counter | Verification requests |
| `agent_os_verification_failures_total` | Counter | Failed verifications |
| `agent_os_drift_score` | Histogram | Semantic drift scores |

### Configuration

```python
from agent_os.observability import MetricsConfig, enable_metrics

config = MetricsConfig(
    port=9090,
    path="/metrics",
    namespace="agent_os",
    include_process_metrics=True,
    include_python_metrics=True,
    custom_labels={"environment": "production", "team": "ml-platform"}
)

enable_metrics(config)
```

### Scrape Config (prometheus.yml)

```yaml
scrape_configs:
  - job_name: 'agent-os'
    static_configs:
      - targets: ['localhost:9090']
    scrape_interval: 15s
    metrics_path: /metrics
```

---

## OpenTelemetry Tracing

### Setup

```python
from agent_os.observability import TracingConfig, enable_tracing

config = TracingConfig(
    service_name="my-agent-service",
    exporter="jaeger",  # jaeger | zipkin | otlp | console
    endpoint="http://localhost:14268/api/traces",
    sample_rate=1.0,  # 1.0 = trace everything
    propagators=["tracecontext", "baggage"]
)

enable_tracing(config)
```

### Automatic Instrumentation

Agent OS automatically creates spans for:

- Agent execution (`agent.execute`)
- Policy evaluation (`policy.evaluate`)
- Memory operations (`memory.store`, `memory.retrieve`)
- Verification (`verification.check`)
- Signal dispatch (`signal.dispatch`)

### Custom Spans

```python
from agent_os.observability import tracer

with tracer.start_span("my-custom-operation") as span:
    span.set_attribute("custom.key", "value")
    # Your code here
```

### Jaeger Setup

```bash
# Run Jaeger locally
docker run -d --name jaeger \
  -p 16686:16686 \
  -p 14268:14268 \
  jaegertracing/all-in-one:latest
```

Access UI at `http://localhost:16686`

---

## Grafana Dashboards

Pre-built dashboards for common monitoring needs.

### Agent OS Overview Dashboard

```json
{
  "dashboard": {
    "title": "Agent OS Overview",
    "panels": [
      {
        "title": "Actions per Second",
        "type": "graph",
        "targets": [{
          "expr": "rate(agent_os_actions_total[5m])"
        }]
      },
      {
        "title": "Violation Rate",
        "type": "stat",
        "targets": [{
          "expr": "rate(agent_os_violations_total[5m]) / rate(agent_os_actions_total[5m]) * 100"
        }]
      },
      {
        "title": "P95 Action Latency",
        "type": "gauge",
        "targets": [{
          "expr": "histogram_quantile(0.95, rate(agent_os_action_duration_seconds_bucket[5m]))"
        }]
      },
      {
        "title": "Active Agents",
        "type": "stat",
        "targets": [{
          "expr": "agent_os_active_agents"
        }]
      }
    ]
  }
}
```

### Download Pre-built Dashboards

| Dashboard | Description | Download |
|:----------|:------------|:---------|
| Overview | Key metrics at a glance | [JSON](https://github.com/imran-siddique/agent-os/blob/main/dashboards/overview.json) |
| Policy | Policy evaluation details | [JSON](https://github.com/imran-siddique/agent-os/blob/main/dashboards/policy.json) |
| Memory | EMK performance | [JSON](https://github.com/imran-siddique/agent-os/blob/main/dashboards/memory.json) |
| Verification | CMVK drift analysis | [JSON](https://github.com/imran-siddique/agent-os/blob/main/dashboards/verification.json) |

### Import to Grafana

1. Open Grafana → Dashboards → Import
2. Upload JSON or paste dashboard ID
3. Select Prometheus data source
4. Click Import

---

## Structured Logging

### Configuration

```python
from agent_os.observability import LoggingConfig, configure_logging

config = LoggingConfig(
    level="INFO",  # DEBUG | INFO | WARNING | ERROR
    format="json",  # json | text
    output="stdout",  # stdout | file | both
    file_path="/var/log/agent-os/agent.log",
    include_trace_ids=True,  # Correlate with traces
    redact_secrets=True  # Redact sensitive data
)

configure_logging(config)
```

### Log Format

```json
{
  "timestamp": "2026-01-28T17:45:00.123Z",
  "level": "INFO",
  "message": "Action executed",
  "agent_id": "agent-001",
  "action": "sql",
  "resource": "SELECT * FROM users",
  "decision": "allow",
  "duration_ms": 5.2,
  "trace_id": "abc123def456",
  "span_id": "789xyz"
}
```

### Log Shipping

Works with any log aggregator:

```yaml
# Fluentd config
<source>
  @type tail
  path /var/log/agent-os/*.log
  format json
  tag agent-os
</source>

<match agent-os.**>
  @type elasticsearch
  host localhost
  port 9200
  index_name agent-os
</match>
```

---

## Audit Trail

Every policy decision is recorded in an immutable audit log.

### Query Audit Logs

```python
from agent_os import KernelSpace

kernel = KernelSpace(policy="strict")

# Query recent violations
violations = kernel.audit.query(
    decision="deny",
    time_range="last_24h",
    limit=100
)

for v in violations:
    print(f"{v.timestamp} | {v.agent_id} | {v.action} | {v.reason}")
```

### Audit Log Format

```json
{
  "id": "audit-001",
  "timestamp": "2026-01-28T17:45:00.123Z",
  "agent_id": "agent-001",
  "action": "file_write",
  "resource": "/prod/config.yaml",
  "decision": "deny",
  "reason": "Production writes blocked",
  "rule_id": "rule-005",
  "context": {
    "user": "system",
    "session_id": "sess-123"
  },
  "signature": "sha256:abc123..."  // Tamper-proof
}
```

### Compliance Reports

```python
# Generate compliance report
report = kernel.audit.generate_report(
    format="pdf",  # pdf | csv | json
    time_range="last_30_days",
    include_summary=True,
    include_violations=True,
    include_statistics=True
)

report.save("compliance-report-january.pdf")
```

---

## Alerting

### Prometheus Alerting Rules

```yaml
# prometheus-alerts.yml
groups:
  - name: agent-os
    rules:
      - alert: HighViolationRate
        expr: rate(agent_os_violations_total[5m]) > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High policy violation rate"
          
      - alert: AgentDown
        expr: agent_os_active_agents == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "No active agents"
          
      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(agent_os_action_duration_seconds_bucket[5m])) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High action latency (>1s p95)"
```

### PagerDuty Integration

```python
from agent_os.observability import AlertConfig

alert_config = AlertConfig(
    provider="pagerduty",
    api_key="your-pagerduty-key",
    service_id="your-service-id",
    rules=[
        {"type": "violation", "severity": "critical", "alert": True},
        {"type": "latency_spike", "threshold_ms": 1000, "alert": True}
    ]
)

kernel = KernelSpace(policy="strict", alerts=alert_config)
```

---

## Example: Full Observability Stack

```yaml
# docker-compose.yml
version: '3.8'
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9091:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      
  jaeger:
    image: jaegertracing/all-in-one
    ports:
      - "16686:16686"
      - "14268:14268"
      
  agent-os-app:
    build: .
    environment:
      - METRICS_PORT=9090
      - JAEGER_ENDPOINT=http://jaeger:14268/api/traces
```

---

## Next Steps

- [Policy Reference](/docs/policies/) — Define what to monitor
- [Benchmarks](/benchmarks/) — Performance expectations
- [Tutorials](/docs/tutorials/) — Hands-on examples
