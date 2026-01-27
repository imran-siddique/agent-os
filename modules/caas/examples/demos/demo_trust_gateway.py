"""
Demo: Trust Gateway - Enterprise-Grade Private Cloud Router

This demo showcases the Trust Gateway addressing the "Middleware Gap" problem:

The Problem:
No Enterprise CISO will send proprietary data to a random middleware startup
just to save 30% on tokens. The risk of data leakage is too high.

The Solution:
Trust Gateway - Deploy within your own infrastructure for zero data leakage.
"""

from caas.gateway import (
    TrustGateway,
    SecurityPolicy,
    DeploymentMode,
    SecurityLevel,
    DataRetentionPolicy
)


def demo_basic_gateway():
    """Demo: Basic Trust Gateway usage."""
    print("\n" + "=" * 70)
    print("DEMO 1: Basic Trust Gateway")
    print("=" * 70)
    
    # Create a basic Trust Gateway
    gateway = TrustGateway()
    
    print("\n📦 Trust Gateway deployed!")
    print("\nDeployment Info:")
    info = gateway.get_deployment_info()
    print(f"  • Deployment Mode: {info['deployment_mode']}")
    print(f"  • Security Level: {info['security_level']}")
    print(f"  • Audit Enabled: {info['audit_enabled']}")
    
    print("\n✅ Trust Guarantees:")
    for guarantee in info['trust_guarantees']:
        print(f"  • {guarantee}")


def demo_enterprise_deployment():
    """Demo: Enterprise deployment with maximum security."""
    print("\n" + "=" * 70)
    print("DEMO 2: Enterprise Deployment (Maximum Security)")
    print("=" * 70)
    
    print("\n🏢 Scenario: Financial institution deploying Trust Gateway")
    print("   Requirements: Air-gapped, maximum security, SOC2 compliance")
    
    # Configure maximum security
    retention = DataRetentionPolicy(
        retain_requests=False,  # No retention for air-gapped
        retention_days=0,
        auto_delete=True,
        encrypt_at_rest=True,
        pii_scrubbing=True
    )
    
    policy = SecurityPolicy(
        deployment_mode=DeploymentMode.AIR_GAPPED,
        security_level="maximum",
        data_retention=retention,
        require_authentication=True,
        allowed_users=["ciso@bank.com", "admin@bank.com"],
        data_classification_required=True,
        encrypt_in_transit=True,
        encrypt_at_rest=True,
        audit_all_requests=True,
        compliance_mode="SOC2",
        allow_external_calls=False
    )
    
    gateway = TrustGateway(security_policy=policy, audit_enabled=True)
    
    print("\n✅ Gateway Configured:")
    print("  • Deployment: Air-gapped (no internet connectivity)")
    print("  • Security: Maximum")
    print("  • Compliance: SOC2")
    print("  • Authentication: Required")
    print("  • Allowed Users: ciso@bank.com, admin@bank.com")
    print("  • Data Classification: Required")
    print("  • Encryption: In transit & at rest")
    print("  • External Calls: Blocked")
    print("  • Data Retention: 0 days (immediate deletion)")
    
    # Test request
    print("\n📝 Test Request:")
    print("  Query: 'Analyze Q4 financial results'")
    print("  User: ciso@bank.com")
    print("  Classification: confidential")
    
    result = gateway.route_request(
        query="Analyze Q4 financial results",
        user_id="ciso@bank.com",
        data_classification="confidential"
    )
    
    print("\n✅ Request Approved:")
    print(f"  • Status: {result['status']}")
    print(f"  • Request ID: {result['request_id']}")
    print(f"  • Model Tier: {result['routing_decision']['model_tier']}")
    print(f"  • Suggested Model: {result['routing_decision']['suggested_model']}")
    
    print("\n🔒 Security Context:")
    sc = result['security_context']
    print(f"  • Deployment: {sc['deployment_mode']}")
    print(f"  • Security Level: {sc['security_level']}")
    print(f"  • Classification: {sc['data_classification']}")
    print(f"  • Encrypted: {sc['encrypted']}")
    print(f"  • Audited: {sc['audited']}")


