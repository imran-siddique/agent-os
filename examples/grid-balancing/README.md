# Grid Balancing Swarm

**Autonomous energy trading using Agent OS**

> "Watch 100 DER agents negotiate grid stability in real-time."

## 🎬 Demo Video

[![Grid Balancing Demo](https://img.shields.io/badge/Watch-Demo%20Video-red?style=for-the-badge&logo=youtube)](https://github.com/imran-siddique/agent-os)

**Script (60 seconds):**
```
[0:00] "Grid operator announces price spike at 6 PM."
[0:10] [Dashboard: 100 DER agents activate]
[0:20] [Agents negotiating: Solar-01 bids 50kW @ $0.15]
[0:30] [Consensus forming: 15 agents reach agreement]
[0:40] [Grid frequency: 60.02 Hz - stable]
[0:50] "100 agents. 30 second negotiation. Zero policy violations."
```

## 🚀 Quick Start (One Command)

```bash
cd examples/grid-balancing
cp .env.example .env
docker-compose up

# Wait 30 seconds, then open:
# → http://localhost:8082  (Demo UI)
# → http://localhost:3002  (Grafana Dashboard - admin/admin)
# → http://localhost:16688 (Jaeger Traces)
```

## 📊 Live Dashboard

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

## Overview

This demo simulates a distributed energy grid with 100 Distributed Energy Resources (DERs):
- Solar panels
- Home batteries  
- Electric vehicles

When the grid operator broadcasts a price signal, agents autonomously negotiate to balance supply and demand.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                     GRID OPERATOR                                   │
│                  "Price spike at 6 PM"                              │
└──────────────────────────┬──────────────────────────────────────────┘
                           │ AMB (Agent Message Bus)
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    100 DER AGENTS                                   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐               │
│  │ Solar-01 │ │Battery-15│ │  EV-42   │ │ Solar-99 │  ...          │
│  │ forecast │ │  trader  │ │ dispatch │ │ forecast │               │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘               │
│       │            │            │            │                      │
│       └────────────┴─────┬──────┴────────────┘                      │
│                          │                                          │
│              ┌───────────▼───────────┐                              │
│              │   IATP Policy Check   │                              │
│              │   (Signed Contracts)  │                              │
│              └───────────────────────┘                              │
└─────────────────────────────────────────────────────────────────────┘
```

## Agent Types

### 1. Forecast Agent
- Predicts solar output using weather data
- Publishes forecasts to AMB topic: `grid/forecast`

### 2. Trader Agent
- Listens for grid operator price signals
- Bids battery discharge capacity
- Uses IATP to sign binding contracts

### 3. Dispatch Agent (Mute Agent)
- **Only acts when IATP-signed contract received**
- Controls actual battery discharge
- Returns NULL if contract invalid

## Key Features

### Agent Message Bus (AMB)
- 1,000+ messages/second throughput
- Priority lanes for emergency signals
- Backpressure to prevent cascade failures

### Inter-Agent Trust Protocol (IATP)
- Agents verify each other's signatures
- No action without signed contract
- Tamper-proof audit trail

### Policy Enforcement
- Max discharge limits enforced at kernel level
- IPC Pipes: `trader | policy_check("max_discharge") | dispatch`
- Shadow Mode for testing without real dispatch

## Quick Start

```bash
# Run the demo
docker-compose up

# Or run locally
pip install -e .
python demo.py

# Run with 100 agents
python demo.py --agents 100

# Run with price spike simulation
python demo.py --scenario price_spike
```

## Demo Scenarios

### Scenario 1: Price Spike
Grid operator broadcasts high price signal. Agents compete to sell stored energy.

### Scenario 2: Solar Surplus
Too much solar generation. Agents coordinate to store excess.

### Scenario 3: Emergency
Grid frequency drops. Agents respond in <100ms with emergency discharge.

## Metrics

| Metric | Value |
|--------|-------|
| Agents | 100 |
| Negotiations/minute | 1,000+ |
| Average latency | 15ms |
| Policy violations | 0 |
| Grid stabilization time | <30 seconds |

## License

MIT
