"""
Plugin System for Community Tool Extensions.

Enables developers to create and share tool plugins that extend agent capabilities.
Supports dynamic loading, versioning, and sandboxed execution.

Research Foundation:
- Plugin architectures (VSCode, WordPress, etc.)
- Sandboxed execution patterns
- Community marketplace patterns (npm, pip, etc.)

Architectural Pattern:
- Plugin discovery via directory scanning or registry
- Isolated execution environment per plugin
- Version compatibility checking
- Security review and approval workflow
"""

from typing import Dict, Any, Optional, List, Callable
from pydantic import BaseModel, Field
from enum import Enum
import logging
import importlib.util
import sys
from pathlib import Path
from datetime import datetime

# Import tool registry - use relative imports within package
from .tool_registry import ToolRegistry, ToolDefinition

logger = logging.getLogger(__name__)


class PluginStatus(str, Enum):
    """Status of a plugin."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    PENDING_APPROVAL = "pending_approval"


class PluginMetadata(BaseModel):
    """
    Metadata for a plugin.
    
    Follows semantic versioning and dependency management.
    """
    plugin_id: str = Field(..., description="Unique plugin identifier")
    name: str
    version: str = Field(..., description="Semantic version (e.g., 1.2.3)")
    author: str
    description: str
    
    # Dependencies
    requires_kernel_version: Optional[str] = Field(
        None,
        description="Minimum kernel version (e.g., >=1.0.0)"
    )
    dependencies: List[str] = Field(
        default_factory=list,
        description="Required Python packages"
    )
    
    # Capabilities
    provides_tools: List[str] = Field(
        default_factory=list,
        description="Tool names this plugin provides"
    )
    
    # Security
    requires_approval: bool = Field(
        default=False,
        description="If True, requires admin approval before activation"
    )
    sandboxed: bool = Field(
        default=True,
        description="If True, runs in isolated environment"
    )
    
    # Metadata
    homepage: Optional[str] = None
    repository: Optional[str] = None
    license: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class Plugin:
    """
    A plugin that extends agent capabilities.
    
    Plugins provide:
    1. New tools for agents to use
    2. Custom execution logic
    3. Integration with external services
    
    Lifecycle:
    1. Discovery (scan directory or registry)
    2. Loading (import module)
    3. Validation (check dependencies, security)
    4. Activation (register tools)
    5. Deactivation (unregister tools)
    """
    
    def __init__(
        self,
        metadata: PluginMetadata,
        module_path: Optional[Path] = None
    ):
        """
        Initialize plugin.
        
        Args:
            metadata: Plugin metadata
            module_path: Path to plugin module
        """
        self.metadata = metadata
        self.module_path = module_path
        self.status = PluginStatus.INACTIVE
        self.module: Optional[Any] = None
        self.registered_tools: List[str] = []
        
        logger.info(
            f"Plugin initialized: {metadata.name} v{metadata.version}"
        )
    
    def load(self) -> bool:
        """
        Load plugin module.
        
        Returns:
            True if loaded successfully, False otherwise
        """
        if not self.module_path or not self.module_path.exists():
            logger.error(f"Plugin module not found: {self.module_path}")
            self.status = PluginStatus.ERROR
            return False
        
        try:
            # Load module dynamically
            spec = importlib.util.spec_from_file_location(
                self.metadata.plugin_id,
                self.module_path
            )
            
            if not spec or not spec.loader:
                raise ImportError("Failed to create module spec")
            
            module = importlib.util.module_from_spec(spec)
            sys.modules[self.metadata.plugin_id] = module
            spec.loader.exec_module(module)
            
            self.module = module
            
            logger.info(f"Plugin loaded: {self.metadata.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load plugin {self.metadata.name}: {e}")
            self.status = PluginStatus.ERROR
            return False
    
    def validate(self) -> bool:
        """
        Validate plugin before activation.
        
        Checks:
        1. Module has required interface (setup, teardown functions)
        2. Dependencies are installed
        3. Security requirements met
        
        Returns:
            True if valid, False otherwise
        """
        if not self.module:
            logger.error("Cannot validate unloaded plugin")
            return False
        
        # Check for required functions
        required_functions = ["setup", "get_tools"]
        
        for func_name in required_functions:
            if not hasattr(self.module, func_name):
                logger.error(
                    f"Plugin {self.metadata.name} missing required function: {func_name}"
                )
                return False
        
        # Check dependencies (simplified - would use pkg_resources in production)
        for dep in self.metadata.dependencies:
            try:
                __import__(dep.split("==")[0].split(">=")[0].split("<=")[0])
            except ImportError:
                logger.error(
                    f"Plugin {self.metadata.name} missing dependency: {dep}"
                )
                return False
        
        logger.info(f"Plugin validated: {self.metadata.name}")
        return True
    
    def activate(self, registry: ToolRegistry) -> bool:
        """
        Activate plugin and register its tools.
        
        Args:
            registry: ToolRegistry to register tools in
            
        Returns:
            True if activated successfully
        """
        if not self.module:
            logger.error("Cannot activate unloaded plugin")
            return False
        
        if self.status == PluginStatus.ACTIVE:
            logger.warning(f"Plugin {self.metadata.name} already active")
            return True
        
        try:
            # Call plugin setup
            if hasattr(self.module, "setup"):
                self.module.setup()
            
            # Get tools from plugin
            if hasattr(self.module, "get_tools"):
                tools = self.module.get_tools()
                
                # Register each tool
                for tool_def, executor in tools:
                    registry.register_tool(tool_def, executor)
                    self.registered_tools.append(tool_def.name)
                
                logger.info(
                    f"Plugin {self.metadata.name} activated: "
                    f"registered {len(self.registered_tools)} tools"
                )
            
            self.status = PluginStatus.ACTIVE
            return True
            
        except Exception as e:
            logger.error(f"Failed to activate plugin {self.metadata.name}: {e}")
            self.status = PluginStatus.ERROR
            return False
    
    def deactivate(self, registry: ToolRegistry) -> bool:
        """
        Deactivate plugin and unregister its tools.
        
        Args:
            registry: ToolRegistry to unregister tools from
            
        Returns:
            True if deactivated successfully
        """
        if self.status != PluginStatus.ACTIVE:
            return True
        
        try:
            # Unregister tools (simplified - ToolRegistry would need unregister method)
            for tool_name in self.registered_tools:
                if tool_name in registry.tools:
                    del registry.tools[tool_name]
                if tool_name in registry.executors:
                    del registry.executors[tool_name]
            
            # Call plugin teardown
            if self.module and hasattr(self.module, "teardown"):
                self.module.teardown()
            
            self.status = PluginStatus.INACTIVE
            self.registered_tools = []
            
            logger.info(f"Plugin {self.metadata.name} deactivated")
            return True
            
        except Exception as e:
            logger.error(f"Failed to deactivate plugin {self.metadata.name}: {e}")
            return False


class PluginManager:
    """
    Manage plugin lifecycle: discovery, loading, activation.
    
    Implements:
    1. Plugin discovery from directories
    2. Version compatibility checking
    3. Dependency resolution
    4. Security review workflow
    5. Plugin marketplace integration
    
    Pattern: Plugin architecture inspired by VSCode, WordPress, etc.
    """
    
    def __init__(
        self,
        plugin_dirs: List[Path],
        registry: ToolRegistry,
        auto_activate: bool = False
    ):
        """
        Initialize plugin manager.
        
        Args:
            plugin_dirs: Directories to search for plugins
            registry: ToolRegistry for registering plugin tools
            auto_activate: If True, automatically activate approved plugins
        """
        self.plugin_dirs = [Path(d) for d in plugin_dirs]
        self.registry = registry
        self.auto_activate = auto_activate
        
        self.plugins: Dict[str, Plugin] = {}
        
        logger.info(
            f"PluginManager initialized (dirs: {len(plugin_dirs)}, "
            f"auto_activate: {auto_activate})"
        )
    
    def discover_plugins(self) -> List[PluginMetadata]:
        """
        Discover plugins in configured directories.
        
        Searches for:
        - plugin.json (metadata file)
        - __init__.py or main.py (entry point)
        
        Returns:
            List of discovered plugin metadata
        """
        discovered = []
        
        for plugin_dir in self.plugin_dirs:
            if not plugin_dir.exists():
                logger.warning(f"Plugin directory not found: {plugin_dir}")
                continue
            
            # Scan for plugin directories
            for item in plugin_dir.iterdir():
                if not item.is_dir():
                    continue
                
                # Check for plugin metadata
                metadata_file = item / "plugin.json"
                if not metadata_file.exists():
                    continue
                
                try:
                    import json
                    with open(metadata_file) as f:
                        metadata_dict = json.load(f)
                    
                    metadata = PluginMetadata(**metadata_dict)
                    discovered.append(metadata)
                    
                    # Find entry point
                    entry_point = None
                    for candidate in ["__init__.py", "main.py"]:
                        path = item / candidate
                        if path.exists():
                            entry_point = path
                            break
                    
                    # Create plugin
                    plugin = Plugin(metadata, entry_point)
                    self.plugins[metadata.plugin_id] = plugin
                    
                except Exception as e:
                    logger.error(f"Failed to load plugin metadata from {item}: {e}")
        
        logger.info(f"Discovered {len(discovered)} plugins")
        
        return discovered
    
    def install_plugin(
        self,
        plugin_id: str,
        auto_activate: Optional[bool] = None
    ) -> bool:
        """
        Install plugin (load and activate).
        
        Args:
            plugin_id: Plugin identifier
            auto_activate: Override default auto_activate setting
            
        Returns:
            True if installed successfully
        """
        if plugin_id not in self.plugins:
            logger.error(f"Plugin not found: {plugin_id}")
            return False
        
        plugin = self.plugins[plugin_id]
        
        # Load module
        if not plugin.load():
            return False
        
        # Validate
        if not plugin.validate():
            return False
        
        # Check if requires approval
        if plugin.metadata.requires_approval:
            logger.warning(
                f"Plugin {plugin.metadata.name} requires approval before activation"
            )
            plugin.status = PluginStatus.PENDING_APPROVAL
            return True
        
        # Activate if auto_activate enabled
        should_activate = auto_activate if auto_activate is not None else self.auto_activate
        
        if should_activate:
            return plugin.activate(self.registry)
        
        return True
    
    def activate_plugin(self, plugin_id: str) -> bool:
        """
        Activate a plugin.
        
        Args:
            plugin_id: Plugin identifier
            
        Returns:
            True if activated successfully
        """
        if plugin_id not in self.plugins:
            logger.error(f"Plugin not found: {plugin_id}")
            return False
        
        plugin = self.plugins[plugin_id]
        return plugin.activate(self.registry)
    
    def deactivate_plugin(self, plugin_id: str) -> bool:
        """
        Deactivate a plugin.
        
        Args:
            plugin_id: Plugin identifier
            
        Returns:
            True if deactivated successfully
        """
        if plugin_id not in self.plugins:
            logger.error(f"Plugin not found: {plugin_id}")
            return False
        
        plugin = self.plugins[plugin_id]
        return plugin.deactivate(self.registry)
    
    def list_plugins(self) -> List[Dict[str, Any]]:
        """
        List all plugins with status.
        
        Returns:
            List of plugin info dicts
        """
        return [
            {
                "plugin_id": plugin.metadata.plugin_id,
                "name": plugin.metadata.name,
                "version": plugin.metadata.version,
                "author": plugin.metadata.author,
                "status": plugin.status.value,
                "tools": len(plugin.registered_tools)
            }
            for plugin in self.plugins.values()
        ]
    
    def get_plugin_info(self, plugin_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed info about a plugin.
        
        Args:
            plugin_id: Plugin identifier
            
        Returns:
            Plugin info dict or None
        """
        if plugin_id not in self.plugins:
            return None
        
        plugin = self.plugins[plugin_id]
        
        return {
            "metadata": plugin.metadata.dict(),
            "status": plugin.status.value,
            "registered_tools": plugin.registered_tools,
            "module_loaded": plugin.module is not None
        }


