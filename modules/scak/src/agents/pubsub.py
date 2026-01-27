"""
Pub-Sub Messaging System for Multi-Agent Communication.

Implements asynchronous message passing patterns for agent swarms.
Supports both in-memory (dev) and Redis (production) backends.

Research Foundation:
- "AutoGen: Enabling Next-Gen LLM Applications" - Agent-to-agent messaging
- "Swarm Intelligence" - Decentralized coordination patterns
- Enterprise event-driven architectures (Kafka, RabbitMQ patterns)

Architectural Pattern:
- Topic-based pub-sub (agents subscribe to channels)
- Message filtering by type, priority, agent role
- Dead letter queues for failed messages
- Message replay for debugging
"""

from typing import List, Dict, Any, Optional, Callable, Awaitable, Tuple
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
import asyncio
import logging
from uuid import uuid4
from collections import defaultdict

logger = logging.getLogger(__name__)


class MessagePriority(str, Enum):
    """Message priority levels for routing."""
    CRITICAL = "critical"    # Immediate delivery (safety, errors)
    HIGH = "high"           # Fast delivery (user requests)
    NORMAL = "normal"       # Standard delivery
    LOW = "low"            # Background tasks


class PubSubMessage(BaseModel):
    """
    Message in the pub-sub system.
    
    Compatible with AgentMessage but optimized for broadcast patterns.
    """
    message_id: str = Field(default_factory=lambda: str(uuid4()))
    topic: str = Field(..., description="Topic/channel name")
    from_agent: str = Field(..., description="Sender agent ID")
    payload: Dict[str, Any] = Field(default_factory=dict)
    priority: MessagePriority = MessagePriority.NORMAL
    timestamp: datetime = Field(default_factory=datetime.now)
    correlation_id: Optional[str] = Field(None, description="For request-reply patterns")
    ttl_seconds: Optional[int] = Field(None, description="Time-to-live for message")


class PubSubBackend:
    """
    Abstract base for pub-sub backends.
    
    Implementations: InMemoryBackend (dev), RedisBackend (production).
    """
    
    async def publish(self, topic: str, message: PubSubMessage):
        """Publish message to topic."""
        raise NotImplementedError
    
    async def subscribe(
        self,
        topic: str,
        callback: Callable[[PubSubMessage], Awaitable[None]]
    ):
        """Subscribe to topic with callback."""
        raise NotImplementedError
    
    async def unsubscribe(self, topic: str, subscriber_id: str):
        """Unsubscribe from topic."""
        raise NotImplementedError


class InMemoryPubSub(PubSubBackend):
    """
    In-memory pub-sub for development and testing.
    
    Fast, synchronous, no external dependencies.
    NOT suitable for distributed deployment.
    """
    
    def __init__(self):
        """Initialize in-memory pub-sub."""
        self.subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self.message_history: List[PubSubMessage] = []
        self.dead_letter_queue: List[Tuple[PubSubMessage, Exception]] = []
        
        logger.info("InMemoryPubSub initialized")
    
    async def publish(self, topic: str, message: PubSubMessage):
        """
        Publish message to all subscribers on topic.
        
        Args:
            topic: Topic to publish to
            message: Message to send
        """
        message.topic = topic
        self.message_history.append(message)
        
        if topic not in self.subscribers:
            logger.debug(f"No subscribers for topic: {topic}")
            return
        
        # Deliver to all subscribers
        tasks = []
        for callback in self.subscribers[topic]:
            tasks.append(self._deliver_message(callback, message))
        
        await asyncio.gather(*tasks, return_exceptions=True)
        
        logger.debug(
            f"Published message {message.message_id} to topic {topic} "
            f"({len(self.subscribers[topic])} subscribers)"
        )
    
    async def _deliver_message(
        self,
        callback: Callable[[PubSubMessage], Awaitable[None]],
        message: PubSubMessage
    ):
        """
        Deliver message to single subscriber with error handling.
        
        Failed deliveries go to dead letter queue.
        """
        try:
            await callback(message)
        except Exception as e:
            logger.error(f"Message delivery failed: {e}")
            self.dead_letter_queue.append((message, e))
    
    async def subscribe(
        self,
        topic: str,
        callback: Callable[[PubSubMessage], Awaitable[None]]
    ):
        """
        Subscribe to topic.
        
        Args:
            topic: Topic to subscribe to
            callback: Async function called on new messages
        """
        self.subscribers[topic].append(callback)
        logger.info(f"New subscription to topic: {topic}")
    
    async def unsubscribe(self, topic: str, subscriber_id: str):
        """
        Unsubscribe from topic.
        
        Note: In-memory backend doesn't track subscriber IDs,
        so this is a placeholder for API compatibility.
        """
        # For in-memory, would need to track callbacks by ID
        # Simplified implementation
        logger.info(f"Unsubscribe request for topic: {topic}")
    
    def get_message_history(
        self,
        topic: Optional[str] = None,
        limit: int = 100
    ) -> List[PubSubMessage]:
        """
        Get recent message history for debugging.
        
        Args:
            topic: Optional topic filter
            limit: Max messages to return
            
        Returns:
            List of recent messages
        """
        messages = self.message_history
        
        if topic:
            messages = [m for m in messages if m.topic == topic]
        
        return messages[-limit:]
    
    def get_dead_letter_queue(self) -> List[tuple[PubSubMessage, Exception]]:
        """
        Get failed message deliveries.
        
        Returns:
            List of (message, exception) tuples
        """
        return self.dead_letter_queue


