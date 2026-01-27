"""
Skill Mapper - Tool signature matching and lesson-to-tool mapping.

This module implements the "Signature Matching" strategy that determines which tool
owns a specific lesson. This is critical for the Skill Cache (Tier 2) system, ensuring
that SQL lessons are only injected when SQL tools are active.

Key Components:
1. ToolSignature: Defines the "fingerprint" of a tool (keywords, file patterns)
2. SkillMapper: Maps failure traces to tools using signature matching
3. Two-phase extraction: Direct hit (explicit tool name) + Semantic fallback (content analysis)

The Problem This Solves:
Without this, we'd inject SQL lessons when using an Email tool, or Python lessons
when querying a database. The Skill Cache is only valuable if we inject the RIGHT
lessons for the RIGHT tools.
"""

import logging
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from src.kernel.schemas import FailureTrace

logger = logging.getLogger(__name__)


class ToolSignature(BaseModel):
    """
    The "fingerprint" of a tool for signature matching.
    
    This defines what makes a tool recognizable:
    - tool_name: Canonical name (e.g., "sql_db", "python_repl")
    - keywords: Terms that indicate this tool (e.g., ["SELECT", "JOIN", "table"])
    - file_patterns: File extensions/patterns (e.g., [".sql", ".db"])
    
    Example:
        SQL Tool: keywords=["select", "join", "query"], file_patterns=[".sql"]
        Python Tool: keywords=["import", "print", "def"], file_patterns=[".py"]
    """
    tool_name: str = Field(..., description="Canonical tool name")
    keywords: List[str] = Field(
        default_factory=list,
        description="Keywords that indicate this tool"
    )
    file_patterns: List[str] = Field(
        default_factory=list,
        description="File patterns/extensions associated with this tool"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "tool_name": "sql_db",
                "keywords": ["select", "join", "table", "query", "database"],
                "file_patterns": [".sql", ".db"]
            }
        }
    }


