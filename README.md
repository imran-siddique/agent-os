# Self-Evolving Agent POC

A proof-of-concept implementation of a self-evolving AI agent that improves its own system instructions based on performance feedback.

## Overview

This agent implements two modes of operation:

### Decoupled Mode (Recommended)
Separates execution from learning for low-latency operation:

1. **Doer (Synchronous)**: Executes tasks with read-only access to wisdom database, emits telemetry
2. **Observer (Asynchronous)**: Offline learning process that analyzes telemetry and updates wisdom

### Legacy Mode (Synchronous)
Traditional self-improvement loop for backward compatibility:

1. **Memory**: System instructions stored in JSON
2. **Task**: Agent receives a query
3. **Act**: Agent attempts to solve using available tools
4. **Reflect**: Separate LLM evaluates the output (returns score 0-1 and critique)
5. **Evolve**: If score < 0.8, a third LLM rewrites system instructions
6. **Retry**: Agent runs again with improved instructions

## Features

- **Silent Signals**: Implicit feedback mechanism that captures user friction
  - **Undo Signal** (Critical Failure): User reverses agent action (Ctrl+Z, revert) 
  - **Abandonment Signal** (Loss): User stops responding mid-workflow
  - **Acceptance Signal** (Success): User moves to next task without follow-up
  - Eliminates blind spot of relying solely on explicit feedback
  - Learns from what users DO, not just what they SAY
  - See [SILENT_SIGNALS.md](SILENT_SIGNALS.md) for detailed documentation
- **Decoupled Execution/Learning**: Low-latency execution with offline learning
- **Upgrade Purge Strategy**: Active lifecycle management for wisdom database
  - Automatically removes lessons when upgrading models
  - Keeps database lean and specialized
  - Treats wisdom like a high-performance cache
- **Prioritization Framework**: Graph RAG-inspired three-layer context ranking system
  - Safety Layer: Prevents repeating recent failures
  - Personalization Layer: User-specific preferences and constraints
  - Global Wisdom Layer: Generic best practices
- **Telemetry System**: Event stream for capturing execution traces
- **Wisdom Database**: Persistent knowledge stored in `system_instructions.json`
- **Tool System**: Simple tools for calculations, time, and string operations
- **Reflection System**: Automatic evaluation of agent responses
- **Evolution System**: Automatic improvement of system instructions
- **Backward Compatible**: Legacy synchronous mode still available

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

## Usage

### Decoupled Architecture (Recommended)

Run the decoupled example:
```bash
python example_decoupled.py
```

This demonstrates:
1. DoerAgent executing tasks (fast, synchronous)
2. ObserverAgent learning offline (asynchronous)

Manual usage:

```python
from agent import DoerAgent
from observer import ObserverAgent

# Phase 1: Execute tasks (fast, no learning)
doer = DoerAgent()
result = doer.run("What is 10 + 20?")

# Phase 2: Learn offline (separate process)
observer = ObserverAgent()
observer.process_events()  # Batch process telemetry
```

### Silent Signals

Run the silent signals demo:
```bash
python example_silent_signals.py
```

This demonstrates the three types of implicit feedback signals:
1. **Undo Signal**: User reverses agent action (critical failure)
2. **Abandonment Signal**: User stops responding mid-workflow (loss)
3. **Acceptance Signal**: User moves to next task without follow-up (success)

Manual usage:

```python
from agent import DoerAgent

doer = DoerAgent()

# Emit an undo signal when user reverses action
doer.emit_undo_signal(
    query="Write code to delete files",
    agent_response="rm -rf /*",
    undo_action="Ctrl+Z in editor",
    user_id="user123"
)

# Emit an abandonment signal when user stops responding
doer.emit_abandonment_signal(
    query="Help me debug",
    agent_response="Check your code",
    interaction_count=3,
    user_id="user456"
)

# Emit an acceptance signal when user moves on
doer.emit_acceptance_signal(
    query="Calculate 10 + 20",
    agent_response="Result is 30",
    next_task="Calculate 20 + 30",
    user_id="user789"
)
```

### Legacy Synchronous Mode

Run the basic example:
```bash
python example.py
```

Run the full demo:
```bash
python agent.py
```

Custom usage:

```python
from agent import SelfEvolvingAgent

# Initialize agent
agent = SelfEvolvingAgent(
    memory_file="system_instructions.json",
    score_threshold=0.8,
    max_retries=3
)

# Run a query
results = agent.run("What is 10 + 20?", verbose=True)

print(f"Success: {results['success']}")
print(f"Final Score: {results['final_score']}")
print(f"Response: {results['final_response']}")
```

## Architecture

### Decoupled Mode Components

1. **DoerAgent**: Synchronous execution agent
   - Executes tasks using wisdom database (read-only)
   - Emits telemetry events to event stream
   - No reflection or learning during execution
   - Low latency operation

2. **ObserverAgent**: Asynchronous learning agent
   - Consumes telemetry events offline
   - Analyzes execution traces
   - Performs reflection and evaluation
   - Evolves wisdom database
   - Can use more powerful models

