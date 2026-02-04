# Finance Agent (SOC2 Compliant)

A financial operations agent with built-in SOC2 compliance and audit trail.

## What it demonstrates

- **Separation of Duties**: No single agent can approve transactions alone
- **Audit Trail**: Every action is logged with full context
- **Rate Limiting**: Prevents runaway transactions
- **Approval Workflows**: Human-in-the-loop for high-value operations

## Quick Start

```bash
pip install agent-os-kernel
python main.py
```

## Policy Configuration

```yaml
# policy.yaml - SOC2 Compliance Policy
version: "1.0"
name: finance-soc2-agent
compliance_framework: SOC2

controls:
  separation_of_duties:
    enabled: true
    require_different_approvers: true
    
  audit_logging:
    enabled: true
    retention_days: 2555  # 7 years for financial records
    include_context: true
    
  rate_limiting:
    transactions_per_minute: 10
    max_single_transaction: 50000

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
```

## Example Usage

```python
from agent_os import Kernel
from agent_os.compliance import SOC2Framework

# Initialize with SOC2 compliance
kernel = Kernel(
    policy_file="policy.yaml",
    compliance=SOC2Framework()
)

# Create finance agent
agent = kernel.create_agent(
    name="FinanceBot",
    role="accounts-payable"
)

# Small transaction - auto-approved
result = agent.execute("Transfer $500 to vendor ABC")
# ✅ Transaction processed, logged to audit trail

# Large transaction - requires human approval
result = agent.execute("Transfer $25,000 to vendor XYZ")
# ⏳ Pending approval from finance-manager or CFO
# 📧 Approval request sent

# Sanctioned entity - blocked
result = agent.execute("Transfer $100 to SanctionedCorp")
# ❌ Blocked: Entity on sanctions list
# 🚨 Alert sent to compliance team
```

## SOC2 Trust Service Criteria Mapping

| SOC2 Criteria | Agent OS Implementation |
|---------------|------------------------|
| CC6.1 Logical Access | Role-based permissions |
| CC6.2 Access Removal | Automatic session expiry |
| CC7.1 System Operations | Audit logging |
| CC7.2 Change Management | Version-controlled policies |
| CC8.1 Incident Response | Automatic alerts |

## Files

- `main.py` - Finance agent implementation
- `policy.yaml` - SOC2 compliance policy
- `README.md` - This file
