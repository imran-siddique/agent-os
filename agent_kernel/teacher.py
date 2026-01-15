"""
Teacher - Simplified reference implementation for the Shadow Teacher.

This is a reference implementation showing the core concept of using a
"Teacher Model" (stronger reasoning model) to diagnose why an agent failed.

The production implementation is integrated throughout the analyzer.py and
completeness_auditor.py modules with full trace capture and cognitive diagnosis.
"""


async def diagnose_failure(prompt, failed_response, tool_trace):
    """
    Uses a 'Reasoning Model' (e.g., o1 or Claude 3.5 Sonnet) 
    to find the Root Cause.
    
    Args:
        prompt: The original task/prompt that failed
        failed_response: The agent's failed response
        tool_trace: Trace of tools/actions the agent attempted
        
    Returns:
        dict: Diagnosis with cause and lesson_patch
    """
    teacher_prompt = f"""
    The Agent failed to complete this task: '{prompt}'.
    
    Agent Output: {failed_response}
    Tool Trace: {tool_trace}
    
    Task:
    1. Did the agent try hard enough? (Laziness)
    2. Did the agent hallucinate a tool parameter? (Skill Issue)
    3. Write a 1-sentence 'Lesson' that fixes this specific error.
    
    Output Format: JSON {{ "cause": "...", "lesson_patch": "..." }}
    """
    
    # In production, this would call the "Expensive" Model only on failure
    # For this reference implementation, we simulate the response
    # diagnosis = await llm_client.generate(model="o1-preview", prompt=teacher_prompt)
    
    # Simulated diagnosis for reference
    diagnosis = {
        "cause": "Agent gave up without exhaustive search",
        "lesson_patch": "Before reporting 'not found', check all data sources including archived partitions"
    }
    
    return diagnosis
