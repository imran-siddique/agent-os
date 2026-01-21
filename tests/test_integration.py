"""
Integration tests for the full verification kernel.
"""
import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.core.kernel import VerificationKernel
from tests.test_agents import MockGenerator, MockVerifier


class TestVerificationKernel:
    """Tests for the VerificationKernel."""
    
    def test_kernel_initialization(self):
        """Test kernel initialization."""
        generator = MockGenerator("gpt-4o", "key")
        verifier = MockVerifier("gemini", "key")
        
        kernel = VerificationKernel(generator, verifier)
        
        assert kernel.generator is not None
        assert kernel.verifier is not None
        assert kernel.graph is not None
    
    def test_kernel_execution(self):
        """Test basic kernel execution."""
        generator = MockGenerator("gpt-4o", "key")
        verifier = MockVerifier("gemini", "key")
        kernel = VerificationKernel(generator, verifier)
        
        state = kernel.execute("Test task")
        
        assert state is not None
        assert state.task_description == "Test task"
        assert state.current_loop >= 1
    
    def test_kernel_reset(self):
        """Test kernel reset functionality."""
        generator = MockGenerator("gpt-4o", "key")
        verifier = MockVerifier("gemini", "key")
        kernel = VerificationKernel(generator, verifier)
        
        kernel.execute("Test task")
        stats_before = kernel.get_graph_stats()
        
        kernel.reset()
        stats_after = kernel.get_graph_stats()
        
        assert stats_after["total_nodes"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