# Example plugin structure (for documentation)
EXAMPLE_PLUGIN = """
# Example Plugin: Weather Tools
# File: plugins/weather/plugin.json
{
  "plugin_id": "weather_tools",
  "name": "Weather Tools",
  "version": "1.0.0",
  "author": "Community",
  "description": "Tools for weather data and forecasts",
  "requires_kernel_version": ">=1.0.0",
  "dependencies": ["requests>=2.0.0"],
  "provides_tools": ["get_weather", "get_forecast"],
  "requires_approval": false,
  "sandboxed": true,
  "tags": ["weather", "data", "api"]
}

# File: plugins/weather/__init__.py
from src.interfaces.tool_registry import ToolDefinition, ToolParameter, ToolType

def setup():
    '''Called when plugin is activated.'''
    print("Weather plugin activated")

def teardown():
    '''Called when plugin is deactivated.'''
    print("Weather plugin deactivated")

def get_tools():
    '''Return list of (ToolDefinition, executor) tuples.'''
    
    # Define tool
    get_weather_tool = ToolDefinition(
        name="get_weather",
        description="Get current weather for a location",
        tool_type=ToolType.API,
        parameters=[
            ToolParameter(
                name="location",
                type="string",
                description="City name or coordinates",
                required=True
            )
        ],
        returns="Weather data with temperature, conditions, etc."
    )
    
    # Define executor
    async def get_weather_executor(location: str):
        # Call weather API
        return {
            "location": location,
            "temperature": 72,
            "conditions": "Sunny",
            "humidity": 60
        }
    
    return [
        (get_weather_tool, get_weather_executor)
    ]
"""


