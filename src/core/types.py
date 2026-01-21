"""
Data types for the Cross-Model Verification Kernel.
These classes define the core data structures used throughout the system.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime


class NodeStatus(Enum):
    """Status of a node in the Graph of Truth."""
    PENDING = "pending"
    VERIFIED = "verified"
    FAILED = "failed"
    IN_PROGRESS = "in_progress"


class VerificationOutcome(Enum):
    """Result of verification process."""
    PASS = "pass"
    FAIL = "fail"
    UNCERTAIN = "uncertain"


@dataclass
class VerificationResult:
    """Result of a verification check by the Adversary."""
    outcome: VerificationOutcome
    confidence: float  # 0.0 to 1.0
    critical_issues: List[str] = field(default_factory=list)
    logic_flaws: List[str] = field(default_factory=list)
    missing_edge_cases: List[str] = field(default_factory=list)
    test_coverage_gaps: List[str] = field(default_factory=list)
    minor_issues: List[str] = field(default_factory=list)
    reasoning: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    # Prosecutor Mode: Generated hostile test cases
    hostile_tests: List[str] = field(default_factory=list)
    hostile_test_results: Dict[str, Any] = field(default_factory=dict)
    
    def has_critical_issues(self) -> bool:
        """Check if there are any critical issues."""
        return len(self.critical_issues) > 0 or len(self.logic_flaws) > 0


@dataclass
class GenerationResult:
    """Result of code generation by the Generator."""
    solution: str
    explanation: str
    test_cases: str
    edge_cases: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Node:
    """A node in the Graph of Truth representing a piece of verified knowledge."""
    id: str
    content: str
    status: NodeStatus
    verification_results: List[VerificationResult] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    parent_id: Optional[str] = None
    children_ids: List[str] = field(default_factory=list)
    
    def is_verified(self) -> bool:
        """Check if this node has been successfully verified."""
        return self.status == NodeStatus.VERIFIED


@dataclass
class KernelState:
    """Current state of the kernel execution."""
    task_description: str
    current_loop: int
    max_loops: int
    current_solution: Optional[GenerationResult] = None
    verification_history: List[VerificationResult] = field(default_factory=list)
    graph_nodes: List[Node] = field(default_factory=list)
    is_complete: bool = False
    final_result: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
