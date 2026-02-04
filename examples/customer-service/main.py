"""
Customer Service Agent with Governance
======================================

Demonstrates Agent OS for customer service compliance.
"""

from agent_os import Kernel, Policy

# Sensitive patterns to detect
PII_PATTERNS = ["ssn", "social security", "credit card", "bank account", "password"]
ESCALATION_TRIGGERS = ["sue", "lawyer", "legal", "discriminat", "media", "news", "injured"]

SUPPORT_POLICY = """
version: "1.0"
name: customer-service-agent

limits:
  max_refund_auto: 100
  max_discount_percent: 20

roles:
  tier1:
    can_refund: 100
    can_discount: 10
  tier2:
    can_refund: 500
    can_discount: 20
  supervisor:
    can_refund: 5000
    can_discount: 50

rules:
  - name: protect-pii
    description: Never share sensitive customer data
    trigger: response
    check: no_pii
    action: redact

  - name: refund-limits
    description: Enforce refund authorization levels
    trigger: action
    condition:
      action_type: refund
    check: within_role_limit
    action: escalate

  - name: auto-escalate-sensitive
    description: Escalate sensitive topics
    trigger: message
    condition:
      contains: [legal, lawsuit, discriminate, injured]
    action: escalate
    to: supervisor
    notify: legal-team

  - name: professional-response
    description: Ensure professional tone
    trigger: response
    check: professional
    action: rewrite
"""


class CustomerServiceAgent:
    """Governed customer service agent."""
    
    def __init__(self, role: str = "tier1"):
        self.kernel = Kernel()
        self.policy = Policy.from_yaml(SUPPORT_POLICY)
        self.kernel.load_policy(self.policy)
        self.role = role
        
        # Role limits
        self.limits = {
            "tier1": {"refund": 100, "discount": 10},
            "tier2": {"refund": 500, "discount": 20},
            "supervisor": {"refund": 5000, "discount": 50},
        }
        
    def contains_pii_request(self, message: str) -> bool:
        """Check if message requests PII."""
        msg_lower = message.lower()
        return any(pattern in msg_lower for pattern in PII_PATTERNS)
        
    def needs_escalation(self, message: str) -> bool:
        """Check if message should be escalated."""
        msg_lower = message.lower()
        return any(trigger in msg_lower for trigger in ESCALATION_TRIGGERS)
        
    def handle(self, customer_message: str):
        """Handle a customer inquiry with governance."""
        print(f"Customer: {customer_message}")
        
        # Check for escalation triggers
        if self.needs_escalation(customer_message):
            print(f"🚨 AUTO-ESCALATED: Sensitive topic detected")
            print(f"   → Transferred to supervisor")
            print(f"   → Legal team notified")
            return {
                "status": "escalated",
                "reason": "sensitive_topic",
                "response": "I'm transferring you to a supervisor who can better assist."
            }
            
        # Check for PII requests
        if self.contains_pii_request(customer_message):
            print(f"🔒 PII REQUEST: Blocked sensitive data disclosure")
            return {
                "status": "blocked",
                "response": "I cannot share sensitive account details. Please verify through our secure portal."
            }
        
        # Check for refund requests
        if "refund" in customer_message.lower():
            # Extract amount (simplified)
            import re
            amounts = re.findall(r'\$?(\d+)', customer_message)
            if amounts:
                amount = int(amounts[0])
                limit = self.limits[self.role]["refund"]
                
                if amount > limit:
                    print(f"⏳ ESCALATED: ${amount} refund exceeds {self.role} limit (${limit})")
                    return {
                        "status": "pending_approval",
                        "response": f"I'll need supervisor approval for a ${amount} refund. One moment."
                    }
                else:
                    print(f"✅ APPROVED: ${amount} refund within limits")
                    return {
                        "status": "approved",
                        "response": f"I've processed your ${amount} refund. Allow 3-5 business days."
                    }
        
        # Normal response
        print(f"✅ RESPONDED: Normal inquiry handled")
        return {
            "status": "success",
            "response": "Thank you for your inquiry. How can I help you today?"
        }


def main():
    print("=" * 60)
    print("Customer Service Agent Demo - Governance with Agent OS")
    print("=" * 60)
    
    agent = CustomerServiceAgent(role="tier1")
    
    print("\n1. Normal inquiry (ALLOWED)")
    print("-" * 40)
    agent.handle("What's your return policy?")
    
    print("\n2. PII request (BLOCKED)")
    print("-" * 40)
    agent.handle("Can you tell me my credit card number?")
    
    print("\n3. Small refund (APPROVED)")
    print("-" * 40)
    agent.handle("I'd like a $50 refund please")
    
    print("\n4. Large refund (ESCALATED)")
    print("-" * 40)
    agent.handle("I want a $500 refund for my order")
    
    print("\n5. Legal threat (AUTO-ESCALATED)")
    print("-" * 40)
    agent.handle("This is ridiculous, I'm going to sue you!")
    
    print("\n" + "=" * 60)
    print("All interactions logged for compliance review")
    print("=" * 60)


if __name__ == "__main__":
    main()
