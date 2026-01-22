# Feature 3: The Witness (Traceability)

## Overview

Feature 3 implements comprehensive traceability for the Cross-Model Verification Kernel. This feature logs the entire debate between the Generator and Verifier, creating a clean JSON artifact suitable for research papers and supplementary materials.

## Key Components

### 1. TraceLogger (`src/core/trace_logger.py`)

The `TraceLogger` class serializes the complete `NodeState` (including history, forbidden strategies, and feedback) into structured JSON files.

**Features:**
- Automatic directory creation (`logs/traces/` by default)
- JSON serialization of dataclasses using `asdict()`
- Metadata generation (timestamp, attempt count, final status)
- Clean, readable output with proper encoding

**Usage:**
```python
from src.core.trace_logger import TraceLogger
from src.core.types import NodeState

logger = TraceLogger(log_dir="logs/traces")
state = NodeState(input_query="Your problem here")
# ... populate state with history ...
filepath = logger.save_trace("experiment_01", state)
```

### 2. SimpleVerificationKernel (`src/simple_kernel.py`)

A simplified kernel implementation designed specifically for research experiments. It provides:
- Direct `solve()` method interface
- Integration with `NodeState` tracking
- Automatic trace logging at completion
- Strategy detection and banning (Feature 2)

**Usage:**
```python
from src.simple_kernel import SimpleVerificationKernel

kernel = SimpleVerificationKernel(max_retries=5)
solution = kernel.solve(
    query="Write a function to merge sorted arrays",
    run_id="experiment_001"
)
# Trace is automatically saved to logs/traces/experiment_001_<timestamp>.json
```

### 3. Paper Data Generator (`experiments/paper_data_generator.py`)

An experiment runner that compares:
1. **Baseline**: Single agent (OpenAI) without verification
2. **CMVK**: Full Cross-Model Verification Kernel with traceability

**Running the Experiment:**
```bash
cd /path/to/cross-model-verification-kernel
python experiments/paper_data_generator.py
```

**Output:**
- Baseline solutions: `logs/baseline_*.py`
- CMVK traces: `logs/traces/cmvk_*.json`

### 4. Enhanced VerificationKernel

The main `VerificationKernel` (`src/core/kernel.py`) now supports optional trace logging:

```python
from src.core.kernel import VerificationKernel
from src.agents.generator_openai import OpenAIGenerator
from src.agents.verifier_gemini import GeminiVerifier

kernel = VerificationKernel(
    generator=OpenAIGenerator(),
    verifier=GeminiVerifier(),
    enable_trace_logging=True  # Enable traceability
)
```

## Trace File Format

Each trace file contains:

```json
{
  "input_query": "The original problem statement",
  "current_code": "The final solution code (if found)",
  "status": "verified|rejected|pending",
  "history": [
    {
      "step_id": 1,
      "code_generated": "First attempt code",
      "verifier_feedback": "Feedback from verifier",
      "status": "success|failed",
      "strategy_used": "recursive|iterative|numpy|..."
    }
  ],
  "forbidden_strategies": ["strategies", "that", "failed"],
  "meta": {
    "timestamp": "20260121-182813",
    "total_attempts": 3,
    "final_status": "solved|failed"
  }
}
```

## Benefits for Research

1. **Reproducibility**: Complete record of every generation-verification iteration
2. **Analysis**: Track which strategies were tried and why they failed
3. **Visualization**: Data ready for charts and graphs
4. **Supplementary Material**: Professional JSON artifacts for paper submission
5. **Debugging**: Full audit trail for understanding system behavior

## Testing

Run the test suite:
```bash
python tests/test_trace_logger.py
```

Tests cover:
- Basic trace logging functionality
- Failed state handling
- JSON structure validation
- Metadata generation

## Integration with Features 1 & 2

- **Feature 1 (Generator ↔ Verifier Loop)**: Traces capture each iteration
- **Feature 2 (Lateral Thinking)**: Forbidden strategies are logged in traces
- **Feature 3 (Traceability)**: This feature - complete audit trail

## Next Steps

As mentioned in the problem statement, you can now:

1. **Visualize the Traces**: Create a script to replay the debate
2. **Scale the Experiment**: Load HumanEval dataset (164 problems)
3. **Draft the Paper**: Use traces to write the Methodology section

## File Locations

- **TraceLogger**: `src/core/trace_logger.py`
- **SimpleKernel**: `src/simple_kernel.py`
- **Experiment**: `experiments/paper_data_generator.py`
- **Tests**: `tests/test_trace_logger.py`
- **Traces**: `logs/traces/` (gitignored)
