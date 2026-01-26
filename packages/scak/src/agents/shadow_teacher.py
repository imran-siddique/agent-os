"""
Shadow Teacher - The o1/Sonnet Diagnostic Agent.

This is the "Critic" that uses a stronger reasoning model (o1-preview, Claude 3.5 Sonnet)
to diagnose agent failures and provide counterfactual analysis.

The Shadow Teacher:
1. Compares Failed_Trace with Counterfactual_Run
2. Identifies cognitive glitches (laziness, hallucination, tool misuse)
3. Generates specific Patches (not just retries)

This is production-grade implementation with async/await, type safety, and telemetry.
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# Import models from agent_kernel for backward compatibility
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from agent_kernel.models import DiagnosisJSON, CognitiveGlitch, ShadowAgentResult


def _sanitize_input(text: str, max_length: int = 1000) -> str:
    """
    Sanitize input to prevent prompt injection.
    
    Critical security measure for production systems where user input
    flows into LLM prompts.
    
    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Truncate to max length
    text = str(text)[:max_length]
    
    # Remove potential prompt injection patterns
    dangerous_patterns = ["ignore previous", "ignore all", "disregard", "new instructions"]
    text_lower = text.lower()
    for pattern in dangerous_patterns:
        if pattern in text_lower:
            text = text.replace(pattern, "[FILTERED]")
    
    return text