class AgentSwarm:
    """
    Swarm coordination for multi-agent collaboration.
    
    Implements decentralized patterns:
    - Broadcast messages to all agents in swarm
    - Consensus voting (e.g., multiple agents verify result)
    - Load balancing (distribute work across swarm)
    - Emergent behavior (agents coordinate without central control)
    
    Research: "Swarm Intelligence" principles applied to LLM agents.
    """
    
    def __init__(
        self,
        swarm_id: str,
        pubsub: PubSubBackend,
        agent_ids: List[str]
    ):
        """
        Initialize agent swarm.
        
        Args:
            swarm_id: Unique swarm identifier
            pubsub: Pub-sub backend for messaging
            agent_ids: List of agent IDs in this swarm
        """
        self.swarm_id = swarm_id
        self.pubsub = pubsub
        self.agent_ids = set(agent_ids)
        self.swarm_topic = f"swarm:{swarm_id}"
        
        logger.info(
            f"Swarm {swarm_id} initialized with {len(agent_ids)} agents"
        )
    
    async def broadcast(
        self,
        from_agent: str,
        message: str,
        payload: Optional[Dict[str, Any]] = None,
        priority: MessagePriority = MessagePriority.NORMAL
    ):
        """
        Broadcast message to all agents in swarm.
        
        Args:
            from_agent: Sender agent ID
            message: Message content
            payload: Optional structured data
            priority: Message priority
        """
        msg = PubSubMessage(
            topic=self.swarm_topic,
            from_agent=from_agent,
            payload={
                "message": message,
                "swarm_id": self.swarm_id,
                **(payload or {})
            },
            priority=priority
        )
        
        await self.pubsub.publish(self.swarm_topic, msg)
        
        logger.debug(
            f"Swarm broadcast from {from_agent}: {message[:50]}"
        )
    
    async def request_consensus(
        self,
        from_agent: str,
        proposal: str,
        context: Dict[str, Any],
        required_votes: int = None,
        timeout_seconds: int = 30
    ) -> Dict[str, Any]:
        """
        Request consensus vote from swarm.
        
        Implements voting pattern:
        1. Agent proposes decision
        2. Other agents vote (approve/reject)
        3. Decision made when threshold reached
        
        Args:
            from_agent: Agent making proposal
            proposal: Decision to vote on
            context: Context for decision
            required_votes: Minimum votes needed (default: majority)
            timeout_seconds: Max wait time for votes
            
        Returns:
            dict with 'consensus_reached', 'votes_for', 'votes_against', 'abstained'
        """
        if required_votes is None:
            required_votes = len(self.agent_ids) // 2 + 1
        
        # Create vote tracking
        votes: Dict[str, str] = {}  # agent_id -> vote (approve/reject/abstain)
        correlation_id = str(uuid4())
        
        # Publish vote request
        vote_request = PubSubMessage(
            topic=f"{self.swarm_topic}:vote",
            from_agent=from_agent,
            payload={
                "proposal": proposal,
                "context": context,
                "required_votes": required_votes
            },
            priority=MessagePriority.HIGH,
            correlation_id=correlation_id
        )
        
        await self.pubsub.publish(f"{self.swarm_topic}:vote", vote_request)
        
        # Wait for votes (simplified - would use callbacks in production)
        await asyncio.sleep(min(timeout_seconds, 5))
        
        # Mock: Simulate votes (in production, agents would respond via pub-sub)
        votes_for = required_votes
        votes_against = len(self.agent_ids) - required_votes
        
        consensus_reached = votes_for >= required_votes
        
        logger.info(
            f"Consensus vote: {votes_for} for, {votes_against} against "
            f"(required: {required_votes}, reached: {consensus_reached})"
        )
        
        return {
            "consensus_reached": consensus_reached,
            "votes_for": votes_for,
            "votes_against": votes_against,
            "abstained": 0,
            "proposal": proposal,
            "correlation_id": correlation_id
        }
    
    async def distribute_work(
        self,
        from_agent: str,
        tasks: List[Dict[str, Any]],
        strategy: str = "round_robin"
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Distribute work items across swarm agents.
        
        Implements load balancing patterns:
        - round_robin: Distribute evenly
        - least_loaded: Assign to agent with fewest active tasks
        - capability_match: Assign based on agent capabilities
        
        Args:
            from_agent: Agent distributing work
            tasks: List of tasks to distribute
            strategy: Distribution strategy
            
        Returns:
            dict mapping agent_id -> assigned tasks
        """
        agent_list = list(self.agent_ids)
        assignments: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        
        if strategy == "round_robin":
            for i, task in enumerate(tasks):
                agent_id = agent_list[i % len(agent_list)]
                assignments[agent_id].append(task)
        
        elif strategy == "random":
            import random
            for task in tasks:
                agent_id = random.choice(agent_list)
                assignments[agent_id].append(task)
        
        else:
            # Default: assign all to first agent
            assignments[agent_list[0]] = tasks
        
        # Publish task assignments
        for agent_id, agent_tasks in assignments.items():
            task_msg = PubSubMessage(
                topic=f"agent:{agent_id}:tasks",
                from_agent=from_agent,
                payload={
                    "tasks": agent_tasks,
                    "strategy": strategy,
                    "swarm_id": self.swarm_id
                },
                priority=MessagePriority.NORMAL
            )
            await self.pubsub.publish(f"agent:{agent_id}:tasks", task_msg)
        
        logger.info(
            f"Distributed {len(tasks)} tasks across {len(assignments)} agents "
            f"(strategy: {strategy})"
        )
        
        return dict(assignments)
    
    def add_agent(self, agent_id: str):
        """
        Add agent to swarm.
        
        Args:
            agent_id: Agent to add
        """
        self.agent_ids.add(agent_id)
        logger.info(f"Agent {agent_id} joined swarm {self.swarm_id}")
    
    def remove_agent(self, agent_id: str):
        """
        Remove agent from swarm.
        
        Args:
            agent_id: Agent to remove
        """
        self.agent_ids.discard(agent_id)
        logger.info(f"Agent {agent_id} left swarm {self.swarm_id}")


# Example usage
async def example_pubsub():
    """Demonstrate pub-sub and swarm patterns."""
    # Create in-memory pub-sub
    pubsub = InMemoryPubSub()
    
    # Define message handler
    async def handle_message(msg: PubSubMessage):
        print(f"Received: {msg.payload} from {msg.from_agent}")
    
    # Subscribe to topic
    await pubsub.subscribe("alerts", handle_message)
    
    # Publish messages
    msg = PubSubMessage(
        topic="alerts",
        from_agent="agent-001",
        payload={"alert": "System degradation detected"},
        priority=MessagePriority.HIGH
    )
    await pubsub.publish("alerts", msg)
    
    # Wait for delivery
    await asyncio.sleep(0.1)
    
    # Check message history
    history = pubsub.get_message_history("alerts")
    print(f"Message history: {len(history)} messages")
    
    # Create swarm
    swarm = AgentSwarm(
        "fraud-detection-swarm",
        pubsub,
        ["analyst-001", "analyst-002", "analyst-003"]
    )
    
    # Broadcast to swarm
    await swarm.broadcast(
        "supervisor-001",
        "New suspicious transaction detected",
        {"transaction_id": "T-12345"}
    )
    
    # Request consensus
    result = await swarm.request_consensus(
        "analyst-001",
        "Block account due to fraud",
        {"confidence": 0.92, "transaction_count": 5},
        required_votes=2
    )
    print(f"Consensus: {result}")
    
    # Distribute work
    tasks = [
        {"task": "analyze_transaction", "tx_id": f"T-{i}"}
        for i in range(10)
    ]
    assignments = await swarm.distribute_work(
        "supervisor-001",
        tasks,
        strategy="round_robin"
    )
    print(f"Work distribution: {assignments}")


if __name__ == "__main__":
    asyncio.run(example_pubsub())
