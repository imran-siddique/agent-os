"""
Finance Agent with SOC2 Compliance
==================================

Demonstrates Agent OS governance for financial operations.
"""

from agent_os import Kernel, Policy, Agent

SOC2_POLICY = """
version: "1.0"
name: finance-soc2-agent
compliance_framework: SOC2

thresholds:
  approval_required: 10000
  high_risk: 50000
  rate_limit: 10  # per minute

roles:
  accounts_payable:
    can_execute: [transfer, query_balance]
    max_single_transaction: 5000
    
  finance_manager:
    can_execute: [transfer, approve, query_balance]
    max_single_transaction: 50000
    can_approve: true
    
  cfo:
    can_execute: [all]
    can_approve: true

rules:
  - name: require-approval-large
    description: Large transactions need human approval
    trigger: action
    condition:
      action_type: transfer
      amount_gt: 10000
    action: require_approval
    approvers: [finance_manager, cfo]
    
  - name: block-sanctioned
    description: Block transactions to sanctioned entities
    trigger: action
    condition:
      action_type: transfer
    check: recipient_not_sanctioned
    action: block
    
  - name: rate-limit
    description: Prevent runaway transactions
    trigger: action
    condition:
      action_type: transfer
    action: rate_limit
    limit: "10/minute"
    
  - name: audit-all
    description: Log everything for SOC2
    trigger: action
    action: log
    include: [user, action, amount, recipient, timestamp, ip_address]
"""

# Mock sanctions list
SANCTIONED_ENTITIES = ["SanctionedCorp", "BadActor LLC", "Blocked Inc"]


class FinanceAgent:
    """SOC2-compliant financial operations agent."""
    
    def __init__(self, role: str):
        self.kernel = Kernel()
        self.policy = Policy.from_yaml(SOC2_POLICY)
        self.kernel.load_policy(self.policy)
        
        self.agent = self.kernel.create_agent(
            name="FinanceBot",
            role=role
        )
        
        self.transaction_count = 0
        
    def transfer(self, amount: float, recipient: str):
        """Execute a money transfer with compliance checks."""
        
        # Check sanctions
        if recipient in SANCTIONED_ENTITIES:
            print(f"❌ BLOCKED: {recipient} is on sanctions list")
            print(f"🚨 Alert sent to compliance team")
            return {"status": "blocked", "reason": "sanctioned_entity"}
        
        # Check rate limit
        self.transaction_count += 1
        if self.transaction_count > 10:
            print(f"❌ RATE LIMITED: Too many transactions")
            return {"status": "blocked", "reason": "rate_limit"}
        
        # Check approval requirement
        if amount > 10000:
            print(f"⏳ PENDING APPROVAL: ${amount:,.2f} to {recipient}")
            print(f"📧 Approval request sent to finance-manager, CFO")
            return {
                "status": "pending_approval",
                "amount": amount,
                "recipient": recipient,
                "approvers": ["finance-manager", "cfo"]
            }
        
        # Execute transaction
        print(f"✅ TRANSFERRED: ${amount:,.2f} to {recipient}")
        print(f"📝 Logged to SOC2 audit trail")
        return {"status": "completed", "amount": amount, "recipient": recipient}
        
    def query_balance(self, account: str):
        """Query account balance."""
        print(f"✅ Balance query for {account} (logged)")
        return {"account": account, "balance": 125000.00}


def main():
    print("=" * 60)
    print("Finance Agent Demo - SOC2 Compliance with Agent OS")
    print("=" * 60)
    
    agent = FinanceAgent(role="accounts_payable")
    
    print("\n1. Small transfer (AUTO-APPROVED)")
    print("-" * 40)
    agent.transfer(500.00, "Vendor ABC")
    
    print("\n2. Large transfer (REQUIRES APPROVAL)")
    print("-" * 40)
    agent.transfer(25000.00, "Vendor XYZ")
    
    print("\n3. Sanctioned entity (BLOCKED)")
    print("-" * 40)
    agent.transfer(100.00, "SanctionedCorp")
    
    print("\n4. Query balance (ALLOWED)")
    print("-" * 40)
    agent.query_balance("operating-account")
    
    print("\n" + "=" * 60)
    print("All actions logged to SOC2 audit trail (7-year retention)")
    print("=" * 60)


if __name__ == "__main__":
    main()
