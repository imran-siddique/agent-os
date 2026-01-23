"""
Store - Abstract interfaces and implementations for episodic memory storage.

This module provides:
- VectorStoreAdapter: Abstract interface for vector stores
- FileAdapter: Simple JSONL-based storage for local logging
- ChromaDBAdapter: ChromaDB-based vector storage (optional)
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from pathlib import Path
import json
import numpy as np

from emk.schema import Episode


class VectorStoreAdapter(ABC):
    """
    Abstract interface for vector store implementations.
    
    All adapters must implement store and retrieve methods for episodes.
    The store is append-only - no updates or deletes are allowed.
    """
    
    @abstractmethod
    def store(self, episode: Episode, embedding: Optional[np.ndarray] = None) -> str:
        """
        Store an episode in the vector store.
        
        Args:
            episode: The episode to store
            embedding: Optional pre-computed embedding vector
            
        Returns:
            The episode_id of the stored episode
        """
        pass
    
    @abstractmethod
    def retrieve(
        self, 
        query_embedding: Optional[np.ndarray] = None,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10
    ) -> List[Episode]:
        """
        Retrieve episodes from the store.
        
        Args:
            query_embedding: Optional embedding vector for similarity search
            filters: Optional metadata filters (e.g., {"user_id": "123"})
            limit: Maximum number of episodes to return
            
        Returns:
            List of matching episodes
        """
        pass
    
    @abstractmethod
    def get_by_id(self, episode_id: str) -> Optional[Episode]:
        """
        Retrieve a specific episode by its ID.
        
        Args:
            episode_id: The unique episode identifier
            
        Returns:
            The episode if found, None otherwise
        """
        pass


class FileAdapter(VectorStoreAdapter):
    """
    Simple JSONL-based file storage adapter for local logging.
    
    This adapter stores episodes as newline-delimited JSON (JSONL) for
    simple persistence without requiring external dependencies.
    """
    
    def __init__(self, filepath: str = "episodes.jsonl"):
        """
        Initialize the file adapter.
        
        Args:
            filepath: Path to the JSONL file for storage
        """
        self.filepath = Path(filepath)
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Ensure file exists
        if not self.filepath.exists():
            self.filepath.touch()
    
    def store(self, episode: Episode, embedding: Optional[np.ndarray] = None) -> str:
        """
        Append an episode to the JSONL file.
        
        Args:
            episode: The episode to store
            embedding: Ignored for file adapter
            
        Returns:
            The episode_id of the stored episode
        """
        with open(self.filepath, 'a') as f:
            f.write(episode.to_json() + '\n')
        return episode.episode_id
    
    def retrieve(
        self, 
        query_embedding: Optional[np.ndarray] = None,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10
    ) -> List[Episode]:
        """
        Retrieve episodes from the file.
        
        Args:
            query_embedding: Ignored for file adapter (no similarity search)
            filters: Optional metadata filters
            limit: Maximum number of episodes to return
            
        Returns:
            List of matching episodes (most recent first)
        """
        episodes = []
        
        if not self.filepath.exists() or self.filepath.stat().st_size == 0:
            return episodes
        
        with open(self.filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                    
                try:
                    episode = Episode.from_json(line)
                    
                    # Apply filters if provided
                    if filters:
                        match = all(
                            episode.metadata.get(key) == value 
                            for key, value in filters.items()
                        )
                        if not match:
                            continue
                    
                    episodes.append(episode)
                except Exception:
                    # Skip invalid lines
                    continue
        
        # Return most recent episodes first
        episodes.reverse()
        return episodes[:limit]
    
    def get_by_id(self, episode_id: str) -> Optional[Episode]:
        """
        Retrieve a specific episode by its ID.
        
        Args:
            episode_id: The unique episode identifier
            
        Returns:
            The episode if found, None otherwise
        """
        if not self.filepath.exists():
            return None
        
        with open(self.filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                    
                try:
                    episode = Episode.from_json(line)
                    if episode.episode_id == episode_id:
                        return episode
                except Exception:
                    continue
        
        return None


# ChromaDB adapter - only available if chromadb is installed
try:
    import chromadb
    from chromadb.config import Settings
    
    class ChromaDBAdapter(VectorStoreAdapter):
        """
        ChromaDB-based vector storage adapter.
        
        This adapter uses ChromaDB for vector similarity search and
        efficient retrieval of episodes based on embeddings.
        """
        
        def __init__(
            self, 
            collection_name: str = "episodes",
            persist_directory: str = "./chroma_data"
        ):
            """
            Initialize the ChromaDB adapter.
            
            Args:
                collection_name: Name of the ChromaDB collection
                persist_directory: Directory for persistent storage
            """
            self.client = chromadb.Client(Settings(
                persist_directory=persist_directory,
                anonymized_telemetry=False
            ))
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"description": "Episodic memory storage"}
            )
        
        def store(self, episode: Episode, embedding: Optional[np.ndarray] = None) -> str:
            """
            Store an episode in ChromaDB.
            
            Args:
                episode: The episode to store
                embedding: Optional pre-computed embedding vector
                
            Returns:
                The episode_id of the stored episode
            """
            # If no embedding provided, create a simple text representation
            if embedding is None:
                # Create a text representation for ChromaDB to embed
                text = f"{episode.goal} {episode.action} {episode.result} {episode.reflection}"
            else:
                text = None
            
            # Store in ChromaDB
            self.collection.add(
                ids=[episode.episode_id],
                documents=[text] if text else None,
                embeddings=[embedding.tolist()] if embedding is not None else None,
                metadatas=[{
                    "goal": episode.goal,
                    "action": episode.action,
                    "result": episode.result,
                    "reflection": episode.reflection,
                    "timestamp": episode.timestamp.isoformat(),
                    **episode.metadata
                }]
            )
            
            return episode.episode_id
        
        def retrieve(
            self, 
            query_embedding: Optional[np.ndarray] = None,
            filters: Optional[Dict[str, Any]] = None,
            limit: int = 10
        ) -> List[Episode]:
            """
            Retrieve episodes from ChromaDB.
            
            Args:
                query_embedding: Optional embedding vector for similarity search
                filters: Optional metadata filters
                limit: Maximum number of episodes to return
                
            Returns:
                List of matching episodes
            """
            if query_embedding is not None:
                # Query by embedding similarity
                results = self.collection.query(
                    query_embeddings=[query_embedding.tolist()],
                    n_results=limit,
                    where=filters
                )
            else:
                # Get all (or filtered) results
                results = self.collection.get(
                    limit=limit,
                    where=filters
                )
            
            # Convert results to Episodes
            episodes = []
            metadatas = results.get('metadatas', [[]])[0] if 'metadatas' in results else results.get('metadatas', [])
            
            if not metadatas:
                return episodes
            
            for metadata in metadatas:
                # Extract episode fields from metadata
                episode_data = {
                    "goal": metadata.pop("goal", ""),
                    "action": metadata.pop("action", ""),
                    "result": metadata.pop("result", ""),
                    "reflection": metadata.pop("reflection", ""),
                    "timestamp": metadata.pop("timestamp", None),
                    "metadata": metadata
                }
                
                try:
                    episode = Episode(**episode_data)
                    episodes.append(episode)
                except Exception:
                    # Skip invalid episodes
                    continue
            
            return episodes
        
        def get_by_id(self, episode_id: str) -> Optional[Episode]:
            """
            Retrieve a specific episode by its ID.
            
            Args:
                episode_id: The unique episode identifier
                
            Returns:
                The episode if found, None otherwise
            """
            try:
                results = self.collection.get(ids=[episode_id])
                
                if not results['ids']:
                    return None
                
                metadata = results['metadatas'][0]
                episode_data = {
                    "goal": metadata.pop("goal", ""),
                    "action": metadata.pop("action", ""),
                    "result": metadata.pop("result", ""),
                    "reflection": metadata.pop("reflection", ""),
                    "timestamp": metadata.pop("timestamp", None),
                    "metadata": metadata
                }
                
                return Episode(**episode_data)
            except Exception:
                return None

except ImportError:
    # ChromaDB not installed, skip the adapter
    pass