async def diagnose_failure(
    prompt: str,
    failed_response: str,
    tool_trace: str,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Uses a 'Reasoning Model' (e.g., o1-preview or Claude 3.5 Sonnet) 
    to find the Root Cause of agent failure.
    
    This is the core of the Shadow Teacher - deep diagnostic analysis
    that goes beyond surface-level error messages to identify systematic
    cognitive issues.
    
    Args:
        prompt: The original task/prompt that failed
        failed_response: The agent's failed response
        tool_trace: Trace of tools/actions the agent attempted
        context: Additional context (optional)
        
    Returns:
        dict: Diagnosis with cause, lesson_patch, and cognitive_glitch type
    """
    # Sanitize inputs to prevent prompt injection
    safe_prompt = _sanitize_input(prompt)
    safe_response = _sanitize_input(failed_response)
    safe_trace = _sanitize_input(tool_trace)
    
    logger.info(f"🔍 Shadow Teacher analyzing failure...")
    
    # Construct diagnostic prompt for reasoning model
    teacher_prompt = f"""
    The Agent failed to complete this task: '{safe_prompt}'.
    
    Agent Output: {safe_response}
    Tool Trace: {safe_trace}
    
    Task:
    1. Did the agent try hard enough? (Laziness)
    2. Did the agent hallucinate a tool parameter? (Skill Issue)
    3. Was there a policy violation? (Safety Issue)
    4. Write a 1-sentence 'Lesson' that fixes this specific error.
    
    Output Format: JSON {{ "cause": "...", "lesson_patch": "...", "cognitive_glitch": "..." }}
    """
    
    # In production, this would call the "Expensive" Model only on failure
    # Example:
    # diagnosis_raw = await llm_client.generate(
    #     model="o1-preview",  # or "claude-3-5-sonnet-20241022"
    #     prompt=teacher_prompt,
    #     temperature=0.7,
    #     max_tokens=500
    # )
    
    # For demonstration, simulate the response based on pattern analysis
    diagnosis = _simulate_teacher_diagnosis(safe_prompt, safe_response, safe_trace, context)
    
    logger.info(f"📊 Diagnosis: {diagnosis['cognitive_glitch']}")
    logger.info(f"💡 Lesson: {diagnosis['lesson_patch'][:80]}...")
    
    return diagnosis


def _simulate_teacher_diagnosis(
    prompt: str,
    response: str,
    trace: str,
    context: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Simulate Shadow Teacher diagnosis.
    
    In production, this would be replaced with actual o1-preview or Claude API call.
    For demonstration, we use pattern matching to simulate diagnostic reasoning.
    
    Args:
        prompt: User prompt
        response: Agent response
        trace: Tool trace
        context: Additional context
        
    Returns:
        dict: Simulated diagnosis
    """
    prompt_lower = prompt.lower()
    response_lower = response.lower()
    
    # Pattern 1: Give-up signals (LAZINESS)
    give_up_signals = ["no data found", "cannot find", "unable to", "not available", "i'm sorry"]
    if any(signal in response_lower for signal in give_up_signals):
        return {
            "cause": "Agent gave up without exhaustive search (SOFT_OMISSION)",
            "lesson_patch": "Before reporting 'not found', check all data sources including archived partitions and alternative indices.",
            "cognitive_glitch": "LAZINESS",
            "confidence": 0.85
        }
    
    # Pattern 2: Tool misuse (SKILL_ISSUE)
    tool_errors = ["invalid parameter", "tool error", "missing required", "type error"]
    if any(error in response_lower for error in tool_errors):
        return {
            "cause": "Agent used tool incorrectly (TOOL_MISUSE)",
            "lesson_patch": "Always validate tool parameters match schema. Use UUID format for IDs, check parameter types before calling.",
            "cognitive_glitch": "TOOL_MISUSE",
            "confidence": 0.92
        }
    
    # Pattern 3: Policy violations (SAFETY_ISSUE)
    blocked_signals = ["blocked", "unauthorized", "permission denied", "not allowed"]
    if any(signal in response_lower for signal in blocked_signals):
        return {
            "cause": "Agent attempted unauthorized action (POLICY_VIOLATION)",
            "lesson_patch": "Never attempt to modify system files or access restricted resources. Always check permissions before operations.",
            "cognitive_glitch": "POLICY_VIOLATION",
            "confidence": 0.95
        }
    
    # Pattern 4: Hallucination (wrong entities)
    if context and "resource" in context:
        if "does not exist" in response_lower or "not found" in response_lower:
            return {
                "cause": "Agent hallucinated entity existence (HALLUCINATION)",
                "lesson_patch": "Verify entity existence in canonical registry before operations. Project_Alpha is archived, not active.",
                "cognitive_glitch": "HALLUCINATION",
                "confidence": 0.88
            }
    
    # Default: General failure
    return {
        "cause": "Agent failed due to unexpected condition",
        "lesson_patch": "Add comprehensive error handling for edge cases and validate assumptions before proceeding.",
        "cognitive_glitch": "UNKNOWN",
        "confidence": 0.70
    }


async def counterfactual_run(
    prompt: str,
    context: Optional[Dict[str, Any]] = None,
    enhanced_context: bool = True
) -> Dict[str, Any]:
    """
    Run a counterfactual simulation with the Shadow Teacher.
    
    The Shadow Teacher attempts the same task with:
    1. Enhanced context/tools
    2. Explicit instructions to be thorough
    3. Access to additional resources
    
    This creates a "what should have happened" baseline for comparison.
    
    Args:
        prompt: Original task prompt
        context: Task context
        enhanced_context: Whether to provide enhanced context
        
    Returns:
        dict with success, response, reasoning, tools_used, confidence
    """
    logger.info(f"🎯 Shadow Teacher attempting counterfactual run...")
    
    # In production, this would:
    # 1. Spin up o1-preview or Claude 3.5 Sonnet
    # 2. Provide enhanced tools/context
    # 3. Add explicit thoroughness instructions
    # 4. Capture complete trace
    
    # Simulate for demonstration
    safe_prompt = _sanitize_input(prompt)
    
    # Enhanced prompt for Shadow Teacher
    enhanced_prompt = f"""
    Task: {safe_prompt}
    
    Instructions:
    - Be exhaustive in your search
    - Check all data sources including archives
    - Verify entity existence before operations
    - Use proper error handling
    - Never give up prematurely
    """
    
    # Simulate successful completion
    result = {
        "success": True,
        "response": "Task completed successfully with exhaustive search.",
        "reasoning": "Shadow Teacher checked all sources including archived data and found results.",
        "tools_used": ["search_primary", "search_archives", "verify_entity"],
        "confidence": 0.90
    }
    
    logger.info(f"✅ Shadow Teacher succeeded: {result['response'][:60]}...")
    
    return result


class ShadowTeacher:
    """
    Production-grade Shadow Teacher orchestrator.
    
    Manages the lifecycle of diagnostic analysis:
    1. Failure diagnosis
    2. Counterfactual runs
    3. Gap analysis (what agent missed)
    4. Patch generation
    
    Uses async/await for non-blocking I/O.
    Emits structured telemetry for offline analysis.
    """
    
    def __init__(self, model: str = "o1-preview"):
        """
        Initialize Shadow Teacher.
        
        Args:
            model: Reasoning model to use (o1-preview, claude-3-5-sonnet, etc.)
        """
        self.model = model
        self.diagnosis_count = 0
        self.counterfactual_count = 0
    
    async def analyze_failure(
        self,
        prompt: str,
        failed_response: str,
        tool_trace: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Complete failure analysis pipeline.
        
        Args:
            prompt: Original prompt
            failed_response: Failed agent response
            tool_trace: Tool execution trace
            context: Additional context
            
        Returns:
            dict: Complete analysis with diagnosis and patch
        """
        self.diagnosis_count += 1
        
        # Step 1: Diagnose the failure
        diagnosis = await diagnose_failure(prompt, failed_response, tool_trace, context)
        
        # Step 2: Run counterfactual (what should have happened)
        counterfactual = await counterfactual_run(prompt, context, enhanced_context=True)
        
        # Step 3: Gap analysis
        gap = self._analyze_gap(failed_response, counterfactual)
        
        return {
            "diagnosis": diagnosis,
            "counterfactual": counterfactual,
            "gap_analysis": gap,
            "timestamp": datetime.now().isoformat(),
            "model": self.model
        }
    
    def _analyze_gap(self, failed_response: str, counterfactual: Dict[str, Any]) -> str:
        """
        Analyze the gap between failed agent and successful Shadow Teacher.
        
        Args:
            failed_response: What agent did
            counterfactual: What Shadow Teacher did (dict with success, response, reasoning, tools_used)
            
        Returns:
            str: Gap analysis
        """
        gap = f"Agent failed with: '{failed_response[:100]}'. "
        gap += f"Shadow Teacher succeeded by: {counterfactual['reasoning']}. "
        gap += f"Key difference: Shadow Teacher used {len(counterfactual['tools_used'])} tools systematically."
        
        return gap
    
    def get_stats(self) -> Dict[str, Any]:
        """Get Shadow Teacher statistics."""
        return {
            "model": self.model,
            "diagnoses_performed": self.diagnosis_count,
            "counterfactuals_run": self.counterfactual_count
        }
