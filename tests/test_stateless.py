"""
Test Stateless Kernel (MCP June 2026 compliant).
"""

import pytest
from typing import Dict, Any


class TestStatelessKernel:
    """Test StatelessKernel class."""
    
    def test_import_stateless(self):
        """Test importing stateless module."""
        from agent_os.stateless import (
            StatelessKernel,
            ExecutionContext,
            ExecutionRequest,
            ExecutionResult,
            MemoryBackend,
            stateless_execute,
        )
        assert StatelessKernel is not None
        assert ExecutionContext is not None
    
    def test_create_kernel(self):
        """Test creating a stateless kernel."""
        from agent_os.stateless import StatelessKernel
        
        kernel = StatelessKernel()
        assert kernel is not None
        assert kernel.backend is not None
    
    def test_execution_context(self):
        """Test ExecutionContext creation."""
        from agent_os.stateless import ExecutionContext
        
        ctx = ExecutionContext(
            agent_id="test-agent",
            policies=["read_only"],
            history=[]
        )
        
        assert ctx.agent_id == "test-agent"
        assert "read_only" in ctx.policies
        assert ctx.history == []
    
    def test_context_to_dict(self):
        """Test ExecutionContext serialization."""
        from agent_os.stateless import ExecutionContext
        
        ctx = ExecutionContext(
            agent_id="test-agent",
            policies=["strict"],
            metadata={"key": "value"}
        )
        
        d = ctx.to_dict()
        assert d["agent_id"] == "test-agent"
        assert d["policies"] == ["strict"]
        assert d["metadata"]["key"] == "value"
    
    @pytest.mark.asyncio
    async def test_execute_allowed_action(self):
        """Test executing an allowed action."""
        from agent_os.stateless import StatelessKernel, ExecutionContext
        
        kernel = StatelessKernel()
        context = ExecutionContext(agent_id="test", policies=[])
        
        result = await kernel.execute(
            action="database_query",
            params={"query": "SELECT 1"},
            context=context
        )
        
        assert result.success is True
        assert result.error is None
        assert result.signal is None
    
    @pytest.mark.asyncio
    async def test_execute_blocked_by_read_only(self):
        """Test action blocked by read_only policy."""
        from agent_os.stateless import StatelessKernel, ExecutionContext
        
        kernel = StatelessKernel()
        context = ExecutionContext(
            agent_id="test",
            policies=["read_only"]
        )
        
        result = await kernel.execute(
            action="file_write",
            params={"path": "/data/file.txt"},
            context=context
        )
        
        assert result.success is False
        assert result.signal == "SIGKILL"
        assert "read_only" in result.error
    
    @pytest.mark.asyncio
    async def test_execute_blocked_by_no_pii(self):
        """Test action blocked by no_pii policy."""
        from agent_os.stateless import StatelessKernel, ExecutionContext
        
        kernel = StatelessKernel()
        context = ExecutionContext(
            agent_id="test",
            policies=["no_pii"]
        )
        
        result = await kernel.execute(
            action="database_query",
            params={"query": "SELECT ssn FROM users"},
            context=context
        )
        
        assert result.success is False
        assert result.signal == "SIGKILL"
        assert "ssn" in result.error.lower()
    
    @pytest.mark.asyncio
    async def test_execute_updates_context(self):
        """Test that execution updates context."""
        from agent_os.stateless import StatelessKernel, ExecutionContext
        
        kernel = StatelessKernel()
        context = ExecutionContext(
            agent_id="test",
            policies=[],
            history=[]
        )
        
        result = await kernel.execute(
            action="api_call",
            params={"url": "https://example.com"},
            context=context
        )
        
        assert result.success is True
        assert result.updated_context is not None
        assert len(result.updated_context.history) == 1
        assert result.updated_context.history[0]["action"] == "api_call"
    
    @pytest.mark.asyncio
    async def test_stateless_execute_helper(self):
        """Test stateless_execute convenience function."""
        from agent_os.stateless import stateless_execute
        
        result = await stateless_execute(
            action="database_query",
            params={"query": "SELECT 1"},
            agent_id="test-agent",
            policies=[]
        )
        
        assert result.success is True


class TestMemoryBackend:
    """Test in-memory state backend."""
    
    @pytest.mark.asyncio
    async def test_memory_backend_get_set(self):
        """Test get/set operations."""
        from agent_os.stateless import MemoryBackend
        
        backend = MemoryBackend()
        
        await backend.set("key1", {"data": "value"})
        result = await backend.get("key1")
        
        assert result["data"] == "value"
    
    @pytest.mark.asyncio
    async def test_memory_backend_delete(self):
        """Test delete operation."""
        from agent_os.stateless import MemoryBackend
        
        backend = MemoryBackend()
        
        await backend.set("key1", {"data": "value"})
        await backend.delete("key1")
        result = await backend.get("key1")
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_memory_backend_missing_key(self):
        """Test getting non-existent key."""
        from agent_os.stateless import MemoryBackend
        
        backend = MemoryBackend()
        result = await backend.get("nonexistent")
        
        assert result is None


class TestPolicyChecking:
    """Test policy enforcement logic."""
    
    def test_default_policies(self):
        """Test default policies are loaded."""
        from agent_os.stateless import StatelessKernel
        
        kernel = StatelessKernel()
        
        assert "read_only" in kernel.policies
        assert "no_pii" in kernel.policies
        assert "strict" in kernel.policies
    
    def test_custom_policies(self):
        """Test custom policies can be provided."""
        from agent_os.stateless import StatelessKernel
        
        custom = {
            "custom_policy": {
                "blocked_actions": ["dangerous_action"]
            }
        }
        
        kernel = StatelessKernel(policies=custom)
        
        assert "custom_policy" in kernel.policies
        assert "read_only" in kernel.policies  # Still has defaults
    
    @pytest.mark.asyncio
    async def test_multiple_policies(self):
        """Test multiple policies are checked."""
        from agent_os.stateless import StatelessKernel, ExecutionContext
        
        kernel = StatelessKernel()
        context = ExecutionContext(
            agent_id="test",
            policies=["read_only", "no_pii"]
        )
        
        # This should be blocked by read_only
        result = await kernel.execute(
            action="send_email",
            params={"to": "user@example.com"},
            context=context
        )
        
        assert result.success is False
