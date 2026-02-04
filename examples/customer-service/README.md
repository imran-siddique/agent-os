# Customer Service Agent (Compliant)

An AI customer service agent with governance for sensitive operations.

## What it demonstrates

- **PII Protection**: Blocks sharing of customer personal data
- **Refund Limits**: Enforces refund authorization levels
- **Escalation Rules**: Auto-escalate sensitive topics
- **Response Filtering**: Ensures professional, compliant responses

## Quick Start

```bash
pip install agent-os-kernel
python main.py
```

## Policy Configuration

```yaml
version: "1.0"
name: customer-service-agent

sensitive_data:
  pii: [ssn, credit_card, bank_account, date_of_birth]
  account: [password, security_questions]

escalation_topics:
  - legal_threat
  - discrimination
  - injury
  - media_mention
  - executive_complaint

rules:
  - name: protect-pii
    trigger: response
    check: does_not_contain_pii
    action: redact
    
  - name: refund-limits
    trigger: action
    condition:
      action_type: refund
      amount_gt: 100
    action: require_approval
    approvers: [supervisor]
    
  - name: auto-escalate
    trigger: message
    condition:
      contains_topic: escalation_topics
    action: escalate
    to: supervisor
    
  - name: professional-tone
    trigger: response
    check: professional_language
    action: rewrite
```

## Example Usage

```python
from agent_os import Kernel

kernel = Kernel(policy_file="policy.yaml")

agent = kernel.create_agent(
    name="SupportBot",
    role="tier1-support"
)

# Normal inquiry - answered
result = agent.handle("What's your return policy?")
# ✅ Response sent

# PII request - redacted
result = agent.handle("What's my credit card number?")
# ✅ Response: "I cannot share payment details. Please check your account."

# Large refund - escalated
result = agent.handle("I want a $500 refund")
# ⏳ Escalated to supervisor for approval

# Legal threat - auto-escalated
result = agent.handle("I'm going to sue you!")
# 🚨 Auto-escalated to supervisor + legal team
```

## Files

- `main.py` - Customer service agent
- `policy.yaml` - Governance policy
- `README.md` - This file
