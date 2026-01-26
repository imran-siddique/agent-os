"""ATR - Agent Tool Registry.

A decentralized marketplace for agent capabilities. ATR provides a standardized
interface for tool discovery, registration, and schema generation compatible with
OpenAI Function Calling, Anthropic Tool Use, and other LLM function calling formats.

Example:
    Basic usage with the global registry::

        import atr

        @atr.register(name="calculator", cost="free", tags=["math"])
        def add(a: int, b: int) -> int:
            '''Add two numbers together.

            Args:
                a: First number to add.
                b: Second number to add.

            Returns:
                The sum of a and b.
            '''
            return a + b

        # Discover tools
        tools = atr.list_tools(tag="math")

        # Get OpenAI-compatible schema
        schema = atr.get_tool("calculator").to_openai_function_schema()

Note:
    The registry stores tool specifications but does NOT execute them.
    Execution is the responsibility of the Agent Runtime (Control Plane).

Attributes:
    __version__: Package version string.
    __author__: Package author.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable, List, Optional

from atr.decorator import register as register_decorator
from atr.executor import (
    DockerExecutor,
    Executor,
    ExecutorError,
    ExecutionTimeoutError,
    LocalExecutor,
)
from atr.registry import Registry, RegistryError, ToolAlreadyExistsError, ToolNotFoundError
from atr.schema import (
    CostLevel,
    ParameterSpec,
    ParameterType,
    SideEffect,
    ToolMetadata,
    ToolSpec,
)

if TYPE_CHECKING:
    from typing import Any

__version__ = "0.1.0"
__author__ = "Imran Siddique"

__all__ = [
    # Core classes
    "ToolSpec",
    "ToolMetadata",
    "ParameterSpec",
    "ParameterType",
    # Enums
    "CostLevel",
    "SideEffect",
    # Registry
    "Registry",
    "RegistryError",
    "ToolNotFoundError",
    "ToolAlreadyExistsError",
    # Executors
    "Executor",
    "LocalExecutor",
    "DockerExecutor",
    "ExecutorError",
    "ExecutionTimeoutError",
    # Functions
    "register",
    "get_tool",
    "list_tools",
    "search_tools",
    "get_callable",
    "execute_tool",
    # Module info
    "__version__",
    "__author__",
]

# ---------------------------------------------------------------------------
# Global Registry Instance
# ---------------------------------------------------------------------------

_global_registry: Registry = Registry()


def register(
    name: Optional[str] = None,
    description: Optional[str] = None,
    version: str = "1.0.0",
    author: Optional[str] = None,
    cost: str = "free",
    side_effects: Optional[List[str]] = None,
    tags: Optional[List[str]] = None,
    registry: Optional[Registry] = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Register a function as a tool in the Agent Tool Registry.

    This decorator transforms a Python function into a discoverable tool by:
    1. Extracting the function signature and type hints
    2. Converting to a standardized ToolSpec schema
    3. Registering in the specified registry (defaults to global)

    Args:
        name: Unique tool identifier. Defaults to function name if not provided.
        description: Human-readable description. Defaults to function docstring.
        version: Semantic version string for the tool.
        author: Tool author name.
        cost: Execution cost level. One of "free", "low", "medium", "high".
        side_effects: List of side effects. Options: "none", "read", "write",
            "delete", "network", "filesystem".
        tags: Searchable tags for tool discovery.
        registry: Custom registry instance. Uses global registry if None.

    Returns:
        A decorator that registers the function and returns it unchanged.

    Raises:
        ValueError: If function parameters lack type hints.
        ToolAlreadyExistsError: If tool with same name already exists.

    Example:
        >>> @register(name="web_scraper", cost="low", tags=["web"])
        ... def scrape(url: str, timeout: int = 30) -> str:
        ...     '''Scrape content from a URL.'''
        ...     return requests.get(url, timeout=timeout).text
    """
    target_registry = registry if registry is not None else _global_registry

    return register_decorator(
        name=name,
        description=description,
        version=version,
        author=author,
        cost=cost,
        side_effects=side_effects,
        tags=tags,
        registry=target_registry,
    )