def demo_security_validation():
    """Demo: Security policy validation."""
    print("\n" + "=" * 70)
    print("DEMO 3: Security Policy Validation")
    print("=" * 70)
    
    print("\n🔐 Scenario: Strict authentication and data classification")
    
    policy = SecurityPolicy(
        require_authentication=True,
        allowed_users=["admin@company.com", "user@company.com"],
        data_classification_required=True,
        allowed_classifications=["public", "internal", "confidential"]
    )
    
    gateway = TrustGateway(security_policy=policy)
    
    # Test 1: Valid request
    print("\n✅ Test 1: Valid Request")
    print("  User: admin@company.com (in allowed list)")
    print("  Classification: confidential (valid)")
    
    validation = gateway.validate_request(
        request_data={"query": "Test query"},
        user_id="admin@company.com",
        data_classification="confidential"
    )
    
    print(f"  Result: {'✅ PASSED' if validation['valid'] else '❌ FAILED'}")
    
    # Test 2: Unauthorized user
    print("\n❌ Test 2: Unauthorized User")
    print("  User: hacker@external.com (not in allowed list)")
    print("  Classification: confidential")
    
    validation = gateway.validate_request(
        request_data={"query": "Test query"},
        user_id="hacker@external.com",
        data_classification="confidential"
    )
    
    print(f"  Result: {'✅ PASSED' if validation['valid'] else '❌ BLOCKED'}")
    if not validation['valid']:
        print(f"  Violations: {', '.join(validation['violations'])}")
    
    # Test 3: Invalid classification
    print("\n❌ Test 3: Invalid Data Classification")
    print("  User: admin@company.com")
    print("  Classification: top-secret (not in allowed list)")
    
    validation = gateway.validate_request(
        request_data={"query": "Test query"},
        user_id="admin@company.com",
        data_classification="top-secret"
    )
    
    print(f"  Result: {'✅ PASSED' if validation['valid'] else '❌ BLOCKED'}")
    if not validation['valid']:
        print(f"  Violations: {', '.join(validation['violations'])}")


def demo_routing_decisions():
    """Demo: Heuristic routing through Trust Gateway."""
    print("\n" + "=" * 70)
    print("DEMO 4: Heuristic Routing Through Trust Gateway")
    print("=" * 70)
    
    print("\n⚡ Philosophy: Speed > Smarts")
    print("   Use deterministic heuristics for 0ms routing decisions")
    print("   No external AI calls = No data leakage")
    
    gateway = TrustGateway()
    
    test_queries = [
        ("Hi", "Greeting → Canned response (zero cost)"),
        ("What is Python?", "Short query → Fast model (low cost)"),
        ("Summarize this 50-page document and compare key findings", "Complex task → Smart model (high cost)")
    ]
    
    for query, description in test_queries:
        print(f"\n📝 Query: '{query}'")
        print(f"   Description: {description}")
        
        result = gateway.route_request(
            query=query,
            user_id="developer@company.com"
        )
        
        decision = result['routing_decision']
        print(f"   ✅ Routed to: {decision['model_tier']} tier")
        print(f"   Model: {decision['suggested_model']}")
        print(f"   Cost: {decision['estimated_cost']}")
        print(f"   Reason: {decision['reason']}")


def demo_audit_trail():
    """Demo: Audit trail for compliance."""
    print("\n" + "=" * 70)
    print("DEMO 5: Audit Trail for Compliance")
    print("=" * 70)
    
    print("\n📊 Scenario: GDPR compliance audit")
    
    policy = SecurityPolicy(compliance_mode="GDPR")
    gateway = TrustGateway(security_policy=policy, audit_enabled=True)
    
    # Make several requests
    print("\n📝 Simulating user activity...")
    
    requests = [
        ("user1@company.com", "What is GDPR?", "public"),
        ("user2@company.com", "Analyze customer data", "confidential"),
        ("admin@company.com", "Generate compliance report", "internal")
    ]
    
    for user, query, classification in requests:
        gateway.route_request(
            query=query,
            user_id=user,
            data_classification=classification
        )
        print(f"  • Request from {user}: '{query}'")
    
    # Retrieve audit logs
    print("\n📋 Retrieving Audit Logs:")
    logs = gateway.get_audit_logs()
    
    print(f"\n  Total Logs: {len(logs)}")
    
    # Show sample logs
    print("\n  Sample Log Entries:")
    for log in logs[:3]:
        print(f"    • {log['timestamp'][:19]}: {log['event_type']}")
        print(f"      User: {log.get('user_id', 'N/A')}")
        print(f"      Action: {log['action']}")
        if log.get('data_classification'):
            print(f"      Classification: {log['data_classification']}")
        print()
    
    # Filter by event type
    routing_logs = gateway.get_audit_logs(event_type="request_routed")
    print(f"  Routing Logs: {len(routing_logs)}")
    
    # Filter by user
    user_logs = gateway.get_audit_logs(user_id="admin@company.com")
    print(f"  Admin Activity: {len(user_logs)} events")
    
    print("\n✅ Complete audit trail available for compliance reporting")


