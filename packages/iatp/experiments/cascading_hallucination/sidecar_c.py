#!/usr/bin/env python3
"""
IATP Sidecar for Agent C (Database)

This sidecar protects Agent C with trust_level="standard" and reversibility="none".
It should block high-risk DELETE operations from low-trust sources.
"""

import sys
import os

# Add parent directories to path to import iatp
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from iatp.models import (
    CapabilityManifest,
    TrustLevel,
    AgentCapabilities,
    ReversibilityLevel,
    PrivacyContract,
    RetentionPolicy
)
from iatp.sidecar import create_sidecar


def main():
    # Create a manifest for Agent B (Summarizer) - LOW TRUST
    # This simulates Agent B being untrusted/compromised
    manifest = CapabilityManifest(
        agent_id="agent-b-summarizer",
        trust_level=TrustLevel.UNTRUSTED,  # Low trust
        capabilities=AgentCapabilities(
            reversibility=ReversibilityLevel.NONE,  # Cannot undo
            idempotency=False,
            sla_latency="5000ms",
            rate_limit=1
        ),
        privacy_contract=PrivacyContract(
            retention=RetentionPolicy.PERMANENT,  # Stores data
            human_review=True  # Requires human review
        )
    )
    
    print("[Sidecar C] Starting IATP Sidecar for Agent C (Database)")
    print(f"[Sidecar C] Trust Level: {manifest.trust_level}")
    print(f"[Sidecar C] Reversibility: {manifest.capabilities.reversibility}")
    
    # Create sidecar pointing to Agent C
    sidecar = create_sidecar(
        agent_url="http://localhost:8011",
        manifest=manifest,
        port=8012
    )
    
    print("[Sidecar C] Sidecar running on port 8012, protecting Agent C on port 8011")
    print("[Sidecar C] This sidecar should WARN about low-trust operations")
    sidecar.run()


if __name__ == "__main__":
    main()
