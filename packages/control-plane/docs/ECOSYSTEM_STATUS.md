# Ecosystem Status

> **Last Updated:** January 23, 2026

This page tracks the status of all utility packages in the Agent Control Plane ecosystem.

## Core Framework

| Package | PyPI | Status | Description |
|---------|------|--------|-------------|
| [agent-control-plane](https://pypi.org/project/agent-control-plane/) | ![PyPI](https://img.shields.io/pypi/v/agent-control-plane?color=blue) | ![Status](https://img.shields.io/badge/status-passing-brightgreen) | Layer 3: The Framework - Governance layer for autonomous AI agents |

## Layer 2: Protocol Utilities

These are the foundational utility packages that integrate with the Agent Control Plane.

| Package | PyPI | Status | Description |
|---------|------|--------|-------------|
| [caas-core](https://pypi.org/project/caas-core/) | ![PyPI](https://img.shields.io/pypi/v/caas-core?color=blue) | ![Status](https://img.shields.io/badge/status-passing-brightgreen) | Context-as-a-Service - Context routing and management |
| [cmvk](https://pypi.org/project/cmvk/) | ![PyPI](https://img.shields.io/pypi/v/cmvk?color=blue) | ![Status](https://img.shields.io/badge/status-passing-brightgreen) | Cryptographic Message Verification Kit - Message verification and signing |
| [iatp](https://pypi.org/project/inter-agent-trust-protocol/) | ![PyPI](https://img.shields.io/pypi/v/inter-agent-trust-protocol?color=blue) | ![Status](https://img.shields.io/badge/status-passing-brightgreen) | Inter-Agent Transport Protocol - Secure message transport |
| [amb](https://pypi.org/project/amb-core/) | ![PyPI](https://img.shields.io/pypi/v/amb-core?color=blue) | ![Status](https://img.shields.io/badge/status-passing-brightgreen) | Agent Message Bus - Pub/sub messaging for agents |
| [emk](https://pypi.org/project/emk/) | ![PyPI](https://img.shields.io/pypi/v/emk?color=blue) | ![Status](https://img.shields.io/badge/status-passing-brightgreen) | Event Messaging Kit - Event-driven communication primitives |
| [atr](https://pypi.org/project/agent-tool-registry/) | ![PyPI](https://img.shields.io/pypi/v/agent-tool-registry?color=blue) | ![Status](https://img.shields.io/badge/status-passing-brightgreen) | Agent Tool Registry - Task distribution and routing |

## Installation

All packages are available via pip:

```bash
# Core framework
pip install agent-control-plane

# Individual utilities
pip install caas-core
pip install cmvk
pip install inter-agent-trust-protocol
pip install amb-core
pip install emk
pip install agent-tool-registry
```

## Package Relationships

```
┌─────────────────────────────────────────────────────────────┐
│                  Layer 3: The Framework                      │
│                   agent-control-plane                        │
│         (Governance, Policy, Orchestration)                  │
└─────────────────────────┬───────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
          ▼               ▼               ▼
┌─────────────────────────────────────────────────────────────┐
│                  Layer 2: Protocols                          │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐           │
│  │  iatp   │ │  cmvk   │ │  caas   │ │   amb   │           │
│  │Transport│ │ Verify  │ │ Context │ │ Message │           │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘           │
│  ┌─────────┐ ┌─────────┐                                    │
│  │   emk   │ │   atr   │                                    │
│  │ Events  │ │ Routing │                                    │
│  └─────────┘ └─────────┘                                    │
└─────────────────────────────────────────────────────────────┘
```

## Version Compatibility

| Utility Package | Compatible with agent-control-plane |
|-----------------|-------------------------------------|
| caas-core       | >= 1.2.0                            |
| cmvk            | >= 1.2.0                            |
| iatp            | >= 1.2.0                            |
| amb             | >= 1.2.0                            |
| emk             | >= 1.2.0                            |
| atr             | >= 1.2.0                            |

## Integration Points

Each utility package integrates with Agent Control Plane through defined interfaces:

| Package | Interface | Purpose |
|---------|-----------|---------|
| caas-core | `ContextRoutingInterface` | Context lifecycle and routing |
| cmvk | `VerificationInterface` | Cryptographic verification |
| iatp | `MessageSecurityInterface` | Secure message transport |
| amb | `MessageBusInterface` | Publish/subscribe messaging |
| emk | `EventInterface` | Event-driven patterns |
| atr | `TaskRoutingInterface` | Task distribution |

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines on contributing to any package in the ecosystem.

## License

All packages are released under the [MIT License](../LICENSE).
