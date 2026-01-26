# MCP Kernel Server

**Expose Agent OS kernel primitives through the Model Context Protocol (MCP)**

MCP is becoming the "USB-C for AI" - a standard interface for AI tools and resources. This server exposes Agent OS capabilities through MCP, enabling any MCP-compatible client to use kernel-level safety.

## Quick Start

```bash
pip install mcp-kernel-server

# Run the server
mcp-kernel-server --port 8080
```

## MCP Tools Exposed

### 1. `cmvk_verify` - Cross-Model Verification
Verify claims across multiple models to detect hallucinations.

```json
{
  "name": "cmvk_verify",
  "arguments": {
    "claim": "Python's GIL prevents true multithreading",
    "models": ["gpt-4", "claude-3", "gemini-pro"]
  }
}
```

Returns:
```json
{
  "verified": true,
  "confidence": 0.95,
  "agreement_score": 0.92,
  "divergences": []
}
```

### 2. `kernel_execute` - Governed Execution
Execute any action through the kernel with policy enforcement.

```json
{
  "name": "kernel_execute",
  "arguments": {
    "action": "database_query",
    "params": {"query": "SELECT * FROM users"},
    "policy": "read_only"
  }
}
```

### 3. `iatp_sign` - Trust Attestation
Sign agent outputs with cryptographic trust.

```json
{
  "name": "iatp_sign",
  "arguments": {
    "content": "Analysis complete: 12 vulnerabilities found",
    "agent_id": "security-scanner-001"
  }
}
```

## MCP Resources Exposed

### `/vfs/{agent_id}/mem/working/*` - Working Memory
Read/write ephemeral working memory for agents.

### `/vfs/{agent_id}/mem/episodic/*` - Episodic Memory
Read/write agent experience logs.

### `/vfs/{agent_id}/policy/*` - Policies (Read-Only)
Read agent policies and constraints.

## Configuration

```yaml
# mcp-kernel.yaml
server:
  port: 8080
  host: 0.0.0.0

kernel:
  policy_mode: strict  # strict | permissive | audit
  max_agents: 100
  
cmvk:
  models:
    - provider: openai
      model: gpt-4-turbo
    - provider: anthropic
      model: claude-3-sonnet
  threshold: 0.85

vfs:
  backend: memory  # memory | redis | s3
  redis_url: redis://localhost:6379
```

## Integration with MCP Clients

### Claude Desktop
```json
{
  "mcpServers": {
    "agent-os": {
      "command": "mcp-kernel-server",
      "args": ["--config", "mcp-kernel.yaml"]
    }
  }
}
```

### Any MCP Client
```python
from mcp import ClientSession

async with ClientSession() as session:
    # Connect to kernel server
    await session.connect("http://localhost:8080")
    
    # Use CMVK verification
    result = await session.call_tool(
        "cmvk_verify",
        {"claim": "The earth is round"}
    )
    
    # Execute with governance
    result = await session.call_tool(
        "kernel_execute",
        {"action": "send_email", "params": {...}}
    )
```

## Stateless Design

This server is **stateless by design** (MCP June 2026 standard):

- No session state maintained
- All context passed in each request
- State externalized to Redis/S3/DynamoDB
- Horizontally scalable (run N instances)

```python
# Every request is self-contained
result = await kernel.execute(
    action="database_query",
    context={
        "agent_id": "analyst-001",
        "policies": ["read_only", "no_pii"],
        "history": [...]  # Passed, not stored
    }
)
```

## License

MIT
