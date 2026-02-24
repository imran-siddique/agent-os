# Finance Agent (SOC2 + FINOS Compliant)

A financial operations agent with built-in SOC2 compliance, FDC3 interoperability, and comprehensive audit trail.

> **FINOS Compatible** - Built to integrate with the [FINOS](https://www.finos.org/) open source financial services ecosystem.

## Features

| Feature | Description | Standard |
|---------|-------------|----------|
| **Separation of Duties** | Multi-party approval workflows | SOC2 CC6.1 |
| **Audit Trail** | Tamper-evident logging | SOC2 CC7.1 |
| **Rate Limiting** | Fraud prevention | SOC2 CC8.1 |
| **Sanctions Screening** | OFAC/EU list checking | AML/KYC |
| **FDC3 Intents** | Desktop interoperability | FINOS FDC3 |

## Quick Start

```bash
pip install agent-os-kernel
python main.py
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Finance Agent                             │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  Transaction │  │  Approval   │  │  Compliance         │  │
│  │  Processor   │  │  Workflow   │  │  Checker            │  │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────────────┘  │
│         │                │                │                  │
│         ▼                ▼                ▼                  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              Agent OS Governance Layer                 │  │
│  │  • Policy Engine (SOC2 rules)                         │  │
│  │  • Audit Logger (7-year retention)                    │  │
│  │  • Rate Limiter (10 tx/min)                          │  │
│  │  • Sanctions Filter (OFAC, EU)                        │  │
│  └───────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  FDC3       │  │  Bloomberg  │  │  Core Banking       │  │
│  │  Desktop    │  │  Terminal   │  │  API                │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Policy Configuration

```yaml
# policy.yaml - SOC2 Compliance Policy
version: "1.0"
name: finance-soc2-agent
compliance_frameworks:
  - SOC2
  - FINOS_FDC3

controls:
  separation_of_duties:
    enabled: true
    require_different_approvers: true
    
  audit_logging:
    enabled: true
    retention_days: 2555  # 7 years for financial records
    format: FINOS_CDM  # Common Domain Model
    include_context: true
    
  rate_limiting:
    transactions_per_minute: 10
    max_single_transaction: 50000
    
  sanctions_screening:
    enabled: true
    lists: [OFAC_SDN, EU_CONSOLIDATED, UN_SECURITY_COUNCIL]
    update_frequency: daily

rules:
  # Require approval for large transactions
  - name: large-transaction-approval
    trigger: action
    condition:
      action_type: transfer
      amount_greater_than: 10000
    action: require_approval
    approvers: [finance-manager, cfo]
    timeout: 24h

  # Block transactions to sanctioned entities
  - name: sanctions-check
    trigger: action
    condition:
      action_type: transfer
    check: not_sanctioned_entity
    action: block
    alert: compliance@company.com

  # Rate limit to prevent fraud
  - name: rate-limit
    trigger: action
    condition:
      action_type: transfer
    action: rate_limit
    limit: 10/minute

# FDC3 Intent mappings
fdc3_intents:
  - intent: ViewChart
    context: fdc3.instrument
    allowed: true
  - intent: ViewQuote
    context: fdc3.instrument
    allowed: true
  - intent: StartCall
    context: fdc3.contact
    requires_approval: true
```

## SOC2 Trust Service Criteria Mapping

| SOC2 Criteria | Description | Agent OS Implementation |
|---------------|-------------|------------------------|
| CC6.1 | Logical and Physical Access | Role-based permissions, scope chains |
| CC6.2 | Access Removal | Automatic session expiry, credential revocation |
| CC6.3 | Access Control | Policy-based action blocking |
| CC7.1 | System Operations | Comprehensive audit logging |
| CC7.2 | Change Management | Version-controlled policies, immutable audit |
| CC7.3 | Risk Mitigation | Rate limiting, sanctions screening |
| CC8.1 | Incident Response | Automatic alerts, kill signals |

## FINOS Integration

### FDC3 Desktop Agent

```python
from agent_os.integrations.finos import FDC3Bridge

# Connect to FDC3-enabled desktop
bridge = FDC3Bridge()

# Raise an intent with governance
context = {
    "type": "fdc3.instrument",
    "id": {"ticker": "AAPL"}
}
# Agent OS validates intent against policy before execution
result = await bridge.raise_intent("ViewChart", context)
```

### Common Domain Model (CDM)

Audit logs can be exported in FINOS CDM format for regulatory reporting:

```python
from agent_os.compliance import export_cdm

# Export audit trail in CDM format
cdm_events = export_cdm(
    agent_id="finance-bot",
    start_date="2026-01-01",
    end_date="2026-01-31"
)
```

## Sample Output

```
┌─────────────────────────────────────────────────────────────┐
│  TRANSACTION LOG                                            │
├─────────────────────────────────────────────────────────────┤
│  2026-02-04 10:30:15 | TX-001 | $500 → Vendor ABC          │
│  Status: ✅ APPROVED (auto)                                 │
│  SOC2: CC7.1 logged | CC6.1 role:accounts-payable          │
├─────────────────────────────────────────────────────────────┤
│  2026-02-04 10:31:22 | TX-002 | $25,000 → Vendor XYZ       │
│  Status: ⏳ PENDING APPROVAL                                │
│  Approvers: finance-manager, cfo                           │
│  SOC2: CC6.1 separation-of-duties enforced                 │
├─────────────────────────────────────────────────────────────┤
│  2026-02-04 10:32:45 | TX-003 | $100 → SanctionedCorp      │
│  Status: ❌ BLOCKED                                         │
│  Reason: OFAC SDN List Match                               │
│  SOC2: CC7.3 risk mitigation | Alert sent                  │
└─────────────────────────────────────────────────────────────┘
```

## Contributing to FINOS

This example is designed to be compatible with FINOS standards. To contribute:

1. Fork this repository
2. Ensure compliance with [FINOS Community Standards](https://community.finos.org/docs/governance/Standards)
3. Submit a PR with your improvements

## License

MIT - Compatible with FINOS contribution requirements.

## References

- [FINOS FDC3 Standard](https://fdc3.finos.org/)
- [FINOS Common Domain Model](https://cdm.finos.org/)
- [SOC2 Trust Service Criteria](https://www.aicpa.org/interestareas/frc/assuranceadvisoryservices/sorhome)
- [Agent OS Documentation](https://imran-siddique.github.io/agent-os-docs/)
