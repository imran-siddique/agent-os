"""
Test Stateless Kernel (MCP June 2026 compliant).
"""

import json
from unittest.mock import AsyncMock

import pytest


class TestStatelessKernel:
    """Test StatelessKernel class."""

    def test_import_stateless(self):
        """Test importing stateless module."""
        from agent_os.stateless import (
            ExecutionContext,
            StatelessKernel,
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
        from agent_os.stateless import ExecutionContext, StatelessKernel

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
        from agent_os.stateless import ExecutionContext, StatelessKernel

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
        from agent_os.stateless import ExecutionContext, StatelessKernel

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
        from agent_os.stateless import ExecutionContext, StatelessKernel

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


class TestRedisBackend:
    """Test Redis state backend logic."""

    def test_default_prefix(self):
        """Test that the default prefix is set correctly."""
        from agent_os.stateless import RedisBackend

        backend = RedisBackend()
        assert backend._prefix == "agent-os:"

    def test_custom_prefix(self):
        """Test that a custom prefix is set correctly."""
        from agent_os.stateless import RedisBackend

        custom_prefix = "my-custom-app:"
        backend = RedisBackend(key_prefix=custom_prefix)
        assert backend._prefix == custom_prefix

    def test_none_prefix_raises_error(self):
        """Test that None prefix raises TypeError."""
        from agent_os.stateless import RedisBackend

        with pytest.raises(TypeError):
            RedisBackend(key_prefix=None)

    @pytest.mark.asyncio
    async def test_operations_use_prefix(self):
        """Test that get/set/delete operations actually use the prefix."""
        from agent_os.stateless import RedisBackend

        # Setup backend and mock
        prefix = "test-prefix:"
        backend = RedisBackend(key_prefix=prefix)

        mock_client = AsyncMock()

        backend._client = mock_client

        test_key = "user-session-123"
        test_value = {"status": "active"}
        expected_redis_key = f"{prefix}{test_key}"

        await backend.set(test_key, test_value, ttl=60)

        mock_client.set.assert_called_with(
            expected_redis_key,
            json.dumps(test_value),
            ex=60
        )

        mock_client.get.return_value = json.dumps(test_value).encode('utf-8')

        result = await backend.get(test_key)

        mock_client.get.assert_called_with(expected_redis_key)
        assert result == test_value

        await backend.delete(test_key)

        mock_client.delete.assert_called_with(expected_redis_key)


class TestRedisConfig:
    """Test RedisConfig dataclass and its integration with RedisBackend."""

    def test_default_values(self):
        """Test RedisConfig defaults."""
        from agent_os.stateless import RedisConfig

        cfg = RedisConfig()
        assert cfg.host == "localhost"
        assert cfg.port == 6379
        assert cfg.db == 0
        assert cfg.password is None
        assert cfg.pool_size == 10
        assert cfg.connect_timeout == 5.0
        assert cfg.read_timeout == 10.0
        assert cfg.retry_on_timeout is True

    def test_custom_values(self):
        """Test RedisConfig with custom settings."""
        from agent_os.stateless import RedisConfig

        cfg = RedisConfig(
            host="redis.prod",
            port=6380,
            db=2,
            password="secret",
            pool_size=20,
            connect_timeout=2.0,
            read_timeout=3.0,
            retry_on_timeout=False,
        )
        assert cfg.host == "redis.prod"
        assert cfg.port == 6380
        assert cfg.db == 2
        assert cfg.password == "secret"
        assert cfg.pool_size == 20
        assert cfg.connect_timeout == 2.0
        assert cfg.read_timeout == 3.0
        assert cfg.retry_on_timeout is False

    def test_to_url_without_password(self):
        """Test URL generation without password."""
        from agent_os.stateless import RedisConfig

        cfg = RedisConfig(host="myhost", port=6380, db=3)
        assert cfg.to_url() == "redis://myhost:6380/3"

    def test_to_url_with_password(self):
        """Test URL generation with password."""
        from agent_os.stateless import RedisConfig

        cfg = RedisConfig(host="myhost", port=6380, db=1, password="s3cret")
        assert cfg.to_url() == "redis://:s3cret@myhost:6380/1"

    def test_backend_uses_config_url(self):
        """Test that RedisBackend.url is derived from RedisConfig."""
        from agent_os.stateless import RedisBackend, RedisConfig

        cfg = RedisConfig(host="redis.example.com", port=6380, db=5)
        backend = RedisBackend(config=cfg)
        assert backend.url == "redis://redis.example.com:6380/5"

    def test_backend_backward_compat_without_config(self):
        """Test that RedisBackend works without RedisConfig (backward compat)."""
        from agent_os.stateless import RedisBackend

        backend = RedisBackend(url="redis://custom:9999")
        assert backend.url == "redis://custom:9999"
        assert backend._config is None

    @pytest.mark.asyncio
    async def test_get_client_creates_pool_with_config(self):
        """Test that _get_client creates a ConnectionPool when config is provided."""
        from unittest.mock import MagicMock, patch

        from agent_os.stateless import RedisBackend, RedisConfig

        cfg = RedisConfig(
            pool_size=25,
            connect_timeout=3.0,
            read_timeout=7.0,
            retry_on_timeout=False,
        )
        backend = RedisBackend(config=cfg)

        mock_pool = MagicMock()
        mock_redis_cls = MagicMock()

        with patch("redis.asyncio.ConnectionPool") as MockPool, \
             patch("redis.asyncio.Redis") as MockRedis:
            MockPool.from_url.return_value = mock_pool
            MockRedis.return_value = mock_redis_cls

            client = await backend._get_client()

            MockPool.from_url.assert_called_once_with(
                cfg.to_url(),
                max_connections=25,
                socket_connect_timeout=3.0,
                socket_timeout=7.0,
                retry_on_timeout=False,
            )
            MockRedis.assert_called_once_with(connection_pool=mock_pool)
            assert client is mock_redis_cls

    @pytest.mark.asyncio
    async def test_get_client_without_config_uses_from_url(self):
        """Test that _get_client uses from_url when no config is given."""
        from unittest.mock import MagicMock, patch

        from agent_os.stateless import RedisBackend

        backend = RedisBackend(url="redis://localhost:6379")

        mock_client = MagicMock()
        with patch("redis.asyncio.from_url", return_value=mock_client) as mock_from_url:
            client = await backend._get_client()
            mock_from_url.assert_called_once_with("redis://localhost:6379")
            assert client is mock_client


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
        from agent_os.stateless import ExecutionContext, StatelessKernel

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