3. **EventStream**: Telemetry system
   - Append-only event log (JSONL format)
   - Stores execution traces
   - Supports batch processing
   - Checkpoint-based progress tracking

4. **MemorySystem/Wisdom Database**: Persistent knowledge
   - Stores system instructions in JSON
   - Version tracking
   - Improvement history

5. **AgentTools**: Simple tools the agent can use
   - `calculate()`: Mathematical expressions
   - `get_current_time()`: Current date/time
   - `string_length()`: String length calculation

### Legacy Mode Components

1. **SelfEvolvingAgent**: Main agent with evolution loop
   - `act()`: Execute query with current instructions
   - `reflect()`: Evaluate response quality
   - `evolve()`: Improve instructions based on critique
   - `run()`: Main loop orchestrating all steps

## Key Benefits of Decoupled Architecture

1. **Low Runtime Latency**: Doer doesn't wait for learning
2. **Persistent Learning**: Observer builds wisdom over time
3. **Scalability**: Observer can process events in batch
4. **Model Flexibility**: Use different/more powerful models for learning
5. **Async Processing**: Learning happens offline, separate from execution
6. **Resource Efficiency**: Learning process can be scheduled independently
7. **Context Prioritization**: Critical information (safety, user prefs) is highly visible

## Prioritization Framework

The system now includes a three-layer prioritization framework that sits between the database and agent:

1. **Safety Layer (Highest Priority)**: "Have we failed at this exact task recently?"
   - Injects corrections with high urgency
   - Prevents repeating past mistakes
   - Time-windowed (7 days default)

2. **Personalization Layer (Medium Priority)**: "Does this specific user have preferred constraints?"
   - User-specific preferences (e.g., "Always use JSON output")
   - Learned from feedback
   - Priority-ranked

3. **Global Wisdom Layer (Low Priority)**: "What is the generic best practice?"
   - Base system instructions
   - Generic best practices

**Try it:**
```bash
# Run prioritization demo
python example_prioritization.py

# Test prioritization framework
python test_prioritization.py
```

See [PRIORITIZATION_FRAMEWORK.md](PRIORITIZATION_FRAMEWORK.md) for detailed documentation.

## Upgrade Purge Strategy

The system includes active lifecycle management for the wisdom database. When you upgrade your base model (e.g., GPT-3.5 → GPT-4), many lessons become redundant as the new model can handle them natively.

**The Process:**
1. **Audit**: Test old failure scenarios against the new model
2. **Identify**: Mark lessons the new model solves natively
3. **Purge**: Automatically remove redundant lessons
4. **Result**: Leaner, more specialized wisdom database

**Try it:**
```bash
# Run upgrade purge demo
python example_upgrade_purge.py

# Test upgrade functionality
python test_model_upgrade.py
```

**Usage:**
```python
from model_upgrade import ModelUpgradeManager

manager = ModelUpgradeManager()
report = manager.perform_upgrade(
    new_model="gpt-4o",
    baseline_instructions="Your baseline system prompt...",
    score_threshold=0.8,
    auto_purge=True
)
```

See [UPGRADE_PURGE.md](UPGRADE_PURGE.md) for detailed documentation.

## Testing

Run all tests:
```bash
# Test legacy components
python test_agent.py

# Test decoupled architecture
python test_decoupled.py

# Test prioritization framework
python test_prioritization.py

# Test upgrade purge strategy
python test_model_upgrade.py

# Test silent signals feature
python test_silent_signals.py
```

### Configuration

Environment variables (in `.env`):
- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `AGENT_MODEL`: Model for agent (default: gpt-4o-mini)
- `REFLECTION_MODEL`: Model for reflection (default: gpt-4o-mini)
- `EVOLUTION_MODEL`: Model for evolution (default: gpt-4o-mini)
- `SCORE_THRESHOLD`: Minimum acceptable score (default: 0.8)
- `MAX_RETRIES`: Maximum retry attempts (default: 3)

## Example Output

```
ATTEMPT 1/3
Current Instructions Version: 1
[ACTING] Processing query...
Agent Response: To calculate 15 * 24 + 100...
[REFLECTING] Evaluating response...
Score: 0.6
Critique: The agent did not clearly identify the calculator tool...
[EVOLVING] Score 0.6 below threshold 0.8
Rewriting system instructions...

ATTEMPT 2/3
[ACTING] Processing query...
Agent Response: I will use the calculate() tool...
[REFLECTING] Evaluating response...
Score: 0.9
[SUCCESS] Score 0.9 meets threshold 0.8
```

## System Instructions

The `system_instructions.json` file evolves over time:

```json
{
  "version": 2,
  "instructions": "You are a helpful AI assistant...",
  "improvements": [
    {
      "version": 2,
      "timestamp": "2024-01-01T12:00:00",
      "critique": "Agent should explicitly mention tool usage..."
    }
  ]
}
```

## License

MIT
