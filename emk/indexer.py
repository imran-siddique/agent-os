"""
Indexer - Logic for hashing and tagging episodes for efficient retrieval.

The indexer provides utilities for generating searchable tags and embeddings
from episodes to enable efficient retrieval by caas or other systems.
"""

from typing import List, Set, Dict, Any
import hashlib
import re

from emk.schema import Episode


class Indexer:
    """
    Utilities for indexing and tagging episodes.
    
    The indexer provides methods to extract tags, generate embeddings,
    and create searchable metadata from episodes.
    """
    
    @staticmethod
    def extract_tags(text: str, min_length: int = 3) -> Set[str]:
        """
        Extract potential search tags from text.
        
        Args:
            text: The text to extract tags from
            min_length: Minimum length for a tag (default: 3)
            
        Returns:
            Set of extracted tags (lowercased)
        """
        # Remove punctuation and split into words
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Filter by minimum length and remove common stop words
        stop_words = {
            'the', 'is', 'at', 'which', 'on', 'and', 'a', 'an', 
            'as', 'are', 'was', 'were', 'been', 'be', 'have', 'has',
            'had', 'do', 'does', 'did', 'will', 'would', 'should',
            'could', 'may', 'might', 'must', 'can', 'to', 'from',
            'in', 'out', 'up', 'down', 'for', 'with', 'by', 'of'
        }
        
        tags = {
            word for word in words 
            if len(word) >= min_length and word not in stop_words
        }
        
        return tags
    
    @staticmethod
    def generate_episode_tags(episode: Episode) -> List[str]:
        """
        Generate searchable tags from an episode.
        
        Args:
            episode: The episode to generate tags from
            
        Returns:
            List of tags for indexing
        """
        # Combine all text fields
        combined_text = f"{episode.goal} {episode.action} {episode.result} {episode.reflection}"
        
        # Extract tags
        tags = Indexer.extract_tags(combined_text)
        
        # Add metadata keys as tags
        for key in episode.metadata.keys():
            tags.add(key.lower())
        
        return sorted(list(tags))
    
    @staticmethod
    def compute_content_hash(episode: Episode) -> str:
        """
        Compute a stable hash of episode content.
        
        Args:
            episode: The episode to hash
            
        Returns:
            SHA-256 hash of the episode content
        """
        # Use the episode's own ID generation logic
        return episode.episode_id
    
    @staticmethod
    def enrich_metadata(episode: Episode, auto_tags: bool = True) -> Dict[str, Any]:
        """
        Enrich episode metadata with indexing information.
        
        Args:
            episode: The episode to enrich
            auto_tags: Whether to automatically generate and add tags
            
        Returns:
            Enriched metadata dictionary
        """
        enriched = episode.metadata.copy()
        
        if auto_tags and 'tags' not in enriched:
            enriched['tags'] = Indexer.generate_episode_tags(episode)
        
        # Add content length metrics
        enriched['goal_length'] = len(episode.goal)
        enriched['action_length'] = len(episode.action)
        enriched['result_length'] = len(episode.result)
        enriched['reflection_length'] = len(episode.reflection)
        
        return enriched
    
    @staticmethod
    def create_search_text(episode: Episode) -> str:
        """
        Create a concatenated search text from an episode.
        
        This is useful for systems that need a single text representation
        for embedding or full-text search.
        
        Args:
            episode: The episode to create search text from
            
        Returns:
            Concatenated search text
        """
        parts = [
            f"Goal: {episode.goal}",
            f"Action: {episode.action}",
            f"Result: {episode.result}",
            f"Reflection: {episode.reflection}"
        ]
        
        # Add metadata if present
        if episode.metadata:
            metadata_str = ", ".join(
                f"{k}: {v}" for k, v in episode.metadata.items()
            )
            parts.append(f"Context: {metadata_str}")
        
        return " | ".join(parts)
