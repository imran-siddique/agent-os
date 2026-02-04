# Healthcare Agent (HIPAA Compliant)

A medical records assistant with built-in HIPAA compliance using Agent OS governance.

## What it demonstrates

- **PHI Protection**: Blocks sharing of Protected Health Information outside approved systems
- **Audit Logging**: Every access to patient data is logged for compliance
- **Role-Based Access**: Different permissions for doctors, nurses, admins
- **Data Minimization**: Agent only accesses minimum necessary information

## Quick Start

```bash
pip install agent-os-kernel
python main.py
```

## Policy Configuration

```yaml
# policy.yaml - HIPAA Compliance Policy
version: "1.0"
name: healthcare-hipaa-agent
compliance_framework: HIPAA

rules:
  # Block PHI in external communications
  - name: block-phi-external
    trigger: action
    condition: 
      action_type: send_message
      destination: external
    check: does_not_contain_phi
    action: block
    alert: compliance-team

  # Require audit log for all patient data access
  - name: audit-patient-access
    trigger: action
    condition:
      action_type: read
      resource_type: patient_record
    action: log
    log_level: audit
    
  # Minimum necessary - only access required fields
  - name: minimum-necessary
    trigger: action
    condition:
      action_type: query
      resource_type: patient_database
    check: fields_are_necessary
    action: filter_response
```

## Example Usage

```python
from agent_os import Kernel
from agent_os.compliance import HIPAAFramework

# Initialize with HIPAA compliance
kernel = Kernel(
    policy_file="policy.yaml",
    compliance=HIPAAFramework()
)

# Create healthcare agent
agent = kernel.create_agent(
    name="MedicalAssistant",
    role="nurse",
    department="cardiology"
)

# This works - accessing patient vitals
result = agent.execute("Get vitals for patient 12345")
# ✅ Logged: Nurse accessed vitals for patient 12345

# This is blocked - trying to email PHI
result = agent.execute("Email patient records to external@gmail.com")
# ❌ Blocked: Cannot send PHI to external destination
# 🚨 Alert sent to compliance team
```

## Compliance Features

| HIPAA Requirement | Agent OS Implementation |
|-------------------|------------------------|
| Access Controls | Role-based permissions |
| Audit Controls | Automatic logging of all PHI access |
| Transmission Security | Blocks external PHI transmission |
| Minimum Necessary | Field-level access filtering |
| Breach Notification | Automatic alerts to compliance team |

## Files

- `main.py` - Healthcare agent implementation
- `policy.yaml` - HIPAA compliance policy
- `roles.yaml` - Role definitions (doctor, nurse, admin)
- `README.md` - This file
