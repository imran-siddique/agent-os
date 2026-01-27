"""
Context Triad Manager for Hot, Warm, Cold context layers.

The Context Triad treats context like a tiered storage system defined by intimacy:

L1: Hot Context (The Situation)
    - What is happening right now?
    - Current conversation, open VS Code tabs, error logs streaming
    - Policy: "Attention Head" - overrides everything
    
L2: Warm Context (The Persona)
    - Who am I?
    - LinkedIn profile, Medium articles, coding style preferences
    - Policy: "Filter" - Always on, colors how AI speaks to you
    
L3: Cold Context (The Archive)
    - What happened last year?
    - Old tickets, closed PRs, historical design docs
    - Policy: "On Demand" - only fetch if explicitly asked
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

from caas.models import ContextLayer, ContextTriadItem, ContextTriadState


class ContextTriadManager:
    """
    Manages the three-tier context system (Hot, Warm, Cold).
    
    The Context Triad is defined by intimacy, not just speed:
    - Hot: Current situation (overrides everything)
    - Warm: User persona (always-on filter)
    - Cold: Historical archive (on-demand only)
    """
    
    def __init__(self):
        """Initialize the context triad manager."""
        self.state = ContextTriadState()
    
    def add_hot_context(
        self, 
        content: str, 
        metadata: Optional[Dict[str, Any]] = None,
        priority: float = 1.0
    ) -> str:
        """
        Add hot context - the current situation.
        
        Hot context represents what is happening RIGHT NOW:
        - Current conversation messages
        - Open VS Code tabs
        - Error logs streaming in real-time
        - Active debugging session
        
        Policy: "Attention Head" - Hot context overrides everything.
        It has the highest priority and is always included.
        
        Args:
            content: The hot context content
            metadata: Optional metadata (e.g., source, type)
            priority: Priority level (higher = more important)
            
        Returns:
            The ID of the created context item
        """
        item_id = str(uuid.uuid4())
        item = ContextTriadItem(
            id=item_id,
            layer=ContextLayer.HOT,
            content=content,
            metadata=metadata or {},
            timestamp=datetime.utcnow().isoformat(),
            priority=priority
        )
        self.state.hot_context.append(item)
        
        # Keep hot context fresh - limit to recent items (last 50)
        if len(self.state.hot_context) > 50:
            # Sort by timestamp and keep most recent
            self.state.hot_context.sort(key=lambda x: x.timestamp or "", reverse=True)
            self.state.hot_context = self.state.hot_context[:50]
        
        return item_id
    
    def add_warm_context(
        self, 
        content: str, 
        metadata: Optional[Dict[str, Any]] = None,
        priority: float = 1.0
    ) -> str:
        """
        Add warm context - the user persona.
        
        Warm context represents WHO THE USER IS:
        - LinkedIn profile
        - Medium articles
        - GitHub bio
        - Coding style preferences
        - Favorite libraries
        - Communication style
        
        Policy: "Always On Filter" - Warm context is persistent and colors
        how the AI speaks to you. It doesn't need to be retrieved every time;
        it should be part of the system prompt.
        
        Args:
            content: The warm context content
            metadata: Optional metadata (e.g., source, category)
            priority: Priority level (higher = more important)
            
        Returns:
            The ID of the created context item
        """
        item_id = str(uuid.uuid4())
        item = ContextTriadItem(
            id=item_id,
            layer=ContextLayer.WARM,
            content=content,
            metadata=metadata or {},
            timestamp=datetime.utcnow().isoformat(),
            priority=priority
        )
        self.state.warm_context.append(item)
        return item_id
    
    def add_cold_context(
        self, 
        content: str, 
        metadata: Optional[Dict[str, Any]] = None,
        priority: float = 1.0
    ) -> str:
        """
        Add cold context - the historical archive.
        
        Cold context represents WHAT HAPPENED IN THE PAST:
        - Old tickets from last year
        - Closed PRs
        - Historical design docs
        - Legacy system documentation
        - Archived meeting notes
        
        Policy: "On Demand Only" - Cold context is NEVER automatically
        included. It's only fetched when the user explicitly asks for history.
        Never let cold data pollute the hot window.
        
        Args:
            content: The cold context content
            metadata: Optional metadata (e.g., date, source)
            priority: Priority level (higher = more important)
            
        Returns:
            The ID of the created context item
        """
        item_id = str(uuid.uuid4())
        item = ContextTriadItem(
            id=item_id,
            layer=ContextLayer.COLD,
            content=content,
            metadata=metadata or {},
            timestamp=datetime.utcnow().isoformat(),
            priority=priority
        )
        self.state.cold_context.append(item)
        return item_id
    
    def get_hot_context(
        self, 
        max_tokens: int = 1000,
        include_metadata: bool = False
    ) -> str:
        """
        Get hot context (current situation).
        
        Hot context is ALWAYS included and has highest priority.
        It represents the "Attention Head" - what you're focused on right now.
        
        Args:
            max_tokens: Maximum tokens to return
            include_metadata: Whether to include metadata in output
            
        Returns:
            Formatted hot context string
        """
        if not self.state.hot_context:
            return ""
        
        # Sort by priority (highest first) then timestamp (most recent first)
        sorted_items = sorted(
            self.state.hot_context,
            key=lambda x: (-x.priority, x.timestamp or ""),
            reverse=False
        )
        
        # Build context within token limit
        context_parts = ["# Hot Context (Current Situation)\n"]
        total_chars = len(context_parts[0])
        char_limit = max_tokens * 4  # Approximate: 4 chars per token
        
        for item in sorted_items:
            if include_metadata:
                item_text = f"\n## {item.metadata.get('source', 'Unknown')}\n{item.content}\n"
            else:
                item_text = f"\n{item.content}\n"
            
            if total_chars + len(item_text) > char_limit:
                break
            
            context_parts.append(item_text)
            total_chars += len(item_text)
        
        return "".join(context_parts)
    
    def get_warm_context(
        self, 
        max_tokens: int = 500,
        include_metadata: bool = False
    ) -> str:
        """
        Get warm context (user persona).
        
        Warm context is ALWAYS ON and acts as a filter that colors
        how the AI communicates with you.
        
        Args:
            max_tokens: Maximum tokens to return
            include_metadata: Whether to include metadata in output
            
        Returns:
            Formatted warm context string
        """
        if not self.state.warm_context:
            return ""
        
        # Sort by priority (highest first)
        sorted_items = sorted(
            self.state.warm_context,
            key=lambda x: x.priority,
            reverse=True
        )
        
        # Build context within token limit
        context_parts = ["# Warm Context (User Persona)\n"]
        total_chars = len(context_parts[0])
        char_limit = max_tokens * 4  # Approximate: 4 chars per token
        
        for item in sorted_items:
            if include_metadata:
                category = item.metadata.get('category', 'General')
                item_text = f"\n## {category}\n{item.content}\n"
            else:
                item_text = f"\n{item.content}\n"
            
            if total_chars + len(item_text) > char_limit:
                break
            
            context_parts.append(item_text)
            total_chars += len(item_text)
        
        return "".join(context_parts)
    
    def get_cold_context(
        self, 
        query: Optional[str] = None,
        max_tokens: int = 1000,
        include_metadata: bool = False
    ) -> str:
        """
        Get cold context (historical archive).
        
        Cold context is ON DEMAND ONLY. It's never automatically included.
        You must explicitly request it with a query.
        
        Policy: Never let cold data pollute the hot window.
        
        Args:
            query: Search query to filter cold context (required)
            max_tokens: Maximum tokens to return
            include_metadata: Whether to include metadata in output
            
        Returns:
            Formatted cold context string (empty if no query provided)
        """
        # Cold context requires explicit query
        if not query or not self.state.cold_context:
            return ""
        
        # Filter items based on query
        query_lower = query.lower()
        matching_items = [
            item for item in self.state.cold_context
            if query_lower in item.content.lower() or
               query_lower in str(item.metadata).lower()
        ]
        
        if not matching_items:
            return ""
        
        # Sort by priority (highest first) then timestamp (most recent first)
        sorted_items = sorted(
            matching_items,
            key=lambda x: (-x.priority, x.timestamp or ""),
            reverse=False
        )
        
        # Build context within token limit
        context_parts = ["# Cold Context (Historical Archive)\n"]
        context_parts.append(f"_Query: {query}_\n")
        total_chars = sum(len(p) for p in context_parts)
        char_limit = max_tokens * 4  # Approximate: 4 chars per token
        
        for item in sorted_items:
            if include_metadata:
                date = item.metadata.get('date', 'Unknown')
                item_text = f"\n## {date}\n{item.content}\n"
            else:
                item_text = f"\n{item.content}\n"
            
            if total_chars + len(item_text) > char_limit:
                break
            
            context_parts.append(item_text)
            total_chars += len(item_text)
        
        return "".join(context_parts)
    
    def get_full_context(
        self,
        include_hot: bool = True,
        include_warm: bool = True,
        include_cold: bool = False,
        cold_query: Optional[str] = None,
        max_tokens_per_layer: Optional[Dict[str, int]] = None,
        include_metadata: bool = False
    ) -> Dict[str, Any]:
        """
        Get the complete context triad.
        
        The Context Triad follows these policies:
        1. Hot Context: ALWAYS included (unless explicitly disabled)
        2. Warm Context: ALWAYS ON (unless explicitly disabled)
        3. Cold Context: ON DEMAND ONLY (requires explicit query)
        
        Args:
            include_hot: Include hot context (default: True)
            include_warm: Include warm context (default: True)
            include_cold: Include cold context (default: False)
            cold_query: Query for cold context retrieval (required if include_cold=True)
            max_tokens_per_layer: Token limits per layer
            include_metadata: Whether to include metadata in output
            
        Returns:
            Dictionary with context from each layer
        """
        if max_tokens_per_layer is None:
            max_tokens_per_layer = {"hot": 1000, "warm": 500, "cold": 1000}
        
        result = {
            "hot_context": "",
            "warm_context": "",
            "cold_context": "",
            "layers_included": [],
            "total_tokens": 0,
            "metadata": {
                "hot_items_count": len(self.state.hot_context),
                "warm_items_count": len(self.state.warm_context),
                "cold_items_count": len(self.state.cold_context),
            }
        }
        
        # Hot Context: The Situation (highest priority, overrides everything)
        if include_hot:
            hot_context = self.get_hot_context(
                max_tokens=max_tokens_per_layer.get("hot", 1000),
                include_metadata=include_metadata
            )
            if hot_context:
                result["hot_context"] = hot_context
                result["layers_included"].append("hot")
                result["total_tokens"] += len(hot_context) // 4
        
        # Warm Context: The Persona (always-on filter)
        if include_warm:
            warm_context = self.get_warm_context(
                max_tokens=max_tokens_per_layer.get("warm", 500),
                include_metadata=include_metadata
            )
            if warm_context:
                result["warm_context"] = warm_context
                result["layers_included"].append("warm")
                result["total_tokens"] += len(warm_context) // 4
        
        # Cold Context: The Archive (on-demand only, requires query)
        if include_cold and cold_query:
            cold_context = self.get_cold_context(
                query=cold_query,
                max_tokens=max_tokens_per_layer.get("cold", 1000),
                include_metadata=include_metadata
            )
            if cold_context:
                result["cold_context"] = cold_context
                result["layers_included"].append("cold")
                result["total_tokens"] += len(cold_context) // 4
        
        return result
    
    def clear_hot_context(self):
        """Clear all hot context items."""
        self.state.hot_context = []
    
    def clear_warm_context(self):
        """Clear all warm context items."""
        self.state.warm_context = []
    
    def clear_cold_context(self):
        """Clear all cold context items."""
        self.state.cold_context = []
    
    def clear_all(self):
        """Clear all context layers."""
        self.state = ContextTriadState()
    
    def remove_item(self, item_id: str, layer: Optional[ContextLayer] = None) -> bool:
        """
        Remove a specific item from context.
        
        Args:
            item_id: The ID of the item to remove
            layer: Optional layer to search in (searches all if not provided)
            
        Returns:
            True if item was found and removed, False otherwise
        """
        if layer is None or layer == ContextLayer.HOT:
            for i, item in enumerate(self.state.hot_context):
                if item.id == item_id:
                    del self.state.hot_context[i]
                    return True
        
        if layer is None or layer == ContextLayer.WARM:
            for i, item in enumerate(self.state.warm_context):
                if item.id == item_id:
                    del self.state.warm_context[i]
                    return True
        
        if layer is None or layer == ContextLayer.COLD:
            for i, item in enumerate(self.state.cold_context):
                if item.id == item_id:
                    del self.state.cold_context[i]
                    return True
        
        return False
    
    def get_state(self) -> ContextTriadState:
        """
        Get the current state of the context triad.
        
        Returns:
            The current context triad state
        """
        return self.state
    
    def set_state(self, state: ContextTriadState):
        """
        Set the context triad state.
        
        Args:
            state: The new context triad state
        """
        self.state = state
