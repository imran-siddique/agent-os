# Build a HIPAA-Compliant Agent with Agent OS

> Protect PHI, enforce audit logging, and add human-in-the-loop controls — using Agent OS policy enforcement.

## What You'll Build

A healthcare AI agent that:
- ✅ **Blocks PHI leakage** — SSNs, MRNs, phone numbers, emails detected and stopped
- ✅ **Requires human approval** for patient data access
- ✅ **Logs every action** to an immutable, tamper-evident audit trail
- ✅ **Enforces minimum necessary** — no bulk patient data queries
- ✅ **Passes safe queries** — appointment scheduling, general health info
- 🚫 Never exposes the 18 HIPAA identifiers without authorization

### Before vs After

```
┌──────────────────────────────────────────────────────────────────┐
│  BEFORE (no governance)            AFTER (with Agent OS)         │
│                                                                  │
│  User: "Patient SSN is             User: "Patient SSN is         │
│         123-45-6789"                      123-45-6789"           │
│  Agent: ✅ Processes it            Agent: 🚫 BLOCKED             │
│                                    → "PHI violation: SSN         │
│  User: "SELECT * FROM               detected"                   │
│         patient_data"                                            │
│  Agent: ✅ Returns all rows        User: "SELECT * FROM          │
│                                          patient_data"           │
│  User: "Access medical records"    Agent: 🚫 BLOCKED             │
│  Agent: ✅ No approval needed      → "Minimum necessary          │
│                                      violation"                  │
│  No audit trail.                                                 │
│  No PHI protection.               User: "Access medical records" │
│  No compliance.                    Agent: ⏸️  PAUSED              │
│                                    → "Awaiting HIPAA officer     │
│                                      approval"                   │
│                                                                  │
│                                    Immutable audit log ✅         │
│                                    PHI detection ✅               │
│                                    Human-in-the-loop ✅           │
└──────────────────────────────────────────────────────────────────┘
```

---

## What HIPAA Requires for AI Agents

The Health Insurance Portability and Accountability Act (HIPAA) applies to any system — including AI agents — that creates, receives, maintains, or transmits Protected Health Information (PHI). If your agent touches patient data, HIPAA applies.

### The Three HIPAA Rules

| Rule | What It Covers | Agent OS Coverage |
|------|---------------|-------------------|
| **Privacy Rule** | Who can access PHI, minimum necessary standard | ✅ Policy enforcement, RBAC |
| **Security Rule** | Technical safeguards for ePHI | ✅ Encryption, audit controls, access controls |
| **Breach Notification Rule** | Reporting unauthorized PHI access | ✅ Real-time violation detection and alerting |

### The 18 PHI Identifiers

HIPAA defines 18 types of information that qualify as PHI. Agent OS detects and blocks all of them:

| # | Identifier | Agent OS Detection |
|---|-----------|-------------------|
| 1 | Names | ✅ Pattern matching |
| 2 | Dates (except year) | ✅ Date format detection |
| 3 | Phone numbers | ✅ US/international formats |
| 4 | Fax numbers | ✅ Fax-labeled numbers |
| 5 | Email addresses | ✅ Email pattern matching |
| 6 | Social Security numbers | ✅ SSN with/without dashes |
| 7 | Medical record numbers | ✅ MRN pattern detection |
| 8 | Health plan beneficiary numbers | ✅ Insurance ID patterns |
| 9 | Account numbers | ✅ Account number formats |
| 10 | Certificate/license numbers | ✅ License plate patterns |
| 11 | Vehicle identifiers (VINs) | ✅ 17-character VIN detection |
| 12 | Device identifiers | ✅ Serial/device ID patterns |
| 13 | Web URLs | ✅ URL detection |
| 14 | IP addresses | ✅ IPv4 pattern matching |
| 15 | Biometric identifiers | ✅ Biometric keyword detection |
| 16 | Full-face photos | ✅ Photo reference detection |
| 17 | Any other unique identifier | ✅ Configurable patterns |
| 18 | Ages over 89 | ✅ Age pattern detection |

