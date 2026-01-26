"""
Pre-built Grafana Dashboards for Agent OS.

Provides JSON dashboard definitions ready for import.
"""

import json


def get_grafana_dashboard(name: str = "agent-os-overview") -> dict:
    """
    Get a pre-built Grafana dashboard.
    
    Available dashboards:
    - agent-os-overview: Main overview for SOC teams
    - agent-os-safety: Safety metrics detail
    - agent-os-performance: Performance metrics
    - agent-os-amb: AMB health and throughput
    
    Usage:
        dashboard = get_grafana_dashboard("agent-os-overview")
        # Import via Grafana API or UI
    """
    dashboards = {
        "agent-os-overview": _overview_dashboard(),
        "agent-os-safety": _safety_dashboard(),
        "agent-os-performance": _performance_dashboard(),
        "agent-os-amb": _amb_dashboard(),
    }
    return dashboards.get(name, dashboards["agent-os-overview"])


def _overview_dashboard() -> dict:
    """Main Agent OS overview dashboard."""
    return {
        "dashboard": {
            "id": None,
            "uid": "agent-os-overview",
            "title": "Agent OS - Overview",
            "tags": ["agent-os", "ai-safety"],
            "timezone": "browser",
            "schemaVersion": 38,
            "version": 1,
            "refresh": "10s",
            "panels": [
                # Row 1: Key Safety Metrics
                {
                    "id": 1,
                    "type": "stat",
                    "title": "Violation Rate",
                    "gridPos": {"h": 4, "w": 6, "x": 0, "y": 0},
                    "targets": [
                        {
                            "expr": "agent_os_violation_rate{window='all_time'}",
                            "refId": "A"
                        }
                    ],
                    "options": {
                        "colorMode": "value",
                        "graphMode": "none",
                        "orientation": "auto",
                        "textMode": "value_and_name"
                    },
                    "fieldConfig": {
                        "defaults": {
                            "unit": "percentunit",
                            "thresholds": {
                                "mode": "absolute",
                                "steps": [
                                    {"color": "green", "value": None},
                                    {"color": "yellow", "value": 0.001},
                                    {"color": "red", "value": 0.01}
                                ]
                            }
                        }
                    }
                },
                {
                    "id": 2,
                    "type": "stat",
                    "title": "SIGKILL Count (24h)",
                    "gridPos": {"h": 4, "w": 6, "x": 6, "y": 0},
                    "targets": [
                        {
                            "expr": "increase(agent_os_sigkill_total[24h])",
                            "refId": "A"
                        }
                    ],
                    "options": {"colorMode": "value"}
                },
                {
                    "id": 3,
                    "type": "stat",
                    "title": "Kernel Uptime",
                    "gridPos": {"h": 4, "w": 6, "x": 12, "y": 0},
                    "targets": [
                        {
                            "expr": "agent_os_kernel_uptime_seconds",
                            "refId": "A"
                        }
                    ],
                    "fieldConfig": {
                        "defaults": {"unit": "s"}
                    }
                },
                {
                    "id": 4,
                    "type": "stat",
                    "title": "Active Agents",
                    "gridPos": {"h": 4, "w": 6, "x": 18, "y": 0},
                    "targets": [
                        {
                            "expr": "agent_os_active_agents",
                            "refId": "A"
                        }
                    ]
                },
                
                # Row 2: Time Series
                {
                    "id": 5,
                    "type": "timeseries",
                    "title": "Requests per Second",
                    "gridPos": {"h": 8, "w": 12, "x": 0, "y": 4},
                    "targets": [
                        {
                            "expr": "rate(agent_os_requests_total[1m])",
                            "legendFormat": "{{action}} - {{status}}",
                            "refId": "A"
                        }
                    ]
                },
                {
                    "id": 6,
                    "type": "timeseries",
                    "title": "Policy Check Latency (p99)",
                    "gridPos": {"h": 8, "w": 12, "x": 12, "y": 4},
                    "targets": [
                        {
                            "expr": "histogram_quantile(0.99, rate(agent_os_policy_check_duration_seconds_bucket[5m]))",
                            "legendFormat": "p99",
                            "refId": "A"
                        },
                        {
                            "expr": "histogram_quantile(0.50, rate(agent_os_policy_check_duration_seconds_bucket[5m]))",
                            "legendFormat": "p50",
                            "refId": "B"
                        }
                    ],
                    "fieldConfig": {
                        "defaults": {
                            "unit": "s",
                            "thresholds": {
                                "steps": [
                                    {"color": "green", "value": None},
                                    {"color": "yellow", "value": 0.005},
                                    {"color": "red", "value": 0.01}
                                ]
                            }
                        }
                    }
                },
                
                # Row 3: Violations and Signals
                {
                    "id": 7,
                    "type": "timeseries",
                    "title": "Violations Over Time",
                    "gridPos": {"h": 8, "w": 12, "x": 0, "y": 12},
                    "targets": [
                        {
                            "expr": "rate(agent_os_violations_total[5m])",
                            "legendFormat": "{{policy}}",
                            "refId": "A"
                        }
                    ],
                    "fieldConfig": {
                        "defaults": {
                            "custom": {
                                "fillOpacity": 30
                            }
                        }
                    }
                },
                {
                    "id": 8,
                    "type": "timeseries",
                    "title": "Signals Sent",
                    "gridPos": {"h": 8, "w": 12, "x": 12, "y": 12},
                    "targets": [
                        {
                            "expr": "rate(agent_os_signals_total[5m])",
                            "legendFormat": "{{signal}}",
                            "refId": "A"
                        }
                    ]
                },
                
                # Row 4: Recovery
                {
                    "id": 9,
                    "type": "histogram",
                    "title": "MTTR Distribution",
                    "gridPos": {"h": 8, "w": 12, "x": 0, "y": 20},
                    "targets": [
                        {
                            "expr": "agent_os_mttr_seconds_bucket",
                            "refId": "A"
                        }
                    ],
                    "fieldConfig": {
                        "defaults": {"unit": "s"}
                    }
                },
                {
                    "id": 10,
                    "type": "table",
                    "title": "Recent Violations",
                    "gridPos": {"h": 8, "w": 12, "x": 12, "y": 20},
                    "targets": [
                        {
                            "expr": "topk(10, agent_os_violations_total)",
                            "format": "table",
                            "refId": "A"
                        }
                    ]
                }
            ]
        },
        "folderId": 0,
        "overwrite": True
    }