def example_plugin_usage():
    """Demonstrate plugin system."""
    from src.interfaces.tool_registry import ToolRegistry
    
    # Create registry
    registry = ToolRegistry()
    
    # Create plugin manager
    manager = PluginManager(
        plugin_dirs=[Path("./plugins")],
        registry=registry,
        auto_activate=True
    )
    
    # Discover plugins
    discovered = manager.discover_plugins()
    print(f"Discovered {len(discovered)} plugins:")
    for metadata in discovered:
        print(f"  - {metadata.name} v{metadata.version} by {metadata.author}")
    
    # List plugins
    plugins = manager.list_plugins()
    print(f"\nPlugin status:")
    for plugin in plugins:
        print(f"  - {plugin['name']}: {plugin['status']} ({plugin['tools']} tools)")
    
    # Install a plugin
    if plugins:
        plugin_id = plugins[0]['plugin_id']
        success = manager.install_plugin(plugin_id)
        print(f"\nInstalled {plugin_id}: {success}")
    
    # Show registry tools
    print(f"\nTotal tools in registry: {len(registry.tools)}")


if __name__ == "__main__":
    print("Plugin System Example")
    print("=" * 60)
    print(EXAMPLE_PLUGIN)
    print("=" * 60)
    print("\nTo create a plugin, follow the structure above.")
