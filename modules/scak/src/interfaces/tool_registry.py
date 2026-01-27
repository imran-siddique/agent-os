"""
Dynamic Tool Registry for extensible agent capabilities.

Implements auto-discovery and registration of tools/functions that agents can use.
Supports multi-modal tools (text, vision, audio) and custom tool plugins.

Research Foundation:
- "Toolformer: Language Models Can Teach Themselves to Use Tools" (arXiv:2302.04761)
- "Multimodal Chain-of-Thought Reasoning in Language Models" (arXiv:2302.00923)
- "ReAct: Synergizing Reasoning and Acting in Language Models" (ICLR 2023)
"""

from typing import Dict, Any, Optional, List, Callable, Awaitable, Union
from pydantic import BaseModel, Field
from enum import Enum
import logging
import inspect
from datetime import datetime

logger = logging.getLogger(__name__)


class ToolType(str, Enum):
    """Types of tools available to agents."""
    TEXT = "text"              # Text processing (search, query, etc.)
    VISION = "vision"          # Image analysis
    AUDIO = "audio"            # Audio processing
    CODE = "code"              # Code execution
    DATABASE = "database"      # Database queries
    API = "api"                # External API calls
    FILESYSTEM = "filesystem"  # File operations
    MULTIMODAL = "multimodal"  # Multiple modalities


class ToolParameter(BaseModel):
    """
    Definition of a tool parameter.
    
    Enables automatic schema generation for LLM function calling.
    """
    name: str
    type: str = Field(..., description="Python type annotation (str, int, etc.)")
    description: str
    required: bool = True
    default: Optional[Any] = None


class ToolDefinition(BaseModel):
    """
    Complete definition of a tool.
    
    Used to generate OpenAI/Anthropic function calling schemas.
    """
    name: str = Field(..., description="Unique tool identifier")
    description: str = Field(..., description="What this tool does")
    tool_type: ToolType
    parameters: List[ToolParameter] = Field(default_factory=list)
    returns: str = Field(..., description="Return type description")
    examples: List[str] = Field(default_factory=list, description="Usage examples")
    requires_approval: bool = Field(
        default=False,
        description="If True, requires human approval before execution"
    )
    multimodal_inputs: List[str] = Field(
        default_factory=list,
        description="Supported input modalities (text, image, audio)"
    )


