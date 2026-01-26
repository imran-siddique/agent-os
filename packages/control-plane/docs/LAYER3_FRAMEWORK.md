# Layer 3: The Framework - Architecture Guide

## Overview

**Elevator Pitch**: The governance layer. Defines Agent, Supervisor, Tool, and Policy. This is the chassis that connects the primitives (caas, cmvk) to the protocols (iatp).

**Publication Target**: PyPI (`pip install agent-control-plane`) - Highest Priority

## Dependency Policy

### Allowed Dependencies

The following Layer 2 protocols may be integrated:

| Package | Purpose | Integration Point |
|---------|---------|-------------------|
| `iatp` | Inter-Agent Transport Protocol | `MessageSecurityInterface` |
| `cmvk` | Cryptographic Message Verification Kit | `VerificationInterface` |
| `caas` | Context-as-a-Service | `ContextRoutingInterface` |

### Strictly Forbidden Dependencies

The following packages **MUST NOT** be hard-imported:

| Package | Reason | Correct Pattern |
|---------|--------|-----------------|
| `scak` | Self-Correcting Agent Kernel | Should implement `KernelInterface` |
| `mute-agent` | Capability-based execution | Should use `ValidatorInterface` |

These packages may depend on `agent-control-plane`, but **NOT** vice versa.

## Architecture

### Interfaces for Dependency Injection

Instead of hard imports, the framework defines interfaces that external components must implement:

```python
# External kernel implementations (like SCAK) should implement:
from agent_control_plane import KernelInterface

class SCAKKernel(KernelInterface):
    # Implementation...
```

### Plugin Registry

Components are registered at runtime via the `PluginRegistry`:

```python
from agent_control_plane import AgentControlPlane, PluginRegistry, get_registry

# Get the global registry
registry = get_registry()

# Register a custom kernel
registry.register_kernel(my_custom_kernel)

# Register validators
registry.register_validator(my_validator, action_types=["code_execution"])

# Create control plane with plugin registry enabled
control_plane = AgentControlPlane(use_plugin_registry=True)
```

### Interface Hierarchy

```
KernelInterface
├── SelfCorrectingKernelInterface (for SCAK-like implementations)
└── CapabilityRestrictedKernelInterface (for Mute Agent pattern)

ValidatorInterface
├── CapabilityValidatorInterface (for capability-based validation)
└── (custom validators)

ExecutorInterface
└── (custom executors)

ContextRouterInterface
└── (caas integration)

PolicyProviderInterface
└── (custom policy sources)

SupervisorInterface
└── (custom supervisor agents)
```

### Protocol Interfaces

For integrating with Layer 2 protocols:

```
MessageSecurityInterface    -> iatp integration
VerificationInterface       -> cmvk integration  
ContextRoutingInterface     -> caas integration
```

## Migration Guide

### From Hard-Coded Mute Agent

**Before (deprecated):**
```python
from agent_control_plane.mute_agent import MuteAgentValidator, MuteAgentConfig

validator = MuteAgentValidator(config)
control_plane.enable_mute_agent("agent-id", config)
```

**After (recommended):**
```python
from agent_control_plane import AgentControlPlane, PluginRegistry

# Option 1: Use plugin registry
registry = PluginRegistry()
registry.register_validator(my_validator, action_types=["database_query"])
control_plane = AgentControlPlane(use_plugin_registry=True)

# Option 2: Direct injection
control_plane = AgentControlPlane()
control_plane.register_validator(my_validator)
```

### From Hard-Coded Kernel

**Before (not possible - tightly coupled):**
```python
# scak was hard-imported
```

**After (recommended):**
```python
from agent_control_plane import AgentControlPlane, KernelInterface

# In scak package:
class SCAKKernel(KernelInterface):
    # Implementation...

# In your application:
control_plane = AgentControlPlane()
control_plane.register_kernel(SCAKKernel())
```

## Core Components

### AgentControlPlane

The main interface now supports dependency injection:

```python
control_plane = AgentControlPlane(
    enable_default_policies=True,
    enable_shadow_mode=False,
    enable_constraint_graphs=False,
    use_plugin_registry=True,           # NEW: Use plugin registry
    kernel=custom_kernel,               # NEW: Inject custom kernel
    validators=[validator1, validator2], # NEW: Inject validators
    context_router=caas_router,         # NEW: Inject context router
    message_security=iatp_security,     # NEW: Inject message security
    verifier=cmvk_verifier,             # NEW: Inject verifier
)
```

### PluginRegistry

Singleton registry for managing plugins:

```python
from agent_control_plane import PluginRegistry, get_registry

registry = get_registry()

# Register components
registry.register_kernel(kernel)
registry.register_validator(validator, action_types=["code_execution"])
registry.register_executor(executor, action_types=["file_read"])
registry.register_context_router(router)
registry.register_policy_provider(provider)
registry.register_supervisor(supervisor)

# Protocol integrations
registry.register_message_security(iatp_security)
registry.register_verifier(cmvk_verifier)

# Query registry
registry.list_plugins()
registry.get_statistics()
registry.health_check_all()
```

## Configuration

### RegistryConfiguration

```python
from agent_control_plane import PluginRegistry, RegistryConfiguration

config = RegistryConfiguration(
    lazy_loading=True,
    plugin_paths=["my_plugins"],
    auto_register_builtins=True,
    forbidden_dependencies=["scak", "mute_agent"],
    allowed_protocols=["iatp", "cmvk", "caas"],
)

registry = PluginRegistry(config)
```

## Best Practices

1. **Never hard-import forbidden packages** - Use interfaces instead
2. **Register components early** - Before creating AgentControlPlane
3. **Use `use_plugin_registry=True`** - For full dependency injection
4. **Implement interfaces completely** - All abstract methods must be implemented
5. **Provide metadata** - Help with debugging and management
6. **Use type hints** - For better IDE support and documentation

## Version History

- **v1.1.0**: Added Layer 3 framework with interfaces and plugin registry
  - `KernelInterface` for custom kernel implementations
  - `ValidatorInterface` for custom validators
  - `PluginRegistry` for dependency injection
  - Protocol interfaces for iatp, cmvk, caas
  - Deprecated hard-coded mute_agent imports