---

## Prerequisites

- Python 3.10+
- Agent OS installed (`pip install agent-os-kernel`)
- 5 minutes of your time
- **No API keys needed** — the demo runs with mock agents

---

## Step 1: Understand the HIPAA Policy Template

Agent OS ships with a pre-built HIPAA policy template at `templates/policies/hipaa.yaml`. It includes:

- **PHI pattern detection** — regex-based blocking for SSNs, MRNs, phone numbers, and more
- **Human approval workflows** — SIGSTOP signals that pause execution for HIPAA officer review
- **Session limits** — max 10 tool calls per session to prevent bulk PHI exposure
- **Minimum necessary enforcement** — blocks `SELECT * FROM patient_data` style queries
- **Mandatory audit logging** — immutable logs with 6-year retention (per HIPAA requirement)

```yaml
# From templates/policies/hipaa.yaml
policies:
  - name: phi_ssn_detection
    description: Block Social Security Numbers in all contexts
    severity: critical
    deny:
      - patterns:
          - '\b\d{3}-\d{2}-\d{4}\b'   # SSN with dashes
          - '\b\d{9}\b'                # SSN without dashes
    action: SIGKILL
    message: "PHI violation: Social Security Number detected"

  - name: phi_data_access_approval
    description: Require human approval for any patient data access
    requires_approval:
      - action: database_read
        scope: patient_data
        approval_level: hipaa_officer
    action: SIGSTOP
    message: "Human approval required for PHI data access"
```

---

## Step 2: Load the HIPAA Policy

```python
from agent_os.integrations import LangChainKernel, GovernancePolicy
from agent_os.templates.policies.loader import load_policy

# Load the built-in HIPAA template
policy = load_policy("hipaa")

# Or load from your own YAML
policy = GovernancePolicy.load("my-hipaa-policy.yaml")
```

---

## Step 3: Wrap Your Agent with HIPAA Governance

```python
# Any agent with an invoke() method works
kernel = LangChainKernel(policy=policy)
governed_agent = kernel.wrap(your_agent)

# Now every call is:
# 1. Checked for PHI patterns
# 2. Checked against minimum necessary rules
# 3. Paused for human approval when accessing patient data
# 4. Logged to an immutable audit trail
```

---

## Step 4: Set Up Audit Logging

HIPAA requires a 6-year audit trail for all PHI access. Agent OS provides this automatically:

```python
from agent_os.integrations.base import GovernanceEventType

# Listen for all governance events
kernel.on(GovernanceEventType.POLICY_CHECK, lambda e: log_to_siem(e))
kernel.on(GovernanceEventType.POLICY_VIOLATION, lambda e: alert_compliance(e))
kernel.on(GovernanceEventType.TOOL_CALL_BLOCKED, lambda e: log_blocked(e))
```

The HIPAA policy template configures audit logging with:

```yaml
audit:
  enabled: true
  mandatory: true
  retention_days: 2190  # 6 years per HIPAA
  immutable: true
  fields:
    - timestamp
    - agent_id
    - action
    - policy
    - result
    - user
    - session_id
    - phi_category
```

---

## Step 5: Implement Human-in-the-Loop

For patient data access, HIPAA requires appropriate authorization. Agent OS uses SIGSTOP signals to pause execution until a HIPAA officer approves:

```python
from agent_os.integrations.base import GovernanceEventType

def on_approval_required(event):
    """Called when agent needs human approval for PHI access."""
    print(f"⏸️  Agent paused — awaiting approval from {event['approval_level']}")
    print(f"   Action: {event['action']}")
    print(f"   Scope: {event['scope']}")
    # In production: send to approval queue, Slack, PagerDuty, etc.

kernel.on(GovernanceEventType.APPROVAL_REQUIRED, on_approval_required)
```

---

## Step 6: Enforce Minimum Necessary

The HIPAA minimum necessary standard requires that access to PHI is limited to the minimum amount needed for the task. Agent OS enforces this:

