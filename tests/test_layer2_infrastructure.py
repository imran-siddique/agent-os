"""
Test Layer 2: Infrastructure packages.
"""

import pytest


# Check if optional packages are installed
try:
    import iatp
    HAS_IATP = True
except ImportError:
    HAS_IATP = False


@pytest.mark.skipif(not HAS_IATP, reason="iatp not installed")
class TestIATP:
    """Test inter-agent-trust-protocol package."""
    
    def test_import_iatp_models(self):
        """Test importing IATP models."""
        from iatp import (
            CapabilityManifest,
            TrustLevel,
            ReversibilityLevel,
            RetentionPolicy,
        )
        assert TrustLevel is not None
        assert ReversibilityLevel is not None
    
    def test_trust_levels(self):
        """Test trust level enum values."""
        from iatp import TrustLevel
        assert hasattr(TrustLevel, 'UNTRUSTED')
        assert hasattr(TrustLevel, 'TRUSTED')
        assert hasattr(TrustLevel, 'VERIFIED_PARTNER')
    
    def test_import_ipc_pipes(self):
        """Test importing IPC pipes (v0.4.0 feature)."""
        from iatp import (
            TypedPipe,
            Pipeline,
            PipeMessage,
            PipeConfig,
            PolicyCheckPipe,
        )
        assert TypedPipe is not None
        assert Pipeline is not None
        assert PipeMessage is not None
    
    def test_create_pipe_message(self):
        """Test creating a pipe message."""
        from iatp import PipeMessage
        
        msg = PipeMessage(
            payload={"query": "test"},
            source_agent="agent-a",
            target_agent="agent-b",
        )
        
        assert msg.payload == {"query": "test"}
        assert msg.source_agent == "agent-a"
        assert msg.policy_checked is False
    
    def test_create_pipeline(self):
        """Test creating a pipeline."""
        from iatp import Pipeline, PolicyCheckPipe
        
        pipeline = Pipeline(name="test-pipeline")
        assert pipeline.name == "test-pipeline"
        assert len(pipeline.stages) == 0


class TestAMB:
    """Test agent-message-bus package."""
    
    def test_import_amb(self):
        """Test basic import."""
        try:
            from amb_core import MessageBus, Message
            assert MessageBus is not None
        except ImportError:
            pytest.skip("amb not installed")


class TestATR:
    """Test agent-tool-registry package."""
    
    def test_import_atr(self):
        """Test basic import."""
        try:
            from atr import ToolRegistry
            assert ToolRegistry is not None
        except ImportError:
            pytest.skip("atr not installed")


# =========================================================================
# IATP trust protocol edge cases (#165)
# =========================================================================


@pytest.mark.skipif(not HAS_IATP, reason="iatp not installed")
class TestIATPTrustProtocol:
    """Test IATP trust establishment, revocation, and score calculation."""

    def test_trust_establishment_between_agents(self):
        """Two agents exchange manifests and calculate trust scores."""
        from iatp import (
            CapabilityManifest, AgentCapabilities, PrivacyContract,
            TrustLevel, ReversibilityLevel, RetentionPolicy,
        )

        agent_a = CapabilityManifest(
            agent_id="agent-a",
            trust_level=TrustLevel.TRUSTED,
            capabilities=AgentCapabilities(
                reversibility=ReversibilityLevel.FULL, idempotency=True,
            ),
            privacy_contract=PrivacyContract(retention=RetentionPolicy.EPHEMERAL),
        )
        agent_b = CapabilityManifest(
            agent_id="agent-b",
            trust_level=TrustLevel.STANDARD,
            capabilities=AgentCapabilities(reversibility=ReversibilityLevel.NONE),
            privacy_contract=PrivacyContract(retention=RetentionPolicy.TEMPORARY),
        )

        score_a = agent_a.calculate_trust_score()
        score_b = agent_b.calculate_trust_score()

        # Agent A should score higher (trusted, full reversibility, ephemeral)
        assert score_a > score_b
        assert 0 <= score_a <= 10
        assert 0 <= score_b <= 10

    def test_trust_revocation_via_reputation(self):
        """Record hallucinations to slash reputation below trust threshold."""
        from iatp import ReputationManager, TrustLevel

        mgr = ReputationManager()
        score = mgr.get_or_create_score("bad-agent")
        assert score.score == 5.0  # initial

        # Slash reputation with critical hallucinations
        mgr.record_hallucination("bad-agent", severity="critical")
        mgr.record_hallucination("bad-agent", severity="critical")
        mgr.record_hallucination("bad-agent", severity="critical")

        updated = mgr.get_score("bad-agent")
        assert updated.score < 2.0
        assert updated.get_trust_level() == TrustLevel.UNTRUSTED

    def test_trust_score_calculation_verified_partner(self):
        """Verified partner with best practices gets maximum score."""
        from iatp import (
            CapabilityManifest, AgentCapabilities, PrivacyContract,
            TrustLevel, ReversibilityLevel, RetentionPolicy,
        )

        manifest = CapabilityManifest(
            agent_id="perfect-agent",
            trust_level=TrustLevel.VERIFIED_PARTNER,
            capabilities=AgentCapabilities(
                reversibility=ReversibilityLevel.FULL, idempotency=True,
            ),
            privacy_contract=PrivacyContract(
                retention=RetentionPolicy.EPHEMERAL, human_review=False,
            ),
        )
        score = manifest.calculate_trust_score()
        assert score == 10  # 5 + 3 + 1 + 1 + 2 - 0 + 1 = clamped to 10

    def test_untrusted_agent_low_score(self):
        """Untrusted agent with poor practices gets very low score."""
        from iatp import (
            CapabilityManifest, AgentCapabilities, PrivacyContract,
            TrustLevel, ReversibilityLevel, RetentionPolicy,
        )

        manifest = CapabilityManifest(
            agent_id="sketchy-agent",
            trust_level=TrustLevel.UNTRUSTED,
            capabilities=AgentCapabilities(
                reversibility=ReversibilityLevel.NONE, idempotency=False,
            ),
            privacy_contract=PrivacyContract(
                retention=RetentionPolicy.PERMANENT, human_review=True,
            ),
        )
        score = manifest.calculate_trust_score()
        # 5 - 5 + 0 + 0 - 2 + 0 = -2 -> clamped to 0
        assert score == 0

    def test_reputation_recovery_with_successes(self):
        """Agent can recover reputation through successful operations."""
        from iatp import ReputationManager

        mgr = ReputationManager()
        mgr.record_hallucination("recovering-agent", severity="high")
        assert mgr.get_score("recovering-agent").score < 5.0

        # Record many successes to recover
        for _ in range(20):
            mgr.record_success("recovering-agent")

        updated = mgr.get_score("recovering-agent")
        assert updated.score > 4.0  # Recovered from the slash

    def test_reputation_score_clamped_0_to_10(self):
        """Reputation score never goes below 0 or above 10."""
        from iatp import ReputationManager

        mgr = ReputationManager()
        # Slash heavily
        for _ in range(10):
            mgr.record_hallucination("floor-agent", severity="critical")
        assert mgr.get_score("floor-agent").score == 0.0

        # Boost heavily
        mgr2 = ReputationManager()
        for _ in range(200):
            mgr2.record_success("ceiling-agent")
        assert mgr2.get_score("ceiling-agent").score <= 10.0