class ToolRegistry:
    """
    Central registry for agent tools.
    
    Implements:
    1. Auto-discovery of tools via decorators
    2. Schema generation for LLM function calling
    3. Permission and safety checks
    4. Multi-modal tool support
    
    Research: Based on "Toolformer" and "ReAct" patterns for tool use.
    """
    
    def __init__(self):
        """Initialize empty tool registry."""
        self.tools: Dict[str, ToolDefinition] = {}
        self.executors: Dict[str, Callable] = {}
        self._approval_callbacks: Dict[str, Callable] = {}
        
        logger.info("ToolRegistry initialized")
    
    def register_tool(
        self,
        definition: ToolDefinition,
        executor: Callable
    ):
        """
        Register a tool with its execution function.
        
        Args:
            definition: Tool definition with metadata
            executor: Function that executes the tool
                     Can be sync or async
        """
        if definition.name in self.tools:
            logger.warning(f"Tool {definition.name} already registered, overwriting")
        
        self.tools[definition.name] = definition
        self.executors[definition.name] = executor
        
        logger.info(
            f"Tool registered: {definition.name} "
            f"(type: {definition.tool_type.value})"
        )
    
    def register_approval_callback(
        self,
        tool_name: str,
        callback: Callable[[Dict[str, Any]], Awaitable[bool]]
    ):
        """
        Register approval callback for restricted tools.
        
        Args:
            tool_name: Tool requiring approval
            callback: Async function that approves/rejects execution
                     Returns True to approve, False to reject
        """
        self._approval_callbacks[tool_name] = callback
        logger.info(f"Approval callback registered for {tool_name}")
    
    async def execute_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a registered tool with safety checks.
        
        Implements:
        1. Tool existence validation
        2. Approval workflow for restricted tools
        3. Execution with error handling
        4. Telemetry emission
        
        Args:
            tool_name: Tool to execute
            parameters: Tool parameters
            context: Optional execution context
            
        Returns:
            dict with 'success', 'result', and optional 'error'
            
        Raises:
            ValueError: If tool not found
            RuntimeError: If approval rejected
        """
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' not found in registry")
        
        definition = self.tools[tool_name]
        executor = self.executors[tool_name]
        
        # Check if approval required
        if definition.requires_approval:
            approved = await self._request_approval(tool_name, parameters)
            if not approved:
                raise RuntimeError(
                    f"Tool execution rejected: {tool_name}"
                )
        
        # Execute tool
        start_time = datetime.now()
        
        try:
            # Handle both sync and async executors
            if inspect.iscoroutinefunction(executor):
                result = await executor(**parameters)
            else:
                result = executor(**parameters)
            
            # Emit telemetry
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            logger.info(
                f"Tool executed successfully: {tool_name} "
                f"(duration: {duration_ms:.0f}ms)"
            )
            
            return {
                "success": True,
                "result": result,
                "tool_name": tool_name,
                "duration_ms": duration_ms
            }
            
        except Exception as e:
            logger.error(f"Tool execution failed: {tool_name} - {e}")
            
            return {
                "success": False,
                "error": str(e),
                "tool_name": tool_name
            }
    
    async def _request_approval(
        self,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> bool:
        """
        Request approval for tool execution.
        
        Args:
            tool_name: Tool requiring approval
            parameters: Tool parameters
            
        Returns:
            True if approved, False otherwise
        """
        if tool_name in self._approval_callbacks:
            callback = self._approval_callbacks[tool_name]
            return await callback(parameters)
        
        # Default: reject if no callback registered
        logger.warning(
            f"No approval callback for {tool_name}, rejecting by default"
        )
        return False
    
    def get_tool_schema(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        Get OpenAI-compatible function calling schema for a tool.
        
        Converts ToolDefinition to OpenAI's expected format.
        
        Args:
            tool_name: Tool name
            
        Returns:
            OpenAI function schema dict or None if not found
        """
        if tool_name not in self.tools:
            return None
        
        definition = self.tools[tool_name]
        
        # Build parameters schema
        properties = {}
        required = []
        
        for param in definition.parameters:
            properties[param.name] = {
                "type": param.type,
                "description": param.description
            }
            
            if param.required:
                required.append(param.name)
        
        return {
            "name": definition.name,
            "description": definition.description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required
            }
        }
    
    def get_all_schemas(self) -> List[Dict[str, Any]]:
        """
        Get OpenAI-compatible schemas for all registered tools.
        
        Returns:
            List of function schemas
        """
        return [
            self.get_tool_schema(name)
            for name in self.tools.keys()
        ]
    
    def get_tools_by_type(self, tool_type: ToolType) -> List[str]:
        """
        Get all tools of a specific type.
        
        Args:
            tool_type: Tool type to filter by
            
        Returns:
            List of tool names
        """
        return [
            name for name, definition in self.tools.items()
            if definition.tool_type == tool_type
        ]
    
    def get_multimodal_tools(self) -> List[str]:
        """
        Get all tools that support multi-modal inputs.
        
        Returns:
            List of tool names supporting vision/audio
        """
        return [
            name for name, definition in self.tools.items()
            if definition.multimodal_inputs
        ]
    
    def list_tools(self) -> List[str]:
        """
        List all registered tool names.
        
        Returns:
            List of tool names
        """
        return list(self.tools.keys())
    
    def get_tool_info(self, tool_name: str) -> Optional[ToolDefinition]:
        """
        Get detailed information about a tool.
        
        Args:
            tool_name: Tool name
            
        Returns:
            ToolDefinition or None if not found
        """
        return self.tools.get(tool_name)


def tool(
    name: str,
    description: str,
    tool_type: ToolType = ToolType.TEXT,
    requires_approval: bool = False,
    multimodal_inputs: Optional[List[str]] = None
):
    """
    Decorator to register a function as a tool.
    
    Implements auto-discovery pattern for tool registration.
    
    Args:
        name: Tool name
        description: What the tool does
        tool_type: Type of tool
        requires_approval: If True, requires approval before execution
        multimodal_inputs: Supported input modalities
        
    Example:
        >>> @tool("web_search", "Search the web for information")
        >>> async def search_web(query: str, max_results: int = 10) -> List[str]:
        >>>     # Implementation
        >>>     return results
    """
    def decorator(func: Callable) -> Callable:
        # Extract parameter info from function signature
        sig = inspect.signature(func)
        parameters = []
        
        for param_name, param in sig.parameters.items():
            param_type = "string"  # Default
            
            if param.annotation != inspect.Parameter.empty:
                if param.annotation == int:
                    param_type = "integer"
                elif param.annotation == float:
                    param_type = "number"
                elif param.annotation == bool:
                    param_type = "boolean"
                elif param.annotation == list:
                    param_type = "array"
            
            parameters.append(ToolParameter(
                name=param_name,
                type=param_type,
                description=f"Parameter: {param_name}",
                required=param.default == inspect.Parameter.empty
            ))
        
        # Store metadata on function
        func._tool_definition = ToolDefinition(
            name=name,
            description=description,
            tool_type=tool_type,
            parameters=parameters,
            returns="Result from tool execution",
            requires_approval=requires_approval,
            multimodal_inputs=multimodal_inputs or []
        )
        
        return func
    
    return decorator


