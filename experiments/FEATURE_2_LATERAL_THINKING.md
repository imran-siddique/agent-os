# Feature 2: Lateral Thinking (Graph Branching) - Documentation

## Overview

Feature 2 transforms the kernel from a simple **retry loop** to a **strategy tree** that prevents getting stuck in the same failed approach.

## Key Concept

**Problem:** Traditional retry loops often fail by repeatedly trying the same approach with minor tweaks (e.g., just renaming variables).

**Solution:** Lateral Thinking tracks failures and explicitly bans failed strategies, forcing the generator to explore fundamentally different approaches.

## Implementation

### 1. Memory Structure (`src/core/types.py`)

Added two new dataclasses to track execution history:

#### `ExecutionTrace`
Records a single execution attempt in the verification loop.
```python
@dataclass
class ExecutionTrace:
    step_id: int
    code_generated: str
    verifier_feedback: str
    status: str  # "success" or "failed"
    strategy_used: Optional[str] = None  # e.g. "recursive", "iterative"
```

#### `NodeState`
Tracks the complete state of a problem-solving node.
```python
@dataclass
class NodeState:
    input_query: str
    current_code: Optional[str] = None
    status: str = "pending"  # pending, verified, rejected
    history: List[ExecutionTrace] = field(default_factory=list)
    forbidden_strategies: List[str] = field(default_factory=list)

    @property
    def fail_count(self) -> int:
        return len([t for t in self.history if t.status == "failed"])
```

### 2. Generator Enhancement (`src/agents/generator_openai.py`)

Added `generate_solution()` method that accepts forbidden strategies:

```python
def generate_solution(
    self,
    query: str,
    context: Optional[str] = None,
    forbidden_strategies: Optional[List[str]] = None
) -> str:
    """
    Generate a solution with optional constraints.

    If forbidden_strategies is provided, the generator is explicitly told:
    "DO NOT USE: [recursive, brute_force, ...]"
    "You MUST choose a fundamentally different algorithmic approach."
    """
```

### 3. Kernel Brain (`src/core/kernel.py`)

The kernel already has lateral thinking logic in `graph_memory.py`. Added helper method:

```python
def _format_history(self, history: List[VerificationResult]) -> str:
    """
    Helper to summarize previous failures for the Generator.
    Formats critical issues, logic flaws, and feedback.
    """
```

## How It Works

### The Flow

1. **Attempt 1:** Generator writes code using approach A (e.g., recursion)
2. **Verification fails:** Verifier identifies critical issues
3. **Kernel records failure:** `graph.record_approach_failure(solution, task)`
4. **Attempt 2:** Same approach A fails again
5. **Branching triggered:** Kernel detects repeated failure
6. **Strategy banned:** Approach A added to `forbidden_approaches`
7. **Generator constrained:** Next generation receives `forbidden_strategies=['recursive']`
8. **Attempt 3:** Generator MUST use different approach (e.g., iterative)

### Example Scenario

**Query:** "Calculate the factorial of a number. Ensure it handles stack overflow risks for large inputs."

**Round 1:**
```python
# Generator produces:
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n-1)

# Verifier: FAIL - RecursionError for factorial(10000)
```

**Round 2:**
```python
# Same recursive approach with tweaks
def factorial(n):
    if n == 0:
        return 1
    return n * factorial(n-1)

# Verifier: FAIL - Still RecursionError
# Kernel: Ban "recursive" approach
```

**Round 3:**
```python
# Generator forced to use different approach
def factorial(n):
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result

# Verifier: PASS - Handles large inputs ✅
```

## Running the Experiment

### Option 1: Run the experiment script
```bash
cd experiments
python test_lateral_thinking.py
```

### Option 2: Run tests
```bash
pytest tests/test_lateral_thinking_witness.py -v
pytest tests/test_lateral_thinking_integration.py -v
```

## Architecture Integration

The feature integrates with existing components:

- **GraphMemory** (`src/core/graph_memory.py`): Tracks approach failures, detects patterns
- **VerificationKernel** (`src/core/kernel.py`): Orchestrates the branching logic
- **Agents** (`src/agents/`): Generator accepts constraints, Verifier identifies issues

## Statistics Tracking

The kernel tracks lateral thinking metrics:

```python
stats = kernel.get_graph_stats()
# Returns:
# {
#     "approach_failures": 2,        # Number of failed approach attempts
#     "forbidden_approaches": 1,     # Number of banned strategies
#     "conversation_entries": 5      # Full trace of all interactions
# }
```

## Benefits

1. **Prevents Stochastic Loops:** No more "trying the same thing and hoping for different results"
2. **Forced Innovation:** Explicitly requires different algorithmic approaches
3. **Transparent Reasoning:** Full trace of why each approach was tried/banned
4. **Efficiency:** Avoids wasting API calls on the same failed strategy

## Next Steps

Consider implementing:
- Feature 3: Witness (Traceability) - already partially implemented
- Strategy suggestion system based on banned approaches
- Multi-dimensional strategy banning (e.g., ban "recursive + no memoization")
- LLM-based strategy extraction (more sophisticated than keyword matching)

## Testing

All tests pass:
- 11 tests for Lateral Thinking in `test_lateral_thinking_witness.py`
- 9 tests for integration in `test_lateral_thinking_integration.py`
- Total: 60 tests pass across the entire test suite
