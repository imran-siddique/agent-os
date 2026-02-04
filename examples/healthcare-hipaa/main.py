"""
Healthcare Agent with HIPAA Compliance
======================================

Demonstrates Agent OS governance for medical applications.
"""

from agent_os import Kernel, Policy, Agent

# HIPAA Compliance Policy
HIPAA_POLICY = """
version: "1.0"
name: healthcare-hipaa-agent
compliance_framework: HIPAA

data_classifications:
  phi:
    - patient_name
    - date_of_birth
    - medical_record_number
    - diagnosis
    - treatment
    - medications
    
  non_phi:
    - appointment_time
    - department
    - general_instructions

roles:
  doctor:
    can_access: [phi, non_phi]
    can_modify: [treatment, medications]
    
  nurse:
    can_access: [phi, non_phi]
    can_modify: [vitals, notes]
    
  receptionist:
    can_access: [non_phi]
    can_modify: [appointments]

rules:
  - name: block-external-phi
    description: Never send PHI outside approved systems
    trigger: action
    condition:
      action_type: send
      contains: phi
      destination_not_in: [ehr_system, approved_fax]
    action: block
    message: "Cannot send PHI to unapproved destination"
    alert: compliance@hospital.com

  - name: audit-phi-access
    description: Log all PHI access
    trigger: action  
    condition:
      accesses: phi
    action: log
    log_format: "HIPAA_AUDIT: {user} accessed {resource} at {timestamp}"

  - name: minimum-necessary
    description: Only return fields the role can access
    trigger: response
    action: filter
    filter_by: role_permissions
"""

class HealthcareAgent:
    """HIPAA-compliant medical records assistant."""
    
    def __init__(self, role: str, department: str):
        self.kernel = Kernel()
        self.policy = Policy.from_yaml(HIPAA_POLICY)
        self.kernel.load_policy(self.policy)
        
        self.agent = self.kernel.create_agent(
            name="MedicalAssistant",
            role=role,
            context={"department": department}
        )
        
    def get_patient_info(self, patient_id: str, fields: list = None):
        """Get patient information with HIPAA compliance."""
        action = {
            "type": "read",
            "resource": "patient_record",
            "patient_id": patient_id,
            "fields": fields or ["all"]
        }
        
        result = self.kernel.execute(self.agent, action)
        
        if result.blocked:
            print(f"❌ Access denied: {result.reason}")
            return None
            
        print(f"✅ Access granted (logged for audit)")
        return result.data
        
    def send_patient_data(self, patient_id: str, destination: str):
        """Attempt to send patient data - will be blocked if external."""
        action = {
            "type": "send",
            "resource": "patient_record", 
            "patient_id": patient_id,
            "destination": destination,
            "contains": "phi"
        }
        
        result = self.kernel.execute(self.agent, action)
        
        if result.blocked:
            print(f"❌ BLOCKED: {result.reason}")
            print(f"🚨 Alert sent to compliance team")
            return False
            
        print(f"✅ Data sent to {destination}")
        return True


def main():
    print("=" * 60)
    print("Healthcare Agent Demo - HIPAA Compliance with Agent OS")
    print("=" * 60)
    
    # Create agent as a nurse
    agent = HealthcareAgent(role="nurse", department="cardiology")
    
    print("\n1. Nurse accessing patient vitals (ALLOWED)")
    print("-" * 40)
    agent.get_patient_info("P12345", fields=["vitals", "medications"])
    
    print("\n2. Nurse trying to email PHI externally (BLOCKED)")
    print("-" * 40)
    agent.send_patient_data("P12345", "external@gmail.com")
    
    print("\n3. Nurse sending to approved EHR system (ALLOWED)")
    print("-" * 40)
    agent.send_patient_data("P12345", "ehr_system")
    
    print("\n" + "=" * 60)
    print("All actions logged for HIPAA audit trail")
    print("=" * 60)


if __name__ == "__main__":
    main()
