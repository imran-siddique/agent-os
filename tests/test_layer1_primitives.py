"""
Test Layer 1: Primitives packages.
"""

import pytest


# Check if optional packages are installed
try:
    import agent_primitives
    HAS_PRIMITIVES = True
except ImportError:
    HAS_PRIMITIVES = False


@pytest.mark.skipif(not HAS_PRIMITIVES, reason="agent_primitives not installed")
class TestAgentPrimitives:
    """Test agent-primitives package."""
    
    def test_import_primitives(self):
        """Test basic import."""
        from agent_primitives import AgentFailure, FailureType, FailureSeverity
        assert FailureType is not None
        assert FailureSeverity is not None
    
    def test_failure_types(self):
        """Test failure type enum values."""
        from agent_primitives import FailureType
        assert hasattr(FailureType, 'TIMEOUT')
        assert hasattr(FailureType, 'INVALID_ACTION')
        assert hasattr(FailureType, 'RESOURCE_EXHAUSTED')
    
    def test_create_agent_failure(self):
        """Test creating an AgentFailure."""
        from agent_primitives import AgentFailure, FailureType, FailureSeverity
        from datetime import datetime, timezone
        
        failure = AgentFailure(
            agent_id="test-agent",
            failure_type=FailureType.TIMEOUT,
            error_message="Test timeout",
            context={"action": "test"},
            timestamp=datetime.now(timezone.utc),
        )
        
        assert failure.agent_id == "test-agent"
        assert failure.failure_type == FailureType.TIMEOUT


class TestCMVK:
    """Test cross-model-verification-kernel package."""
    
    def test_import_cmvk(self):
        """Test basic import."""
        try:
            from cmvk import DriftDetector
            assert DriftDetector is not None
        except ImportError:
            pytest.skip("cmvk not installed with numpy")
    
    def test_drift_detection_stub(self):
        """Test drift detector can be instantiated."""
        try:
            from cmvk import DriftDetector
            detector = DriftDetector()
            assert detector is not None
        except ImportError:
            pytest.skip("cmvk not installed with numpy")


class TestCaaS:
    """Test context-as-a-service package."""
    
    def test_import_caas(self):
        """Test basic import."""
        try:
            from caas_core import ContextPipeline
            assert ContextPipeline is not None
        except ImportError:
            pytest.skip("caas not installed")


class TestEMK:
    """Test episodic-memory-kernel package."""
    
    def test_import_emk(self):
        """Test basic import."""
        try:
            from emk import EpisodicMemory, Episode
            assert EpisodicMemory is not None
            assert Episode is not None
        except ImportError:
            pytest.skip("emk not installed")
