# Finance Agent (SOC2 Compliant)

A financial operations agent with built-in SOC2 compliance, role-based access
control, sanctions screening, and comprehensive audit trail — powered by the
real Agent OS governance APIs.

## Features

| Feature | Description | SOC2 Control |
|---------|-------------|--------------|
| **Separation of Duties** | Role-based tool permissions (AP / FM / CFO) | CC6.1 |
| **Approval Workflows** | Transactions > $10K require human approval | CC6.3 |
| **Audit Trail** | Immutable JSON + CSV logging | CC7.1 |
| **Rate Limiting** | Max 10 transfers per session | CC8.1 |
| **Sanctions Screening** | Blocked-pattern matching for OFAC entities | CC7.3 |
| **PII Protection** | SSN and credit-card regex blocking | CC7.3 |

## Quick Start

```bash
# From the repo root
python examples/finance-soc2/main.py
```

No external dependencies beyond `agent-os` itself.

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                   Finance SOC2 Demo                          │
├──────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │ accounts_    │  │ finance_     │  │ cfo              │   │
│  │ payable      │  │ manager      │  │                  │   │
│  │ ≤$5K, no     │  │ ≤$50K, can   │  │ unlimited, can   │   │
│  │ approve      │  │ approve      │  │ approve          │   │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────────┘   │
│         │                 │                  │               │
│         ▼                 ▼                  ▼               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │          SOC2Interceptor (custom interceptor)          │  │
│  │  • Role-based allowed_tools check (CC6.1)             │  │
│  │  • Blocked patterns: sanctions + PII (CC7.3)          │  │
│  │  • Transfer amount limits per role (CC6.3)            │  │
│  │  • Rate limiting (CC8.1)                              │  │
│  │  • Max tool calls enforcement                         │  │
│  └────────────────────────────────────────────────────────┘  │
│         │                                                    │
│         ▼                                                    │
│  ┌────────────────────────────────────────────────────────┐  │
│  │          Agent OS Governance Layer                     │  │
│  │  GovernancePolicy · BaseIntegration · ExecutionContext │  │
│  │  ToolCallRequest · ToolCallResult · Event Emitters     │  │
│  └────────────────────────────────────────────────────────┘  │
│         │                                                    │
│         ▼                                                    │
│  ┌────────────────────────────────────────────────────────┐  │
│  │          Immutable Audit Log (JSON + CSV export)       │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

## Role Configuration

| Role | Allowed Tools | Max Transfer | Can Approve |
|------|--------------|-------------|-------------|
| `accounts_payable` | `transfer`, `query_balance` | $5,000 | No |
| `finance_manager` | `transfer`, `approve`, `query_balance` | $50,000 | Yes |
| `cfo` | `transfer`, `approve`, `query_balance`, `generate_report` | Unlimited | Yes |

## Governance Policy (per role)

Each role gets a `GovernancePolicy` from `agent_os.integrations.base`:

```python
from agent_os.integrations.base import GovernancePolicy, PatternType

policy = GovernancePolicy(
    name="soc2_accounts_payable",
    require_human_approval=True,
    max_tool_calls=20,
    allowed_tools=["transfer", "query_balance"],
    blocked_patterns=[
        (r"\b\d{3}-\d{2}-\d{4}\b", PatternType.REGEX),  # SSN
        (r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b", PatternType.REGEX),  # CC
        "password",
        "secret",
        "SanctionedCorp",
        "BadActor LLC",
        "Blocked Inc",
    ],
    log_all_calls=True,
    checkpoint_frequency=5,
    version="1.0.0",
)
```

## Demo Scenarios

The demo runs six scenarios that exercise every governance control:

| # | Scenario | Role | Expected Result |
|---|----------|------|-----------------|
| 1 | Small transfer ($500) | AP | ✅ Auto-approved |
| 2 | Large transfer ($25K) | FM | ⏳ Pending human approval |
| 3 | Sanctioned entity | AP | ✘ Blocked by pattern match |
| 4 | Rate limit burst | AP | ✘ Blocked after 10 transfers |
| 5 | Balance query | AP | ✔ Allowed |
| 6 | Role escalation (AP → approve) | AP | ✘ Blocked — not in allowed_tools |

## SOC2 Trust Service Criteria Mapping

| SOC2 Criteria | Description | Agent OS Implementation |
|---------------|-------------|------------------------|
| CC6.1 | Logical and Physical Access | Role-based `allowed_tools` per policy |
| CC6.3 | Access Control | `SOC2Interceptor` enforces transfer limits |
| CC7.1 | System Operations | `log_all_calls=True`, immutable audit log |
| CC7.2 | Change Management | Version-controlled `GovernancePolicy` |
| CC7.3 | Risk Mitigation | `blocked_patterns` for sanctions + PII |
| CC8.1 | Incident Response | Rate limiting, event emitters for alerts |

## Audit Trail

The demo exports a complete audit trail in two formats:

- **`soc2_audit_trail.json`** — structured JSON for programmatic analysis
- **`soc2_audit_trail.csv`** — flat CSV for compliance review

Fields: `timestamp`, `agent_id`, `event_type`, `tool`, `role`, `call_count`,
`reason`, `checkpoint`, `amount`, `recipient`, `decision`.

## Sample Output

```
================================================================
  Finance SOC2 Compliance Demo — Agent OS
================================================================
  Roles: accounts_payable, finance_manager, cfo
  Human approval required: YES (transactions > $10,000)
  ...

--- Scenario 1: Small transfer — accounts_payable (auto-approved) ---
  ✔ ALLOWED  | tool=transfer (call 1/20)
  ✅ PROCESSED: $500.00 to Vendor ABC — approved

--- Scenario 3: Sanctioned entity — blocked by governance ---
  ✘ BLOCKED  | tool=transfer
             | reason: Blocked pattern detected: SanctionedCorp

--- Scenario 6: Role escalation — AP tries to approve (blocked) ---
  ✘ BLOCKED  | tool=approve
             | reason: Tool 'approve' not permitted for role 'accounts_payable'
  🔒 Separation of duties enforced (SOC2 CC6.1)
```

## License

MIT

## References

- [SOC2 Trust Service Criteria](https://www.aicpa.org/interestareas/frc/assuranceadvisoryservices/sorhome)
- [Agent OS Documentation](https://imran-siddique.github.io/agent-os-docs/)