class SkillMapper:
    """
    Maps failure traces to tools using signature matching.
    
    This implements the two-phase extraction strategy:
    1. Direct Hit: Check if tool name is explicitly in the trace
    2. Semantic Fallback: Analyze content for tool-specific keywords
    
    The registry contains all known tools and their signatures. In production,
    this would be loaded from configuration or discovered dynamically.
    
    Architecture:
    - Registry: Dict[tool_name, ToolSignature]
    - extract_tool_context(): Main entry point for tool extraction
    - _check_direct_hit(): Phase 1 - explicit tool name matching
    - _check_semantic_match(): Phase 2 - keyword-based matching
    """
    
    # Confidence threshold for semantic matching (minimum keyword matches required)
    SEMANTIC_CONFIDENCE_THRESHOLD = 2
    
    def __init__(self, custom_registry: Optional[Dict[str, ToolSignature]] = None):
        """
        Initialize SkillMapper with tool registry.
        
        Args:
            custom_registry: Optional custom tool registry. If None, uses default.
        """
        if custom_registry:
            self.registry = custom_registry
        else:
            # Default registry with common tools
            self.registry = self._build_default_registry()
        
        logger.info(f"SkillMapper initialized with {len(self.registry)} tools")
    
    def _build_default_registry(self) -> Dict[str, ToolSignature]:
        """
        Build the default tool registry.
        
        This contains common tools with their signatures. In production,
        this would be loaded from configuration files or discovered from
        the agent's available tools.
        """
        return {
            "sql_db": ToolSignature(
                tool_name="sql_db",
                keywords=["select", "table", "query", "join", "where", "database", "sql"],
                file_patterns=[".sql", ".db"]
            ),
            "python_repl": ToolSignature(
                tool_name="python_repl",
                keywords=["import", "print", "def", "class", "python", "execute"],
                file_patterns=[".py"]
            ),
            "file_operations": ToolSignature(
                tool_name="file_operations",
                keywords=["read file", "write file", "file", "directory", "path"],
                file_patterns=[".txt", ".json", ".csv"]
            ),
            "api_client": ToolSignature(
                tool_name="api_client",
                keywords=["http", "request", "api", "endpoint", "get", "post"],
                file_patterns=[".json", ".xml"]
            ),
            "search": ToolSignature(
                tool_name="search",
                keywords=["search", "find", "lookup", "query", "results"],
                file_patterns=[]
            )
        }
    
    def extract_tool_context(self, failure_trace: FailureTrace) -> str:
        """
        Determines which tool owns this lesson.
        
        This is the main entry point for tool extraction. It uses a two-phase
        strategy to maximize accuracy:
        
        Phase 1 - Direct Hit:
        Check if the tool name is explicitly mentioned in the tool_call field.
        This is the most reliable indicator.
        
        Phase 2 - Semantic Fallback:
        If no explicit tool name, analyze the agent_reasoning and tool_output
        for keywords that match tool signatures.
        
        Args:
            failure_trace: The failure trace to analyze
            
        Returns:
            str: The tool name (e.g., "sql_db") or "general" if no match
        
        Examples:
            >>> trace = FailureTrace(
            ...     user_prompt="Query the database",
            ...     agent_reasoning="I'll SELECT * FROM users",
            ...     tool_call={"tool": "sql_db", "query": "SELECT * FROM users"},
            ...     tool_output="Error: missing WHERE clause",
            ...     failure_type="commission_safety",
            ...     severity="critical"
            ... )
            >>> mapper.extract_tool_context(trace)
            'sql_db'  # Direct hit from tool_call
        """
        # Phase 1: Direct Hit - Check tool_call for explicit tool name
        tool_name = self._check_direct_hit(failure_trace)
        if tool_name:
            logger.info(f"✓ Direct hit: Tool '{tool_name}' from tool_call")
            return tool_name
        
        # Phase 2: Semantic Fallback - Analyze content for keywords
        tool_name = self._check_semantic_match(failure_trace)
        if tool_name:
            logger.info(f"✓ Semantic match: Tool '{tool_name}' from content analysis")
            return tool_name
        
        # No match found - belongs to general agent context
        logger.info("✓ No tool match - assigning to 'general' context")
        return "general"
    
    def _check_direct_hit(self, failure_trace: FailureTrace) -> Optional[str]:
        """
        Phase 1: Check for explicit tool name in tool_call.
        
        This is the most reliable method - if the tool_call contains
        a "tool" or "name" field, we use that directly.
        
        Args:
            failure_trace: The failure trace to check
            
        Returns:
            Optional[str]: Tool name if found, None otherwise
        """
        if not failure_trace.tool_call:
            return None
        
        # Check common field names for tool identification
        tool_call = failure_trace.tool_call
        
        # Direct tool name in tool_call
        for field in ["tool", "tool_name", "name", "function"]:
            if field in tool_call:
                tool_value = tool_call[field]
                # Check if it's in our registry
                if tool_value in self.registry:
                    return tool_value
                # Check if it's a variant (e.g., "sql" -> "sql_db")
                for registered_tool in self.registry:
                    if tool_value.lower() in registered_tool.lower():
                        return registered_tool
        
        return None
    
    def _check_semantic_match(self, failure_trace: FailureTrace) -> Optional[str]:
        """
        Phase 2: Semantic fallback using keyword matching.
        
        This analyzes the agent_reasoning and tool_output for keywords
        that match tool signatures. We score each tool and return the
        best match if confidence is high enough.
        
        Args:
            failure_trace: The failure trace to analyze
            
        Returns:
            Optional[str]: Best matching tool name, or None if no strong match
        """
        # Combine text fields for analysis
        content_parts = []
        
        if failure_trace.agent_reasoning:
            content_parts.append(failure_trace.agent_reasoning.lower())
        
        if failure_trace.tool_output:
            content_parts.append(failure_trace.tool_output.lower())
        
        if failure_trace.user_prompt:
            content_parts.append(failure_trace.user_prompt.lower())
        
        if not content_parts:
            return None
        
        content = " ".join(content_parts)
        
        # Score each tool based on keyword matches
        scores: Dict[str, int] = {}
        
        for tool_name, signature in self.registry.items():
            score = 0
            
            # Count keyword matches
            for keyword in signature.keywords:
                if keyword.lower() in content:
                    score += 1
            
            # Count file pattern matches
            for pattern in signature.file_patterns:
                if pattern in content:
                    score += 2  # File patterns are stronger signals
            
            if score > 0:
                scores[tool_name] = score
        
        if not scores:
            return None
        
        # Return tool with highest score (if confidence threshold met)
        best_tool = max(scores, key=scores.get)
        best_score = scores[best_tool]
        
        # Require minimum threshold for confidence
        if best_score >= self.SEMANTIC_CONFIDENCE_THRESHOLD:
            return best_tool
        
        return None
    
    def add_tool_signature(self, signature: ToolSignature) -> None:
        """
        Add a new tool signature to the registry.
        
        This allows dynamic registration of tools at runtime.
        
        Args:
            signature: The tool signature to add
        """
        self.registry[signature.tool_name] = signature
        logger.info(f"Added tool signature: {signature.tool_name}")
    
    def get_tool_signature(self, tool_name: str) -> Optional[ToolSignature]:
        """
        Get the signature for a specific tool.
        
        Args:
            tool_name: The tool name to look up
            
        Returns:
            Optional[ToolSignature]: The signature if found, None otherwise
        """
        return self.registry.get(tool_name)
    
    def list_tools(self) -> List[str]:
        """
        List all registered tool names.
        
        Returns:
            List[str]: List of tool names in the registry
        """
        return list(self.registry.keys())
