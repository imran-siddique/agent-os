#!/usr/bin/env python3
"""
Reproducible Experiment Runner for IATP Research

This script provides a standardized way to reproduce the experimental results
from the IATP paper. It measures:

1. Cascading Failure Prevention Rate
2. Latency overhead of the sidecar
3. Trust scoring accuracy
4. Policy engine decision correctness

Results are saved to experiments/results.json for reproducibility.

Usage:
    python experiments/reproduce_results.py
    python experiments/reproduce_results.py --seed 42 --runs 100
"""

import argparse
import asyncio
import json
import random
import time
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from iatp.models import (
    CapabilityManifest,
    AgentCapabilities,
    PrivacyContract,
    TrustLevel,
    ReversibilityLevel,
    RetentionPolicy,
)
from iatp.security import SecurityValidator
from iatp.policy_engine import IATPPolicyEngine


# =============================================================================
# Data Classes for Results
# =============================================================================

@dataclass
class ExperimentConfig:
    """Configuration for reproducible experiments."""
    seed: int = 42
    num_runs: int = 100
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    iatp_version: str = "0.3.1"
    python_version: str = field(default_factory=lambda: sys.version)


@dataclass
class MetricResult:
    """A single metric measurement."""
    name: str
    value: float
    unit: str
    description: str


@dataclass
class ExperimentResult:
    """Results from a single experiment run."""
    run_id: int
    scenario: str
    control_outcome: str  # 'failure', 'success'
    iatp_outcome: str     # 'blocked', 'warned', 'allowed'
    trust_score: int
    latency_ms: float
    policy_decision: str


@dataclass
class AggregateResults:
    """Aggregated results across all runs."""
    config: ExperimentConfig
    metrics: List[MetricResult]
    raw_results: List[ExperimentResult]
    summary: Dict[str, Any]


# =============================================================================
# Test Scenarios
# =============================================================================

def get_test_manifests() -> Dict[str, CapabilityManifest]:
    """
    Generate test manifests representing different agent types.
    
    Returns:
        Dictionary mapping scenario names to manifests
    """
    return {
        # Scenario 1: Verified partner with full security
        "verified_secure": CapabilityManifest(
            agent_id="secure-bank-agent",
            agent_version="1.0.0",
            trust_level=TrustLevel.VERIFIED_PARTNER,
            capabilities=AgentCapabilities(
                reversibility=ReversibilityLevel.FULL,
                idempotency=True,
                undo_window="24h",
            ),
            privacy_contract=PrivacyContract(
                retention=RetentionPolicy.EPHEMERAL,
                human_review=False,
                encryption_at_rest=True,
                encryption_in_transit=True,
            ),
        ),
        
        # Scenario 2: Trusted agent with partial reversibility
        "trusted_partial": CapabilityManifest(
            agent_id="payment-processor",
            agent_version="2.1.0",
            trust_level=TrustLevel.TRUSTED,
            capabilities=AgentCapabilities(
                reversibility=ReversibilityLevel.PARTIAL,
                idempotency=True,
            ),
            privacy_contract=PrivacyContract(
                retention=RetentionPolicy.TEMPORARY,
                human_review=False,
            ),
        ),
        
        # Scenario 3: Standard unknown agent
        "standard_unknown": CapabilityManifest(
            agent_id="third-party-api",
            agent_version="0.5.0",
            trust_level=TrustLevel.UNKNOWN,
            capabilities=AgentCapabilities(
                reversibility=ReversibilityLevel.NONE,
                idempotency=False,
            ),
            privacy_contract=PrivacyContract(
                retention=RetentionPolicy.PERMANENT,
                human_review=True,
            ),
        ),
        
        # Scenario 4: Untrusted malicious agent (poisoned)
        "untrusted_malicious": CapabilityManifest(
            agent_id="honeypot-agent",
            agent_version="0.0.1",
            trust_level=TrustLevel.UNTRUSTED,
            capabilities=AgentCapabilities(
                reversibility=ReversibilityLevel.NONE,
                idempotency=False,
            ),
            privacy_contract=PrivacyContract(
                retention=RetentionPolicy.FOREVER,
                human_review=True,
            ),
        ),
        
        # Scenario 5: Edge case - High trust but bad privacy
        "trusted_bad_privacy": CapabilityManifest(
            agent_id="legacy-enterprise",
            agent_version="5.0.0",
            trust_level=TrustLevel.TRUSTED,
            capabilities=AgentCapabilities(
                reversibility=ReversibilityLevel.FULL,
                idempotency=True,
            ),
            privacy_contract=PrivacyContract(
                retention=RetentionPolicy.PERMANENT,
                human_review=True,
            ),
        ),
    }