```yaml
# Blocks overly broad queries
- name: minimum_necessary
  deny:
    - patterns:
        - '(?i)SELECT\s+\*\s+FROM\s+(?:patient|medical|health)'
        - '(?i)(pg_dump|mysqldump).*(?:patient|medical|health)'
  action: SIGKILL
  message: "HIPAA minimum necessary violation"
```

Instead of `SELECT * FROM patients`, agents must use targeted queries:
```sql
-- ✅ Allowed: specific fields for specific patient
SELECT appointment_date, department FROM patients WHERE id = 12345

-- 🚫 Blocked: bulk access to all patient data
SELECT * FROM patient_data
```

---

## Run the Demo

A fully runnable demo is included — **no API keys needed**:

```bash
cd tutorials/hipaa-compliant-agent
python demo.py
```

The demo creates a mock healthcare agent and demonstrates:
1. PHI pattern detection (SSN, MRN, phone, email blocked)
2. Human approval required for medical record access
3. Minimum necessary enforcement (bulk queries blocked)
4. Safe queries passing through (appointments, general health info)
5. Immutable audit trail with tamper detection

---

## BAA (Business Associate Agreement) Considerations

If your AI agent processes PHI on behalf of a covered entity, you need a BAA:

| Scenario | BAA Required? | Notes |
|----------|:------------:|-------|
| Agent accesses EHR data | ✅ | Agent vendor is a Business Associate |
| Agent processes insurance claims | ✅ | Handles PHI (member IDs, diagnoses) |
| Agent provides general health info | ❌ | No PHI involved |
| Agent schedules appointments (no PHI) | ❌ | Only if no patient identifiers used |
| LLM provider processes PHI | ✅ | Must have BAA with LLM vendor |

**Agent OS helps by:**
- Ensuring PHI never reaches the LLM when not needed (pattern blocking)
- Providing audit evidence for BAA compliance reviews
- Enforcing that only approved destinations receive PHI
- Flagging `requires_baa: true` in the HIPAA policy template

> **Important:** Agent OS provides technical safeguards. You still need legal BAA agreements with all vendors in the PHI data flow.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Healthcare Agent                      │
│                                                         │
│  ┌──────────┐    ┌──────────────────┐    ┌───────────┐  │
│  │  User     │───▸│   Agent OS        │───▸│  LLM /    │  │
│  │  Query    │    │   HIPAA Policy    │    │  Tools    │  │
│  └──────────┘    │                    │    └───────────┘  │
│                  │  ┌──────────────┐  │                   │
│                  │  │ PHI Detection │  │                   │
│                  │  │ ✓ 18 identifiers│                   │
│                  │  └──────────────┘  │                   │
│                  │  ┌──────────────┐  │                   │
│                  │  │ Human Approval│  │                   │
│                  │  │ ✓ SIGSTOP     │  │                   │
│                  │  └──────────────┘  │                   │
│                  │  ┌──────────────┐  │                   │
│                  │  │ Audit Logger  │  │                   │
│                  │  │ ✓ Immutable   │  │                   │
│                  │  └──────────────┘  │                   │
│                  │  ┌──────────────┐  │                   │
│                  │  │ Min Necessary │  │                   │
│                  │  │ ✓ Scope limit │  │                   │
│                  │  └──────────────┘  │                   │
│                  └──────────────────┘  │                   │
└─────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────┐
│  Immutable Audit Log │
│  6-year retention    │
│  Hash-chained entries│
└─────────────────────┘
```

---

## Next Steps

- 📋 [HIPAA Compliance Checklist](hipaa-checklist.md) — Full checklist of safeguards
- 🏥 [Healthcare HIPAA Example](../../examples/healthcare-hipaa/) — Production-grade medical chart review agent
- 📖 [Policy Templates](../../templates/policies/) — All pre-built compliance templates
- 🔧 [Full Documentation](https://github.com/imran-siddique/agent-os)
- 🏗️ [Architecture Overview](../../ARCHITECTURE.md)
