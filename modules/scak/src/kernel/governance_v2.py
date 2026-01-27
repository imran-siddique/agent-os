"""
Emergence Monitor - Graph-based anomaly detection for multi-agent swarms.

This implements the "Safety Layer" for swarm intelligence - detecting emergent
behaviors that only exist in agent-to-agent interactions, not in individual messages.

Detection Vectors:
1. Echo Chambers - Agents repeating similar content (semantic similarity > 0.9)
2. Approval Spirals - Infinite "After you" loops (graph cycles)
3. Goal Drift - Semantic divergence from original intent (cosine distance > threshold)
4. Escalation Spirals - Agents keep deferring to each other

Architecture:
- Uses networkx for graph topology analysis (cycle detection)
- Uses vector embeddings for semantic drift detection
- Operates on SwarmTrace, not individual messages
- Emits AnomalyDecision with circuit breaker suggestions

This is inspired by chaos engineering and distributed systems monitoring.
"""

import logging
import hashlib
from typing import Dict, Any, Optional, List, Set, Tuple
from datetime import datetime
from collections import Counter

try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False
    nx = None

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None

from src.kernel.schemas import (
    SwarmTrace, SwarmStep, AnomalyDecision, AnomalyType
)

logger = logging.getLogger(__name__)


class VectorStore:
    """
    Simple vector store for semantic similarity computation.
    
    In production, this would use:
    - OpenAI embeddings API
    - Sentence-transformers
    - Pinecone/Weaviate/Chroma
    
    For now, we simulate with simple hashing-based embeddings.
    """
    
    def __init__(self, embedding_dim: int = 384):
        """
        Initialize vector store.
        
        Args:
            embedding_dim: Dimension of embedding vectors
        """
        self.embedding_dim = embedding_dim
        self.cache: Dict[str, List[float]] = {}
    
    def embed(self, text: str) -> List[float]:
        """
        Generate embedding for text.
        
        This is a mock implementation using deterministic hashing.
        In production, would call actual embedding model.
        
        Args:
            text: Text to embed
            
        Returns:
            List[float]: Embedding vector
        """
        if text in self.cache:
            return self.cache[text]
        
        # Mock: Hash text and convert to pseudo-random vector
        # In production: embedding = openai.embeddings.create(input=text)
        text_hash = hashlib.md5(text.encode()).hexdigest()
        
        # Convert hex to pseudo-random floats (deterministic)
        if NUMPY_AVAILABLE:
            seed = int(text_hash[:8], 16)
            rng = np.random.RandomState(seed)
            embedding = rng.randn(self.embedding_dim).tolist()
            
            # Normalize
            norm = sum(x**2 for x in embedding) ** 0.5
            embedding = [x / norm for x in embedding]
        else:
            # Fallback: simple hash-based embedding
            embedding = [float(int(text_hash[i:i+2], 16)) / 255.0 
                        for i in range(0, min(len(text_hash), self.embedding_dim * 2), 2)]
            
            # Pad if needed
            while len(embedding) < self.embedding_dim:
                embedding.append(0.0)
            embedding = embedding[:self.embedding_dim]
        
        self.cache[text] = embedding
        return embedding
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Compute cosine similarity between two vectors.
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            float: Cosine similarity (0.0-1.0)
        """
        if NUMPY_AVAILABLE:
            v1 = np.array(vec1)
            v2 = np.array(vec2)
            
            dot = np.dot(v1, v2)
            norm1 = np.linalg.norm(v1)
            norm2 = np.linalg.norm(v2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return float(dot / (norm1 * norm2))
        else:
            # Manual computation
            dot = sum(a * b for a, b in zip(vec1, vec2))
            norm1 = sum(x**2 for x in vec1) ** 0.5
            norm2 = sum(x**2 for x in vec2) ** 0.5
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot / (norm1 * norm2)
    
    def cosine_distance(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Compute cosine distance (1 - similarity).
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            float: Cosine distance (0.0-2.0, typically 0.0-1.0)
        """
        return 1.0 - self.cosine_similarity(vec1, vec2)