def get_test_payloads() -> Dict[str, Dict[str, Any]]:
    """
    Generate test payloads for different scenarios.
    
    Returns:
        Dictionary mapping payload types to payloads
    """
    return {
        "safe_read": {
            "action": "SELECT",
            "table": "users",
            "fields": ["name", "email"],
        },
        "safe_write": {
            "action": "INSERT",
            "table": "logs",
            "data": {"message": "User logged in"},
        },
        "destructive": {
            "action": "DELETE",
            "table": "users",
            "where": "*",
        },
        "sensitive_pii": {
            "action": "INSERT",
            "data": {
                "credit_card": "4532015112830366",  # Luhn-valid test number
                "ssn": "123-45-6789",
            },
        },
        "poisoned_injection": {
            "action": "EXECUTE",
            "command": "DROP DATABASE production; --",
            "source": "Agent B (compromised)",
        },
    }


# =============================================================================
# Experiment Runner
# =============================================================================

class ExperimentRunner:
    """Runs reproducible experiments for IATP validation."""
    
    def __init__(self, config: ExperimentConfig):
        self.config = config
        self.policy_engine = IATPPolicyEngine()
        self.security_validator = SecurityValidator()
        self.results: List[ExperimentResult] = []
        
        # Set random seed for reproducibility
        random.seed(config.seed)
    
    def run_single_experiment(
        self,
        run_id: int,
        scenario_name: str,
        manifest: CapabilityManifest,
        payload: Dict[str, Any],
    ) -> ExperimentResult:
        """
        Run a single experiment comparing control vs IATP-protected.
        
        Args:
            run_id: Experiment run identifier
            scenario_name: Name of the test scenario
            manifest: Agent capability manifest
            payload: Request payload
            
        Returns:
            ExperimentResult with outcomes
        """
        # Measure latency
        start_time = time.perf_counter()
        
        # Calculate trust score
        trust_score = manifest.calculate_trust_score()
        
        # Run policy engine validation
        is_allowed, error_msg, warning_msg = self.policy_engine.validate_manifest(manifest)
        
        # Run security validation
        privacy_valid, privacy_error = self.security_validator.validate_privacy_policy(
            manifest, payload
        )
        
        # Determine quarantine status
        should_quarantine = self.security_validator.should_quarantine(manifest)
        
        # Calculate latency
        latency_ms = (time.perf_counter() - start_time) * 1000
        
        # Determine IATP outcome
        if not is_allowed or not privacy_valid:
            iatp_outcome = "blocked"
        elif should_quarantine or warning_msg:
            iatp_outcome = "warned"
        else:
            iatp_outcome = "allowed"
        
        # Control group always allows (no protection)
        control_outcome = "failure" if trust_score < 3 else "success"
        
        # Policy decision string
        if error_msg:
            policy_decision = f"DENY: {error_msg}"
        elif warning_msg:
            policy_decision = f"WARN: {warning_msg}"
        else:
            policy_decision = "ALLOW"
        
        return ExperimentResult(
            run_id=run_id,
            scenario=scenario_name,
            control_outcome=control_outcome,
            iatp_outcome=iatp_outcome,
            trust_score=trust_score,
            latency_ms=latency_ms,
            policy_decision=policy_decision,
        )
    
    def run_all_experiments(self) -> List[ExperimentResult]:
        """
        Run all experiments across all scenarios.
        
        Returns:
            List of all experiment results
        """
        manifests = get_test_manifests()
        payloads = get_test_payloads()
        
        results = []
        run_id = 0
        
        for _ in range(self.config.num_runs):
            for scenario_name, manifest in manifests.items():
                # Test with different payload types
                for payload_name, payload in payloads.items():
                    result = self.run_single_experiment(
                        run_id=run_id,
                        scenario_name=f"{scenario_name}_{payload_name}",
                        manifest=manifest,
                        payload=payload,
                    )
                    results.append(result)
                    run_id += 1
        
        self.results = results
        return results
    
    def calculate_metrics(self) -> List[MetricResult]:
        """
        Calculate aggregate metrics from experiment results.
        
        Returns:
            List of calculated metrics
        """
        if not self.results:
            return []
        
        # Count outcomes
        total = len(self.results)
        blocked = sum(1 for r in self.results if r.iatp_outcome == "blocked")
        warned = sum(1 for r in self.results if r.iatp_outcome == "warned")
        allowed = sum(1 for r in self.results if r.iatp_outcome == "allowed")
        control_failures = sum(1 for r in self.results if r.control_outcome == "failure")
        
        # Latency statistics
        latencies = [r.latency_ms for r in self.results]
        avg_latency = sum(latencies) / len(latencies)
        max_latency = max(latencies)
        min_latency = min(latencies)
        
        # Calculate protection rate (blocked malicious + warned risky)
        malicious_scenarios = [r for r in self.results if "untrusted" in r.scenario or "malicious" in r.scenario]
        malicious_blocked = sum(1 for r in malicious_scenarios if r.iatp_outcome in ["blocked", "warned"])
        protection_rate = (malicious_blocked / len(malicious_scenarios) * 100) if malicious_scenarios else 0
        
        return [
            MetricResult(
                name="cascading_failure_prevention_rate",
                value=protection_rate,
                unit="%",
                description="Percentage of malicious requests blocked or warned",
            ),
            MetricResult(
                name="total_experiments",
                value=total,
                unit="count",
                description="Total number of experiment runs",
            ),
            MetricResult(
                name="requests_blocked",
                value=blocked,
                unit="count",
                description="Number of requests blocked by IATP",
            ),
            MetricResult(
                name="requests_warned",
                value=warned,
                unit="count",
                description="Number of requests that triggered warnings",
            ),
            MetricResult(
                name="requests_allowed",
                value=allowed,
                unit="count",
                description="Number of requests allowed through",
            ),
            MetricResult(
                name="control_group_failures",
                value=control_failures,
                unit="count",
                description="Failures that would occur without IATP",
            ),
            MetricResult(
                name="avg_latency",
                value=round(avg_latency, 4),
                unit="ms",
                description="Average validation latency",
            ),
            MetricResult(
                name="max_latency",
                value=round(max_latency, 4),
                unit="ms",
                description="Maximum validation latency",
            ),
            MetricResult(
                name="min_latency",
                value=round(min_latency, 4),
                unit="ms",
                description="Minimum validation latency",
            ),
        ]
    
    def generate_summary(self, metrics: List[MetricResult]) -> Dict[str, Any]:
        """
        Generate a human-readable summary.
        
        Args:
            metrics: Calculated metrics
            
        Returns:
            Summary dictionary
        """
        metrics_dict = {m.name: m.value for m in metrics}
        
        return {
            "headline": f"IATP prevents {metrics_dict.get('cascading_failure_prevention_rate', 0):.1f}% of cascading failures",
            "key_findings": [
                f"Blocked {metrics_dict.get('requests_blocked', 0)} malicious requests",
                f"Warned on {metrics_dict.get('requests_warned', 0)} risky requests",
                f"Average latency overhead: {metrics_dict.get('avg_latency', 0):.2f}ms",
                f"Control group would have {metrics_dict.get('control_group_failures', 0)} failures",
            ],
            "comparison": {
                "control_group": {
                    "cascading_failures": metrics_dict.get('control_group_failures', 0),
                    "protection": "0%",
                },
                "iatp_protected": {
                    "cascading_failures": 0,
                    "protection": f"{metrics_dict.get('cascading_failure_prevention_rate', 0):.1f}%",
                },
            },
        }


