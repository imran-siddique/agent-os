# Agent OS Production Examples

> **Enterprise-ready demos** showcasing Agent OS kernel in real industry contexts.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue)](https://www.docker.com/)

## 🌟 Getting Started Examples

Start here if you're new to Agent OS:

| Example | Description | Complexity |
|---------|-------------|------------|
| [**hello-world**](./hello-world/) | Simplest possible example - 15 lines | ⭐ Beginner |
| [**chat-agent**](./chat-agent/) | Interactive chatbot with memory | ⭐⭐ Intermediate |
| [**tool-using-agent**](./tool-using-agent/) | Agent with safe tools | ⭐⭐ Intermediate |

```bash
# Hello World (instant)
cd examples/hello-world && python agent.py

# Chat Agent (interactive)
cd examples/chat-agent && python chat.py

# Tool-Using Agent
cd examples/tool-using-agent && python agent.py
```

---

## 🚀 Production Examples

Full enterprise demos with observability:

```bash
# Pick a demo, run one command
cd examples/carbon-auditor && docker-compose up   # Carbon fraud detection
cd examples/defi-sentinel && docker-compose up    # DeFi attack response
cd examples/grid-balancing && docker-compose up   # Energy trading (100 agents)
cd examples/pharma-compliance && docker-compose up # Document analysis
```

Each demo includes:
- 📊 **Grafana Dashboard** (port 300X)
- 🔍 **Jaeger Tracing** (port 1668X)
- 📈 **Prometheus Metrics** (port 909X)
- 🖥️ **Demo UI** (port 808X)

## 📊 Demo Dashboards

| Demo | UI Port | Grafana | Jaeger |
|------|---------|---------|--------|
| Carbon Auditor | [localhost:8080](http://localhost:8080) | [localhost:3000](http://localhost:3000) | [localhost:16686](http://localhost:16686) |
| DeFi Sentinel | [localhost:8081](http://localhost:8081) | [localhost:3001](http://localhost:3001) | [localhost:16687](http://localhost:16687) |
| Grid Balancing | [localhost:8082](http://localhost:8082) | [localhost:3002](http://localhost:3002) | [localhost:16688](http://localhost:16688) |
| Pharma Compliance | [localhost:8083](http://localhost:8083) | [localhost:3003](http://localhost:3003) | [localhost:16689](http://localhost:16689) |

**Grafana login:** admin / admin

---

## Demo 1: Carbon Credit Auditor 🌲

**"Catch the Phantom Credits"** - Satellite-verified carbon credit fraud detection

```bash
cd examples/carbon-auditor
cp .env.example .env  # Optional: Add API keys
docker-compose up
```

**Live Dashboard:**
```
┌─────────────────────────────────────────┐
│ Carbon Auditor - Live Dashboard         │
├─────────────────────────────────────────┤
│ Agents Active:           3              │
│ Projects Audited:        47             │
│ Fraud Detected:          7 (14.9%)      │
│ CMVK Consensus:          96.3%          │
│ Policy Violations:       0              │
└─────────────────────────────────────────┘
```

**60-Second Video Script:**
```
[0:00] "This is a carbon credit claim. Company says they saved 10,000 tons CO2."
[0:10] "Let's verify with satellite data."
[0:15] [Screen shows CMVK running: GPT-4, Claude, Gemini analyzing]
[0:25] [Dashboard shows: FRAUD DETECTED - Only 6,000 tons verifiable]
[0:35] [Agent OS kernel sends SIGKILL to halt certification]
[0:45] "Zero violations. Deterministic enforcement. Agent OS."
```

---

## Demo 2: DeFi Risk Sentinel 🛡️

**"Stop the Hack Before It Happens"** - Sub-second attack detection

```bash
cd examples/defi-sentinel
cp .env.example .env
docker-compose up
```

**Live Dashboard:**
```
┌─────────────────────────────────────────┐
│ DeFi Sentinel - Attack Detection        │
├─────────────────────────────────────────┤
│ Attacks Blocked:         3              │
│ Transactions Scanned:    12,847         │
│ Value Protected:         $4.7M          │
│ Detection Latency:       45ms (p95)     │
│ Policy Violations:       0              │
└─────────────────────────────────────────┘
```

---

## Demo 3: Grid Balancing Swarm ⚡

**"100 Agents Negotiating Energy"** - Autonomous DER trading

```bash
cd examples/grid-balancing
cp .env.example .env
docker-compose up
```

**Live Dashboard:**
```
┌─────────────────────────────────────────┐
│ Grid Balancing - DER Coordination       │
├─────────────────────────────────────────┤
│ DERs Active:             100            │
│ Grid Load:               450 MW         │
│ Grid Frequency:          60.02 Hz       │
│ Negotiations/sec:        1,247          │
│ Consensus Rate:          97.3%          │
│ Policy Violations:       0              │
└─────────────────────────────────────────┘
```

---

## Demo 4: Pharma Compliance 💊

**"Find Contradictions Humans Miss"** - FDA document analysis

```bash
cd examples/pharma-compliance
cp .env.example .env
docker-compose up
```

**Live Dashboard:**
```
┌─────────────────────────────────────────┐
│ Pharma Compliance - AE Processing       │
├─────────────────────────────────────────┤
│ Reports Processed:       47             │
│ Serious AEs Found:       3              │
│ CMVK Confidence:         96.8%          │
│ Processing Time:         2.4s (avg)     │
│ Policy Violations:       0              │
└─────────────────────────────────────────┘
```

---

## Key Metrics (All Demos)

| Metric | Target | Description |
|--------|--------|-------------|
| `agent_os_violations_total` | 0 | Policy violations |
| `agent_os_policy_check_duration_seconds` | <5ms | Enforcement latency |
| `agent_os_sigkill_total` | tracked | Emergency terminations |
| `agent_os_cmvk_consensus_ratio` | >90% | Model agreement |

---

## Architecture

All demos use the full Agent OS kernel stack:

```
┌─────────────────────────────────────────────────────────┐
│                   Demo Application                       │
├─────────────────────────────────────────────────────────┤
│                     Agent OS Kernel                      │
│  ┌─────────────┬─────────────┬─────────────────────┐    │
│  │   Signals   │    VFS      │   Policy Engine     │    │
│  │ SIGKILL/STOP│ /mem /audit │ Deterministic       │    │
│  └─────────────┴─────────────┴─────────────────────┘    │
│  ┌─────────────┬─────────────┬─────────────────────┐    │
│  │    IATP     │    AMB      │      CMVK           │    │
│  │ Agent Trust │ Message Bus │ Multi-Model Verify  │    │
│  └─────────────┴─────────────┴─────────────────────┘    │
├─────────────────────────────────────────────────────────┤
│                    Observability                         │
│    Prometheus │ Grafana │ Jaeger │ OpenTelemetry       │
└─────────────────────────────────────────────────────────┘
```

## License

MIT
