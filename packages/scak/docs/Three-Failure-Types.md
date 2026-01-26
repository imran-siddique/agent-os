# Three Failure Types - Implementation Guide

This document explains the implementation of automated fix strategies for three specific failure types as defined in the problem statement.

## Problem Statement

The problem statement defined three failure types that require specific automated fix strategies:

| Failure Type | Description | Automated Fix Strategy |
|-------------|-------------|----------------------|
| Tool Misuse | Agent called `delete_user(id)` with a name instead of UUID | Schema Injection: Update the tool definition in the prompt to be stricter |
| Hallucination | Agent referenced Project_Alpha which doesn't exist | RAG Patch: Add a negative constraint ("Project_Alpha is deprecated") to the context |
| Policy Violation | Agent tried to advise on medical issues | Constitutional Update: Prepend a specific "Refusal Rule" to the system prompt |

## Implementation

### 1. New Cognitive Glitch Types

Added two new cognitive glitch types to the `CognitiveGlitch` enum in `agent_kernel/models.py`:

```python
class CognitiveGlitch(str, Enum):
    # ... existing types ...
    TOOL_MISUSE = "tool_misuse"  # Agent uses tool with wrong parameter types
    POLICY_VIOLATION = "policy_violation"  # Agent violates policy boundaries
```

### 2. Enhanced Failure Detection

Updated `agent_kernel/analyzer.py` to detect these specific patterns:

#### Tool Misuse Detection
- Looks for keywords: "type error", "invalid type", "expected uuid", "uuid", "format"
- Checks if parameter types don't match (e.g., name instead of UUID)
- Example: `delete_user(id='john_doe')` triggers TOOL_MISUSE

#### Hallucination Detection
- Looks for keywords: "not found", "does not exist", "unknown", "deprecated"
- Identifies when agent references non-existent entities
- Example: `get_project('Project_Alpha')` triggers HALLUCINATION

#### Policy Violation Detection  
- Looks for keywords: "policy violation", "cannot advise", "cannot provide"
- Checks user prompt for restricted domains (medical, legal, financial)
- Example: Medical advice request triggers POLICY_VIOLATION

### 3. Patch Strategy Selection

Updated `agent_kernel/patcher.py` to implement the correct patch strategies:

```python
def _determine_patch_strategy(self, analysis, diagnosis):
    # Tool Misuse → Schema Injection (system_prompt)
    if diagnosis.cognitive_glitch == CognitiveGlitch.TOOL_MISUSE:
        return PatchStrategy.SYSTEM_PROMPT
    
    # Hallucination → RAG Patch (rag_memory)
    if diagnosis.cognitive_glitch == CognitiveGlitch.HALLUCINATION:
        return PatchStrategy.RAG_MEMORY
    
    # Policy Violation → Constitutional Update (system_prompt)
    if diagnosis.cognitive_glitch == CognitiveGlitch.POLICY_VIOLATION:
        return PatchStrategy.SYSTEM_PROMPT
```

### 4. Patch Content Generation

#### Tool Misuse → Schema Injection

Generates a strict schema rule for the system prompt:

```python
rule = "SCHEMA INJECTION: Tool definitions for {tool} require strict parameter type checking. 
        Always verify parameter types match the schema exactly (e.g., UUID format for id parameters, not names or strings)."
```

#### Hallucination → RAG Patch

Generates a RAG memory entry with a negative constraint:

```python
{
    "type": "rag_memory",
    "failure_context": "In 2026, user asked: 'Show Project_Alpha', and we failed with: Project_Alpha does not exist.",
    "negative_constraint": "Project_Alpha does not exist and is deprecated. Do not reference it.",
    "verified_by_shadow": True
}
```

#### Policy Violation → Constitutional Update

Generates a constitutional refusal rule:

```python
rule = "CONSTITUTIONAL REFUSAL RULE: You must refuse to provide advice on {domain}. 
        Politely decline and explain that you are not qualified to advise on such matters."
```

## Usage Example

```python
from agent_kernel import SelfCorrectingAgentKernel

kernel = SelfCorrectingAgentKernel()

# Tool Misuse Example
result = kernel.handle_failure(
    agent_id="user-agent",
    error_message="Expected UUID for id parameter",
    user_prompt="Delete user john_doe",
    chain_of_thought=["Deleting user"],
    failed_action={"action": "delete_user", "params": {"id": "john_doe"}},
    auto_patch=True
)
# → Applies Schema Injection patch to system prompt

# Hallucination Example  
result = kernel.handle_failure(
    agent_id="project-agent",
    error_message="Project 'Project_Alpha' does not exist",
    user_prompt="Show Project_Alpha status",
    chain_of_thought=["Getting project"],
    failed_action={"action": "get_project", "name": "Project_Alpha"},
    auto_patch=True
)
# → Adds negative constraint to RAG memory

# Policy Violation Example
result = kernel.handle_failure(
    agent_id="assistant-agent",
    error_message="Policy violation: Cannot advise on medical issues",
    user_prompt="What medication should I take?",
    chain_of_thought=["Providing medical advice"],
    failed_action={"action": "medical_advice"},
    auto_patch=True
)
# → Prepends refusal rule to system prompt
```

## Testing

Comprehensive test suite added in `tests/test_specific_failures.py`:

- **TestToolMisuse**: Tests UUID/parameter type mismatch detection and patching
- **TestHallucination**: Tests non-existent entity detection and RAG patching
- **TestPolicyViolation**: Tests policy boundary detection and constitutional updates
- **TestPatchIntegration**: Integration tests for all three scenarios

Run tests:
```bash
python -m pytest tests/test_specific_failures.py -v
```

## Demo

Run the interactive demonstration:
```bash
python examples/three_failure_types_demo.py
```

This shows all three failure types being detected and patched correctly with detailed output.

## Key Benefits

1. **Automatic Detection**: Cognitive glitch detection happens automatically based on error patterns
2. **Correct Strategy**: Each failure type gets the appropriate fix strategy as specified
3. **Minimal Changes**: Patches are targeted and minimal - only what's necessary
4. **Backward Compatible**: All existing tests still pass, no breaking changes
5. **Well Tested**: 10 new tests added, all 27 tests passing

## Files Modified

- `agent_kernel/models.py`: Added TOOL_MISUSE and POLICY_VIOLATION enums
- `agent_kernel/analyzer.py`: Enhanced cognitive glitch detection logic
- `agent_kernel/patcher.py`: Implemented three patch strategies
- `agent_kernel/detector.py`: Improved failure classification
- `tests/test_specific_failures.py`: Added comprehensive test suite (NEW)
- `examples/three_failure_types_demo.py`: Interactive demonstration (NEW)