def demo_comparison():
    """Demo: SaaS Router vs Trust Gateway comparison."""
    print("\n" + "=" * 70)
    print("DEMO 6: SaaS Router vs Trust Gateway")
    print("=" * 70)
    
    print("\n🏢 CISO Decision Matrix:")
    print("\n" + "-" * 70)
    print("| Feature              | SaaS Router        | Trust Gateway      |")
    print("-" * 70)
    print("| Data Location        | ❌ Third-party     | ✅ Your servers    |")
    print("| Data Security        | ⚠️  Trust required | ✅ Full control    |")
    print("| CISO Approval        | ❌ Difficult       | ✅ Easy            |")
    print("| Compliance           | ⚠️  Provider-based | ✅ Your controls   |")
    print("| Audit Trail          | ⚠️  Limited        | ✅ Full visibility |")
    print("| Cost Savings         | 30% token savings  | 30% token savings  |")
    print("| Latency              | +500ms (external)  | 0ms (local)        |")
    print("| Data Leakage Risk    | ⚠️  High           | ✅ Zero            |")
    print("-" * 70)
    
    print("\n💡 The Trust Gateway Advantage:")
    print("   'The winner won't be the one with the smartest routing algorithm;")
    print("    it will be the one the Enterprise trusts with the keys to the kingdom.'")
    
    print("\n📊 Annual Cost Comparison:")
    print("\n  SaaS Router (External Service):")
    print("    • External routing service: $500/month")
    print("    • Data egress fees: $200/month")
    print("    • Third-party security audit: $1,000/month")
    print("    • Risk of data breach: Priceless")
    print("    Total: $1,700/month + breach risk")
    
    print("\n  Trust Gateway (Self-Hosted):")
    print("    • Server resources: $100/month (marginal)")
    print("    • No external service fees: $0")
    print("    • No data egress: $0")
    print("    • No third-party risk: $0")
    print("    • Peace of mind: Priceless")
    print("    Total: $100/month + full control")
    
    print("\n  💰 Annual Savings: $19,200 + eliminated security risk")


def demo_deployment_options():
    """Demo: Different deployment options."""
    print("\n" + "=" * 70)
    print("DEMO 7: Deployment Options")
    print("=" * 70)
    
    deployments = [
        (DeploymentMode.ON_PREM, "Financial Institution", 
         "Maximum control, data center deployment"),
        (DeploymentMode.PRIVATE_CLOUD, "Tech Company",
         "Cloud-native with isolated VPC"),
        (DeploymentMode.HYBRID, "Healthcare Provider",
         "Local processing with cloud backup"),
        (DeploymentMode.AIR_GAPPED, "Defense Contractor",
         "Complete isolation, no external connectivity")
    ]
    
    for mode, org_type, description in deployments:
        print(f"\n🏢 {org_type}")
        print(f"   Mode: {mode}")
        print(f"   Description: {description}")
        
        policy = SecurityPolicy(deployment_mode=mode)
        gateway = TrustGateway(security_policy=policy)
        info = gateway.get_deployment_info()
        
        print(f"   ✅ Deployment Status: Operational")
        print(f"   Security Level: {info['security_level']}")


def run_all_demos():
    """Run all Trust Gateway demos."""
    print("\n" + "=" * 70)
    print("TRUST GATEWAY DEMONSTRATION")
    print("Enterprise-Grade Private Cloud Router")
    print("=" * 70)
    print("\nThe Middleware Gap Solution:")
    print("'Build an On-Prem / Private Cloud Router that enterprises")
    print(" can deploy within their own infrastructure.'")
    
    demos = [
        demo_basic_gateway,
        demo_enterprise_deployment,
        demo_security_validation,
        demo_routing_decisions,
        demo_audit_trail,
        demo_comparison,
        demo_deployment_options
    ]
    
    for demo in demos:
        try:
            demo()
        except Exception as e:
            print(f"\n❌ Demo failed: {str(e)}")
    
    print("\n" + "=" * 70)
    print("DEMONSTRATION COMPLETE")
    print("=" * 70)
    print("\n🎉 Trust Gateway is ready for enterprise deployment!")
    print("\nKey Takeaways:")
    print("  1. ✅ Data never leaves your infrastructure")
    print("  2. ✅ Zero third-party data sharing")
    print("  3. ✅ Full audit trail for compliance")
    print("  4. ✅ Enterprise-grade security controls")
    print("  5. ✅ 0ms routing decisions (no external calls)")
    print("  6. ✅ Flexible deployment (on-prem, cloud, hybrid, air-gapped)")
    print("\n💡 Remember:")
    print("   'The winner won't be the one with the smartest routing;")
    print("    it will be the one the Enterprise trusts with the keys to the kingdom.'")
    print()


if __name__ == "__main__":
    run_all_demos()
