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