class EmergenceMonitor:
    """
    Graph-based anomaly detection for multi-agent swarms.
    
    This is the "Circuit Breaker" that detects when swarms go off the rails:
    - Infinite loops (agents approving each other in circles)
    - Echo chambers (agents repeating similar content)
    - Goal drift (semantic divergence from original intent)
    - Escalation spirals (agents keep deferring)
    
    Architecture Pattern:
    - Stateful: Maintains interaction_graph and embeddings
    - Incremental: check_step() processes one step at a time
    - Defensive: Safe fallbacks when networkx/numpy unavailable
    
    Integration with v1:
    - FailureTriage routes emergent anomalies here
    - Results in CIRCUIT_BREAK → immediate termination
    """
    
    def __init__(
        self,
        drift_threshold: float = 0.4,
        echo_threshold: float = 0.9,
        cycle_detection_enabled: bool = True
    ):
        """
        Initialize emergence monitor.
        
        Args:
            drift_threshold: Cosine distance threshold for goal drift (0.0-1.0)
            echo_threshold: Similarity threshold for echo chamber (0.0-1.0)
            cycle_detection_enabled: Whether to detect graph cycles
        """
        self.drift_threshold = drift_threshold
        self.echo_threshold = echo_threshold
        self.cycle_detection_enabled = cycle_detection_enabled and NETWORKX_AVAILABLE
        
        # State
        self.interaction_graph = nx.DiGraph() if NETWORKX_AVAILABLE else None
        self.embeddings = VectorStore()
        self.original_intent_embedding: Optional[List[float]] = None
        self.step_count = 0
        self.recent_contents: List[str] = []
        
        # Statistics
        self.anomalies_detected = 0
        self.cycles_detected = 0
        self.drift_detected = 0
        self.echo_chambers_detected = 0
        
        if not NETWORKX_AVAILABLE:
            logger.warning("networkx not available - cycle detection disabled")
        
        logger.info(
            f"EmergenceMonitor initialized (drift_threshold={drift_threshold}, "
            f"echo_threshold={echo_threshold})"
        )
    
    def initialize_trace(self, trace: SwarmTrace):
        """
        Initialize monitor with a new swarm trace.
        
        This must be called before check_step() to set the baseline
        for drift detection.
        
        Args:
            trace: The swarm trace with original intent
        """
        self.original_intent_embedding = self.embeddings.embed(trace.original_intent)
        self.step_count = 0
        self.recent_contents = []
        
        if NETWORKX_AVAILABLE:
            self.interaction_graph = nx.DiGraph()
        
        logger.info(
            f"Initialized trace monitoring: '{trace.original_intent[:50]}...'"
        )
    
    async def check_step(self, step: SwarmStep) -> AnomalyDecision:
        """
        Check a single swarm step for anomalies.
        
        This is the main entry point - call this for each step
        in the swarm interaction.
        
        Checks performed:
        1. Graph cycle detection (infinite loops)
        2. Semantic drift from original intent
        3. Echo chamber detection (repetitive content)
        4. Escalation spiral detection
        
        Args:
            step: The swarm step to analyze
            
        Returns:
            AnomalyDecision indicating safety or anomaly type
        """
        self.step_count += 1
        
        logger.debug(
            f"Checking step {self.step_count}: {step.source} → {step.target}"
        )
        
        # Update state
        self._update_graph(step)
        self.recent_contents.append(step.content)
        
        # Keep only last 10 messages for echo detection
        if len(self.recent_contents) > 10:
            self.recent_contents.pop(0)
        
        # Check 1: Cycle detection (infinite loops)
        if self.cycle_detection_enabled:
            cycle_result = self._detect_cycles()
            if cycle_result["has_cycle"]:
                self.cycles_detected += 1
                self.anomalies_detected += 1
                return AnomalyDecision(
                    is_anomaly=True,
                    type=AnomalyType.INFINITE_LOOP,
                    is_safe=False,
                    confidence=0.95,
                    reasoning=cycle_result["reasoning"],
                    suggested_action="CIRCUIT_BREAK",
                    cycle_detected=True
                )
        
        # Check 2: Goal drift (semantic divergence)
        if self.original_intent_embedding:
            drift_result = self._detect_drift(step)
            if drift_result["is_drift"]:
                self.drift_detected += 1
                self.anomalies_detected += 1
                return AnomalyDecision(
                    is_anomaly=True,
                    type=AnomalyType.GOAL_DRIFT,
                    is_safe=False,
                    confidence=drift_result["confidence"],
                    reasoning=drift_result["reasoning"],
                    suggested_action="TERMINATE_SWARM",
                    drift_score=drift_result["score"]
                )
        
        # Check 3: Echo chamber (repetitive content)
        echo_result = self._detect_echo_chamber()
        if echo_result["is_echo"]:
            self.echo_chambers_detected += 1
            self.anomalies_detected += 1
            return AnomalyDecision(
                is_anomaly=True,
                type=AnomalyType.ECHO_CHAMBER,
                is_safe=False,
                confidence=echo_result["confidence"],
                reasoning=echo_result["reasoning"],
                suggested_action="INJECT_DIVERSITY"
            )
        
        # Check 4: Escalation spiral (agents keep deferring)
        escalation_result = self._detect_escalation_spiral(step)
        if escalation_result["is_spiral"]:
            self.anomalies_detected += 1
            return AnomalyDecision(
                is_anomaly=True,
                type=AnomalyType.ESCALATION_SPIRAL,
                is_safe=False,
                confidence=escalation_result["confidence"],
                reasoning=escalation_result["reasoning"],
                suggested_action="FORCE_DECISION"
            )
        
        # All checks passed - safe
        return AnomalyDecision(
            is_anomaly=False,
            type=AnomalyType.SAFE,
            is_safe=True,
            confidence=0.85
        )
    
    def _update_graph(self, step: SwarmStep):
        """
        Update interaction graph with new step.
        
        Args:
            step: The swarm step
        """
        if not NETWORKX_AVAILABLE or self.interaction_graph is None:
            return
        
        # Add edge from source to target
        if self.interaction_graph.has_edge(step.source, step.target):
            # Increment weight for repeated interactions
            self.interaction_graph[step.source][step.target]["weight"] += 1
        else:
            self.interaction_graph.add_edge(
                step.source,
                step.target,
                weight=1,
                content=step.content
            )
    
    def _detect_cycles(self) -> Dict[str, Any]:
        """
        Detect cycles in interaction graph (infinite loops).
        
        This uses networkx's cycle detection to find circular dependencies
        like Agent A → Agent B → Agent A.
        
        Returns:
            dict: {"has_cycle": bool, "reasoning": str, "cycle": list}
        """
        if not NETWORKX_AVAILABLE or self.interaction_graph is None:
            return {"has_cycle": False, "reasoning": "Cycle detection unavailable"}
        
        try:
            # Find all simple cycles
            cycles = list(nx.simple_cycles(self.interaction_graph))
            
            if cycles:
                # Get the first cycle for reporting
                cycle = cycles[0]
                cycle_str = " → ".join(cycle)
                
                return {
                    "has_cycle": True,
                    "reasoning": f"Infinite loop detected: {cycle_str}. Agents are in circular approval pattern.",
                    "cycle": cycle
                }
            
            return {"has_cycle": False, "reasoning": "No cycles detected"}
            
        except Exception as e:
            logger.error(f"Error detecting cycles: {e}")
            return {"has_cycle": False, "reasoning": f"Cycle detection error: {e}"}
    
    def _detect_drift(self, step: SwarmStep) -> Dict[str, Any]:
        """
        Detect semantic drift from original intent.
        
        Compares current step content with original intent using
        cosine distance. High distance indicates the swarm has
        drifted off-topic.
        
        Args:
            step: The current swarm step
            
        Returns:
            dict: {"is_drift": bool, "score": float, "reasoning": str, "confidence": float}
        """
        if self.original_intent_embedding is None:
            return {"is_drift": False, "score": 0.0, "reasoning": "No baseline set"}
        
        # Embed current content
        current_embedding = step.semantic_embedding or self.embeddings.embed(step.content)
        
        # Compute distance from original intent
        drift_score = self.embeddings.cosine_distance(
            self.original_intent_embedding,
            current_embedding
        )
        
        is_drift = drift_score > self.drift_threshold
        
        if is_drift:
            return {
                "is_drift": True,
                "score": drift_score,
                "reasoning": (
                    f"Goal drift detected: semantic distance {drift_score:.2f} "
                    f"exceeds threshold {self.drift_threshold:.2f}. "
                    f"Swarm discussion has diverged from original intent."
                ),
                "confidence": min(0.7 + (drift_score - self.drift_threshold) / 0.6, 0.95)
            }
        
        return {
            "is_drift": False,
            "score": drift_score,
            "reasoning": f"Semantic distance {drift_score:.2f} within threshold",
            "confidence": 0.85
        }
    
    def _detect_echo_chamber(self) -> Dict[str, Any]:
        """
        Detect echo chambers (agents repeating similar content).
        
        Checks if recent messages have high semantic similarity,
        indicating agents are just echoing each other.
        
        Returns:
            dict: {"is_echo": bool, "reasoning": str, "confidence": float}
        """
        if len(self.recent_contents) < 3:
            # Need at least 3 messages to detect echo
            return {"is_echo": False, "reasoning": "Insufficient message history"}
        
        # Check last 3 messages for similarity
        recent = self.recent_contents[-3:]
        embeddings = [self.embeddings.embed(content) for content in recent]
        
        # Compute pairwise similarities
        similarities = []
        for i in range(len(embeddings) - 1):
            sim = self.embeddings.cosine_similarity(embeddings[i], embeddings[i+1])
            similarities.append(sim)
        
        avg_similarity = sum(similarities) / len(similarities)
        
        is_echo = avg_similarity > self.echo_threshold
        
        if is_echo:
            return {
                "is_echo": True,
                "reasoning": (
                    f"Echo chamber detected: agents repeating similar content "
                    f"(avg similarity {avg_similarity:.2f} > {self.echo_threshold:.2f}). "
                    f"Last 3 messages are semantically identical."
                ),
                "confidence": 0.85
            }
        
        return {
            "is_echo": False,
            "reasoning": f"Content diversity maintained (similarity {avg_similarity:.2f})",
            "confidence": 0.80
        }
    
    def _detect_escalation_spiral(self, step: SwarmStep) -> Dict[str, Any]:
        """
        Detect escalation spirals (agents keep deferring to each other).
        
        Looks for patterns like "Let me check with X" repeated multiple times.
        
        Args:
            step: The current swarm step
            
        Returns:
            dict: {"is_spiral": bool, "reasoning": str, "confidence": float}
        """
        content_lower = step.content.lower()
        
        # Deferral phrases
        deferral_phrases = [
            "let me check with",
            "i'll defer to",
            "asking",
            "escalating to",
            "need approval from",
            "waiting for",
            "after you",
            "your turn"
        ]
        
        has_deferral = any(phrase in content_lower for phrase in deferral_phrases)
        
        if not has_deferral:
            return {"is_spiral": False, "reasoning": "No deferral detected"}
        
        # Count deferrals in recent history
        deferral_count = sum(
            1 for content in self.recent_contents[-5:]
            if any(phrase in content.lower() for phrase in deferral_phrases)
        )
        
        is_spiral = deferral_count >= 3
        
        if is_spiral:
            return {
                "is_spiral": True,
                "reasoning": (
                    f"Escalation spiral detected: {deferral_count} deferrals in last 5 messages. "
                    f"Agents are passing responsibility back and forth without making progress."
                ),
                "confidence": 0.80
            }
        
        return {
            "is_spiral": False,
            "reasoning": f"Deferral count {deferral_count} within acceptable range",
            "confidence": 0.75
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get emergence monitoring statistics.
        
        Returns:
            dict: Statistics about detected anomalies
        """
        return {
            "steps_monitored": self.step_count,
            "anomalies_detected": self.anomalies_detected,
            "cycles_detected": self.cycles_detected,
            "drift_detected": self.drift_detected,
            "echo_chambers_detected": self.echo_chambers_detected,
            "drift_threshold": self.drift_threshold,
            "echo_threshold": self.echo_threshold,
            "cycle_detection_enabled": self.cycle_detection_enabled
        }
    
    def reset(self):
        """Reset monitor state for new trace."""
        if NETWORKX_AVAILABLE:
            self.interaction_graph = nx.DiGraph()
        self.original_intent_embedding = None
        self.step_count = 0
        self.recent_contents = []


# Integration with v1 Triage
def triage_anomaly(anomaly: AnomalyDecision) -> str:
    """
    Route anomaly to appropriate handling strategy.
    
    This bridges v2 EmergenceMonitor with v1 FailureTriage.
    
    Args:
        anomaly: The anomaly decision
        
    Returns:
        str: Triage decision (CIRCUIT_BREAK, RETRY, CONTINUE)
    """
    if not anomaly.is_anomaly:
        return "CONTINUE"
    
    # Critical anomalies → immediate circuit break
    critical_types = [
        AnomalyType.INFINITE_LOOP,
        AnomalyType.GOAL_DRIFT
    ]
    
    if anomaly.type in critical_types:
        return "CIRCUIT_BREAK"
    
    # Recoverable anomalies → retry with intervention
    if anomaly.type == AnomalyType.ECHO_CHAMBER:
        return "INJECT_DIVERSITY"
    
    if anomaly.type == AnomalyType.ESCALATION_SPIRAL:
        return "FORCE_DECISION"
    
    return "CONTINUE"