def get_tool(name: str) -> ToolSpec:
    """Retrieve a tool specification from the global registry.

    Args:
        name: The unique tool identifier.

    Returns:
        The complete tool specification including metadata and parameters.

    Raises:
        ToolNotFoundError: If no tool with the given name exists.

    Example:
        >>> spec = get_tool("calculator")
        >>> print(spec.metadata.description)
    """
    return _global_registry.get_tool(name)


def list_tools(
    tag: Optional[str] = None,
    cost: Optional[CostLevel] = None,
    side_effect: Optional[SideEffect] = None,
) -> List[ToolSpec]:
    """List all registered tools with optional filtering.

    Args:
        tag: Filter by tag (e.g., "math", "web", "file").
        cost: Filter by cost level enum.
        side_effect: Filter by side effect type.

    Returns:
        List of tool specifications matching the filters.

    Example:
        >>> # Get all low-cost tools
        >>> cheap_tools = list_tools(cost=CostLevel.LOW)
        >>> # Get all tools tagged "math"
        >>> math_tools = list_tools(tag="math")
    """
    return _global_registry.list_tools(tag=tag, cost=cost, side_effect=side_effect)


def search_tools(query: str) -> List[ToolSpec]:
    """Search tools by name, description, or tags.

    Performs a case-insensitive search across tool metadata.

    Args:
        query: Search query string.

    Returns:
        List of matching tool specifications.

    Example:
        >>> results = search_tools("scrape")
        >>> for tool in results:
        ...     print(tool.metadata.name)
    """
    return _global_registry.search_tools(query)


def get_callable(name: str) -> Callable[..., Any]:
    """Get the callable function for a registered tool.

    This returns the function object but does NOT execute it.
    The caller (Agent Runtime) is responsible for execution.

    Args:
        name: The unique tool identifier.

    Returns:
        The original callable function.

    Raises:
        ToolNotFoundError: If no tool with the given name exists.
        ValueError: If the tool has no associated callable.

    Example:
        >>> func = get_callable("calculator")
        >>> result = func(a=1, b=2)  # Caller executes
    """
    return _global_registry.get_callable(name)


def execute_tool(
    name: str,
    args: Optional[dict] = None,
    executor: Optional[Executor] = None,
    timeout: Optional[int] = None,
) -> Any:
    """Execute a registered tool with optional sandboxing.

    This is a convenience function that retrieves a tool and executes it
    using the specified executor. If no executor is provided, uses LocalExecutor
    (direct execution on host - not sandboxed).

    For production use with untrusted code, always provide a DockerExecutor
    to ensure sandboxed execution.

    Args:
        name: The unique tool identifier.
        args: Dictionary of arguments to pass to the tool.
        executor: Executor instance to use. Defaults to LocalExecutor if None.
        timeout: Execution timeout in seconds (only applicable for DockerExecutor).

    Returns:
        The result of the tool execution.

    Raises:
        ToolNotFoundError: If no tool with the given name exists.
        ValueError: If the tool has no associated callable.
        ExecutorError: If execution fails.
        ExecutionTimeoutError: If execution exceeds timeout.

    Example:
        >>> # Direct execution (not sandboxed - use only with trusted code)
        >>> result = execute_tool("calculator", {"a": 5, "b": 3})
        
        >>> # Sandboxed execution (recommended for untrusted code)
        >>> from atr import DockerExecutor
        >>> docker_exec = DockerExecutor()
        >>> result = execute_tool("calculator", {"a": 5, "b": 3}, executor=docker_exec)
    """
    if args is None:
        args = {}
    
    # Get the callable function
    func = get_callable(name)
    
    # Use LocalExecutor if no executor provided
    if executor is None:
        executor = LocalExecutor()
    
    # Execute with the specified executor
    return executor.execute(func, args=args, timeout=timeout)