def _safety_dashboard() -> dict:
    """Detailed safety metrics dashboard."""
    return {
        "dashboard": {
            "id": None,
            "uid": "agent-os-safety",
            "title": "Agent OS - Safety Metrics",
            "tags": ["agent-os", "ai-safety", "compliance"],
            "timezone": "browser",
            "schemaVersion": 38,
            "version": 1,
            "panels": [
                {
                    "id": 1,
                    "type": "stat",
                    "title": "30-Day Violation Count",
                    "gridPos": {"h": 6, "w": 8, "x": 0, "y": 0},
                    "targets": [
                        {
                            "expr": "increase(agent_os_violations_total[30d])",
                            "refId": "A"
                        }
                    ],
                    "fieldConfig": {
                        "defaults": {
                            "thresholds": {
                                "steps": [
                                    {"color": "green", "value": None},
                                    {"color": "red", "value": 1}
                                ]
                            }
                        }
                    }
                }
            ]
        }
    }


def _performance_dashboard() -> dict:
    """Performance metrics dashboard."""
    return {
        "dashboard": {
            "id": None,
            "uid": "agent-os-performance",
            "title": "Agent OS - Performance",
            "tags": ["agent-os", "performance"],
            "timezone": "browser",
            "schemaVersion": 38,
            "version": 1,
            "panels": []
        }
    }


def export_dashboard(name: str, path: str):
    """Export dashboard to JSON file."""
    dashboard = get_grafana_dashboard(name)
    with open(path, "w") as f:
        json.dump(dashboard, f, indent=2)


