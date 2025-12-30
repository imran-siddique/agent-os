# Self-Evolving Agent POC

A proof-of-concept implementation of a self-evolving AI agent that improves its own system instructions based on performance feedback.

## Overview

This agent implements a self-improvement loop:

1. **Memory**: System instructions stored in JSON
2. **Task**: Agent receives a query
3. **Act**: Agent attempts to solve using available tools
4. **Reflect**: Separate LLM evaluates the output (returns score 0-1 and critique)
5. **Evolve**: If score < 0.8, a third LLM rewrites system instructions
6. **Retry**: Agent runs again with improved instructions

## Features

- **JSON-based Memory**: System instructions stored in `system_instructions.json`
- **Tool System**: Simple tools for calculations, time, and string operations
- **Reflection System**: Automatic evaluation of agent responses
- **Evolution System**: Automatic improvement of system instructions
- **Retry Logic**: Up to 3 attempts with evolving instructions

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

### Simple Example

Run the basic example:
```bash
python example.py
```

### Full Demo

Run the full demo with multiple queries:
```bash
python agent.py
```

### Custom Usage

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

### Components

1. **MemorySystem**: Manages system instructions in JSON
   - `load_instructions()`: Load from file
   - `save_instructions()`: Persist to file
   - `update_instructions()`: Evolve instructions with critique history

2. **AgentTools**: Simple tools the agent can use
   - `calculate()`: Mathematical expressions
   - `get_current_time()`: Current date/time
   - `string_length()`: String length calculation

3. **SelfEvolvingAgent**: Main agent with evolution loop
   - `act()`: Execute query with current instructions
   - `reflect()`: Evaluate response quality
   - `evolve()`: Improve instructions based on critique
   - `run()`: Main loop orchestrating all steps

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
