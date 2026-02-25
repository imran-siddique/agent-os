# Financial SOX Compliance Agent

A financial transaction processing agent with Sarbanes-Oxley (SOX) compliance,
human-in-the-loop approval for large transactions, and an immutable audit trail.

## Features

| Feature | Description | SOX Section |
|---------|-------------|-------------|
| **Human Approval** | Transactions over $1,000 require approval | §302 / §404 |
| **Immutable Audit Log** | Append-only JSON audit trail | §802 |
| **Blocked Patterns** | PII and credential redaction | §404 Internal Controls |
| **Rate Limiting** | Max tool calls per session | §404 Internal Controls |
| **Export** | JSON and CSV audit trail export | §802 Record Retention |

## Quick Start

```bash
pip install agent-os-kernel
python demo.py
```

No external dependencies or API keys required — all agent responses are mocked.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 Financial SOX Agent                          │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Transaction │  │  Approval   │  │  Audit Trail        │  │
│  │ Processor   │  │  Workflow   │  │  (append-only)      │  │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────────────┘  │
│         │                │                │                  │
│         ▼                ▼                ▼                  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              Agent OS Governance Layer                 │  │
│  │  • GovernancePolicy (require_human_approval)          │  │
│  │  • PolicyInterceptor (blocked_patterns, allowed_tools)│  │
│  │  • Audit Logger (immutable, append-only)              │  │
│  └───────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ JSON Export │  │ CSV Export  │  │  Console Output     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Governance Policy

The demo uses `GovernancePolicy` from `agent_os.integrations.base`:

```python
sox_policy = GovernancePolicy(
    name="financial_sox",
    require_human_approval=True,       # Transactions >$1000 need approval
    max_tool_calls=15,                 # Rate limiting per session
    allowed_tools=[                    # Only approved financial operations
        "process_transaction",
        "query_balance",
        "generate_report",
        "flag_for_review",
    ],
    blocked_patterns=[                 # Block PII / credentials
        (r"\b\d{3}-\d{2}-\d{4}\b", PatternType.REGEX),  # SSN
        (r"\b\d{16}\b", PatternType.REGEX),              # Credit card
        "password",
        "secret",
    ],
    log_all_calls=True,
    checkpoint_frequency=3,
)
```

## SOX Compliance Mapping

| SOX Section | Requirement | Agent OS Implementation |
|-------------|-------------|------------------------|
| §302 | CEO/CFO certification of controls | `require_human_approval` for large transactions |
| §404 | Internal control assessment | `GovernancePolicy` with `allowed_tools`, `blocked_patterns` |
| §409 | Real-time disclosure | Governance events emitted on every action |
| §802 | Record retention (7 years) | Append-only JSON audit log, CSV/JSON export |
| §906 | Criminal penalties for fraud | Immutable audit trail with tamper-evident logging |

## Audit Trail

All decisions are written to an append-only JSON file (`sox_audit_trail.json`)
and can be exported to CSV for compliance review:

```
sox_audit_trail.json   — machine-readable, append-only
sox_audit_trail.csv    — human-readable, for compliance review
```

## Sample Output

```
================================================================
  Financial SOX Compliance Demo — Agent OS
================================================================

  Policy: financial_sox (v1.0.0)
  Human approval required: YES (transactions > $1,000)
  Max tool calls: 15
  Allowed tools: process_transaction, query_balance, generate_report, flag_for_review
  Blocked patterns: SSN regex, credit-card regex, password, secret
  Audit logging: ON

--- Scenario 1: Small transaction (auto-approved) ---
  ✔ ALLOWED  | tool=process_transaction (call 1/15)
  ✅ PROCESSED: $250.00 to Office Supplies Inc — auto-approved

--- Scenario 2: Large transaction (requires human approval) ---
  ✔ ALLOWED  | tool=process_transaction (call 2/15)
  ⏳ PENDING APPROVAL: $15,000.00 to Acme Consulting LLC
  📧 Approval request sent to: CFO, Controller

--- Scenario 3: Blocked PII (SSN detected) ---
  ✘ BLOCKED  | tool=process_transaction
               | reason: Input matches blocked pattern

--- Scenario 4: Unauthorized tool blocked ---
  ✘ BLOCKED  | tool=delete_ledger_entry
               | reason: Tool not in allowed list

================================================================
  Audit Trail Summary
================================================================
  1. [sox-agent] ALLOWED  tool=process_transaction  (calls=1)
  2. [sox-agent] ALLOWED  tool=process_transaction  (calls=2)
  3. [sox-agent] BLOCKED  tool=process_transaction  reason=blocked_pattern
  4. [sox-agent] BLOCKED  tool=delete_ledger_entry  reason=not_allowed

  Total audit entries: 4
  Exported: sox_audit_trail.json, sox_audit_trail.csv
```

## License

MIT

## References

- [SOX Act Overview (SEC)](https://www.sec.gov/about/laws/soa2002.pdf)
- [PCAOB Auditing Standards](https://pcaobus.org/oversight/standards/auditing-standards)
- [Agent OS Documentation](https://imran-siddique.github.io/agent-os-docs/)