def _amb_dashboard() -> dict:
    """AMB (Agent Message Bus) health dashboard."""
    return {
        "dashboard": {
            "id": None,
            "uid": "agent-os-amb",
            "title": "Agent OS - AMB Health",
            "tags": ["agent-os", "amb", "messaging"],
            "timezone": "browser",
            "schemaVersion": 38,
            "version": 1,
            "refresh": "5s",
            "panels": [
                # Row 1: Key Metrics
                {
                    "id": 1,
                    "type": "stat",
                    "title": "Messages/sec",
                    "gridPos": {"h": 4, "w": 6, "x": 0, "y": 0},
                    "targets": [
                        {
                            "expr": "sum(rate(amb_messages_published_total[1m]))",
                            "refId": "A"
                        }
                    ],
                    "fieldConfig": {
                        "defaults": {
                            "unit": "msg/s",
                            "thresholds": {
                                "steps": [
                                    {"color": "green", "value": None},
                                    {"color": "yellow", "value": 10000},
                                    {"color": "red", "value": 50000}
                                ]
                            }
                        }
                    }
                },
                {
                    "id": 2,
                    "type": "stat",
                    "title": "Queue Depth",
                    "gridPos": {"h": 4, "w": 6, "x": 6, "y": 0},
                    "targets": [
                        {
                            "expr": "sum(amb_queue_depth)",
                            "refId": "A"
                        }
                    ],
                    "fieldConfig": {
                        "defaults": {
                            "thresholds": {
                                "steps": [
                                    {"color": "green", "value": None},
                                    {"color": "yellow", "value": 500},
                                    {"color": "red", "value": 1000}
                                ]
                            }
                        }
                    }
                },
                {
                    "id": 3,
                    "type": "stat",
                    "title": "Backpressure Events (1h)",
                    "gridPos": {"h": 4, "w": 6, "x": 12, "y": 0},
                    "targets": [
                        {
                            "expr": "increase(amb_backpressure_activated_total[1h])",
                            "refId": "A"
                        }
                    ],
                    "fieldConfig": {
                        "defaults": {
                            "thresholds": {
                                "steps": [
                                    {"color": "green", "value": None},
                                    {"color": "yellow", "value": 1},
                                    {"color": "red", "value": 10}
                                ]
                            }
                        }
                    }
                },
                {
                    "id": 4,
                    "type": "stat",
                    "title": "Delivery Failures (1h)",
                    "gridPos": {"h": 4, "w": 6, "x": 18, "y": 0},
                    "targets": [
                        {
                            "expr": "increase(amb_delivery_failures_total[1h])",
                            "refId": "A"
                        }
                    ],
                    "fieldConfig": {
                        "defaults": {
                            "thresholds": {
                                "steps": [
                                    {"color": "green", "value": None},
                                    {"color": "yellow", "value": 1},
                                    {"color": "red", "value": 10}
                                ]
                            }
                        }
                    }
                },
                
                # Row 2: Throughput
                {
                    "id": 5,
                    "type": "timeseries",
                    "title": "Message Throughput",
                    "gridPos": {"h": 8, "w": 12, "x": 0, "y": 4},
                    "targets": [
                        {
                            "expr": "rate(amb_messages_published_total[1m])",
                            "legendFormat": "Published - {{topic}}",
                            "refId": "A"
                        },
                        {
                            "expr": "rate(amb_messages_delivered_total[1m])",
                            "legendFormat": "Delivered - {{topic}}",
                            "refId": "B"
                        }
                    ],
                    "fieldConfig": {
                        "defaults": {"unit": "msg/s"}
                    }
                },
                {
                    "id": 6,
                    "type": "timeseries",
                    "title": "Queue Depth by Topic",
                    "gridPos": {"h": 8, "w": 12, "x": 12, "y": 4},
                    "targets": [
                        {
                            "expr": "amb_queue_depth",
                            "legendFormat": "{{topic}}",
                            "refId": "A"
                        }
                    ]
                },
                
                # Row 3: Latency
                {
                    "id": 7,
                    "type": "timeseries",
                    "title": "Publish Latency",
                    "gridPos": {"h": 8, "w": 12, "x": 0, "y": 12},
                    "targets": [
                        {
                            "expr": "histogram_quantile(0.99, rate(amb_publish_duration_seconds_bucket[5m]))",
                            "legendFormat": "p99",
                            "refId": "A"
                        },
                        {
                            "expr": "histogram_quantile(0.95, rate(amb_publish_duration_seconds_bucket[5m]))",
                            "legendFormat": "p95",
                            "refId": "B"
                        },
                        {
                            "expr": "histogram_quantile(0.50, rate(amb_publish_duration_seconds_bucket[5m]))",
                            "legendFormat": "p50",
                            "refId": "C"
                        }
                    ],
                    "fieldConfig": {
                        "defaults": {
                            "unit": "s",
                            "thresholds": {
                                "steps": [
                                    {"color": "green", "value": None},
                                    {"color": "yellow", "value": 0.01},
                                    {"color": "red", "value": 0.1}
                                ]
                            }
                        }
                    }
                },
                {
                    "id": 8,
                    "type": "timeseries",
                    "title": "Delivery Latency",
                    "gridPos": {"h": 8, "w": 12, "x": 12, "y": 12},
                    "targets": [
                        {
                            "expr": "histogram_quantile(0.99, rate(amb_delivery_duration_seconds_bucket[5m]))",
                            "legendFormat": "p99",
                            "refId": "A"
                        },
                        {
                            "expr": "histogram_quantile(0.50, rate(amb_delivery_duration_seconds_bucket[5m]))",
                            "legendFormat": "p50",
                            "refId": "B"
                        }
                    ],
                    "fieldConfig": {
                        "defaults": {"unit": "s"}
                    }
                },
                
                # Row 4: Health
                {
                    "id": 9,
                    "type": "timeseries",
                    "title": "Priority Lane Distribution",
                    "gridPos": {"h": 8, "w": 12, "x": 0, "y": 20},
                    "targets": [
                        {
                            "expr": "rate(amb_messages_published_total[5m])",
                            "legendFormat": "{{priority}}",
                            "refId": "A"
                        }
                    ],
                    "options": {
                        "legend": {"displayMode": "table"}
                    }
                },
                {
                    "id": 10,
                    "type": "table",
                    "title": "Dead Letter Queue",
                    "gridPos": {"h": 8, "w": 12, "x": 12, "y": 20},
                    "targets": [
                        {
                            "expr": "amb_dlq_messages_total",
                            "format": "table",
                            "refId": "A"
                        }
                    ],
                    "fieldConfig": {
                        "defaults": {
                            "thresholds": {
                                "steps": [
                                    {"color": "green", "value": None},
                                    {"color": "red", "value": 1}
                                ]
                            }
                        }
                    }
                },
                
                # Row 5: Broker Health
                {
                    "id": 11,
                    "type": "stat",
                    "title": "Broker Status",
                    "gridPos": {"h": 4, "w": 8, "x": 0, "y": 28},
                    "targets": [
                        {
                            "expr": "amb_broker_connected",
                            "refId": "A"
                        }
                    ],
                    "fieldConfig": {
                        "defaults": {
                            "mappings": [
                                {"type": "value", "options": {"1": {"text": "Connected", "color": "green"}}},
                                {"type": "value", "options": {"0": {"text": "Disconnected", "color": "red"}}}
                            ]
                        }
                    }
                },
                {
                    "id": 12,
                    "type": "stat",
                    "title": "Persistence Status",
                    "gridPos": {"h": 4, "w": 8, "x": 8, "y": 28},
                    "targets": [
                        {
                            "expr": "amb_persistence_enabled",
                            "refId": "A"
                        }
                    ],
                    "fieldConfig": {
                        "defaults": {
                            "mappings": [
                                {"type": "value", "options": {"1": {"text": "Enabled", "color": "green"}}},
                                {"type": "value", "options": {"0": {"text": "Disabled", "color": "yellow"}}}
                            ]
                        }
                    }
                },
                {
                    "id": 13,
                    "type": "stat",
                    "title": "Messages in WAL",
                    "gridPos": {"h": 4, "w": 8, "x": 16, "y": 28},
                    "targets": [
                        {
                            "expr": "amb_wal_messages_pending",
                            "refId": "A"
                        }
                    ]
                }
            ]
        },
        "folderId": 0,
        "overwrite": True
    }