# Example tools demonstrating registry usage

@tool("web_search", "Search the web for information", tool_type=ToolType.TEXT)
async def web_search(query: str, max_results: int = 10) -> List[Dict[str, str]]:
    """
    Search the web for information.
    
    Args:
        query: Search query
        max_results: Maximum number of results
        
    Returns:
        List of search results with title, url, snippet
    """
    # Mock implementation
    logger.info(f"Searching web: {query}")
    return [
        {
            "title": f"Result {i+1}",
            "url": f"https://example.com/{i}",
            "snippet": f"Information about {query}"
        }
        for i in range(min(3, max_results))
    ]


@tool(
    "analyze_image",
    "Analyze an image using vision model",
    tool_type=ToolType.VISION,
    multimodal_inputs=["image"]
)
async def analyze_image(image_url: str, question: str) -> str:
    """
    Analyze an image and answer questions about it.
    
    Research: "Multimodal Chain-of-Thought Reasoning" for vision-language fusion.
    
    Args:
        image_url: URL or base64 encoded image
        question: Question about the image
        
    Returns:
        Answer based on image analysis
    """
    # Mock implementation - would use GPT-4V or similar
    logger.info(f"Analyzing image: {image_url[:50]}...")
    return f"Image analysis: {question}"


@tool(
    "execute_code",
    "Execute code in a sandboxed environment",
    tool_type=ToolType.CODE,
    requires_approval=True
)
async def execute_code(code: str, language: str = "python") -> Dict[str, Any]:
    """
    Execute code in a sandboxed environment.
    
    REQUIRES APPROVAL for security.
    
    Args:
        code: Code to execute
        language: Programming language
        
    Returns:
        dict with stdout, stderr, exit_code
    """
    # Mock implementation - would use secure sandbox
    logger.info(f"Executing {language} code (approval granted)")
    return {
        "stdout": "Execution result",
        "stderr": "",
        "exit_code": 0
    }


@tool(
    "query_database",
    "Query a database with SQL",
    tool_type=ToolType.DATABASE,
    requires_approval=True
)
async def query_database(
    sql: str,
    database: str = "default"
) -> List[Dict[str, Any]]:
    """
    Execute SQL query on database.
    
    REQUIRES APPROVAL for safety (prevents SQL injection).
    
    Args:
        sql: SQL query
        database: Database name
        
    Returns:
        Query results as list of dicts
    """
    # Mock implementation
    logger.info(f"Querying database: {database}")
    return [{"id": 1, "value": "sample"}]


def create_default_registry() -> ToolRegistry:
    """
    Create a tool registry with default tools.
    
    Returns:
        ToolRegistry with common tools pre-registered
    """
    registry = ToolRegistry()
    
    # Register example tools
    for func in [web_search, analyze_image, execute_code, query_database]:
        if hasattr(func, '_tool_definition'):
            registry.register_tool(func._tool_definition, func)
    
    logger.info(f"Default registry created with {len(registry.tools)} tools")
    
    return registry


# Example usage
async def example_tool_usage():
    """Demonstrate tool registry usage."""
    registry = create_default_registry()
    
    # List all tools
    print(f"Registered tools: {registry.list_tools()}")
    
    # Get tool schemas for LLM function calling
    schemas = registry.get_all_schemas()
    print(f"Function schemas: {len(schemas)}")
    
    # Execute a tool
    result = await registry.execute_tool(
        "web_search",
        {"query": "self-correcting agents", "max_results": 5}
    )
    print(f"Search result: {result}")
    
    # Get multimodal tools
    multimodal = registry.get_multimodal_tools()
    print(f"Multimodal tools: {multimodal}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(example_tool_usage())