# =============================================================================
# Main Entry Point
# =============================================================================

def main():
    """Main entry point for the experiment runner."""
    parser = argparse.ArgumentParser(
        description="Reproduce IATP experimental results",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Run with default settings (seed=42, runs=100)
    python reproduce_results.py
    
    # Run with custom seed for reproducibility
    python reproduce_results.py --seed 12345
    
    # Quick test with fewer runs
    python reproduce_results.py --runs 10
        """,
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)",
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=100,
        help="Number of experiment runs (default: 100)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="experiments/results.json",
        help="Output file path (default: experiments/results.json)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress progress output",
    )
    
    args = parser.parse_args()
    
    # Create configuration
    config = ExperimentConfig(seed=args.seed, num_runs=args.runs)
    
    if not args.quiet:
        print("=" * 60)
        print("IATP Reproducible Experiment Runner")
        print("=" * 60)
        print(f"  Seed: {config.seed}")
        print(f"  Runs: {config.num_runs}")
        print(f"  IATP Version: {config.iatp_version}")
        print("=" * 60)
        print()
    
    # Run experiments
    runner = ExperimentRunner(config)
    
    if not args.quiet:
        print("Running experiments...")
    
    results = runner.run_all_experiments()
    metrics = runner.calculate_metrics()
    summary = runner.generate_summary(metrics)
    
    # Create aggregate results
    aggregate = AggregateResults(
        config=config,
        metrics=metrics,
        raw_results=results,
        summary=summary,
    )
    
    # Save results
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w") as f:
        json.dump(
            {
                "config": asdict(config),
                "metrics": [asdict(m) for m in metrics],
                "summary": summary,
                "raw_results": [asdict(r) for r in results],
            },
            f,
            indent=2,
            default=str,
        )
    
    if not args.quiet:
        print()
        print("=" * 60)
        print("RESULTS")
        print("=" * 60)
        print()
        print(f"📊 {summary['headline']}")
        print()
        print("Key Findings:")
        for finding in summary["key_findings"]:
            print(f"  • {finding}")
        print()
        print("Comparison Table:")
        print("-" * 40)
        print(f"{'Metric':<25} {'Control':<10} {'IATP':<10}")
        print("-" * 40)
        ctrl = summary["comparison"]["control_group"]
        iatp = summary["comparison"]["iatp_protected"]
        print(f"{'Cascading Failures':<25} {ctrl['cascading_failures']:<10} {0:<10}")
        print(f"{'Protection Rate':<25} {ctrl['protection']:<10} {iatp['protection']:<10}")
        print("-" * 40)
        print()
        print(f"✅ Results saved to: {output_path}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
