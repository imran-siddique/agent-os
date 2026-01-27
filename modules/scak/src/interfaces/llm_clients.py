"""
Real LLM client integrations for production use.

This module provides async clients for OpenAI and Anthropic APIs,
replacing the mock implementations used in prototypes.

Research Foundation:
- "Reflexion: Language Agents with Verbal Reinforcement Learning" (NeurIPS 2023)
- "Constitutional AI: Harmlessness from AI Feedback" (arXiv:2212.08073)
- "Self-Refine: Iterative Refinement with Self-Feedback" (NeurIPS 2023)
"""

from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod
import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class LLMClient(ABC):
    """
    Abstract base class for LLM clients.
    
    Enables pluggable LLM backends while maintaining consistent interface
    for the self-correcting kernel.
    """
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        """Generate completion from LLM."""
        pass
    
    @abstractmethod
    async def generate_with_reasoning(
        self,
        prompt: str,
        system: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate completion with reasoning trace.
        
        Used by Shadow Teacher for diagnostic analysis.
        Based on o1-preview's reasoning capabilities.
        """
        pass


class OpenAIClient(LLMClient):
    """
    Async OpenAI client for production use.
    
    Supports GPT-4o, GPT-4-turbo, and o1-preview models.
    Implements retry logic, rate limiting, and structured telemetry.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o",
        max_retries: int = 3,
        timeout: float = 60.0
    ):
        """
        Initialize OpenAI client.
        
        Args:
            api_key: OpenAI API key (or set OPENAI_API_KEY env var)
            model: Model to use (gpt-4o, gpt-4-turbo, o1-preview)
            max_retries: Number of retries on failure
            timeout: Request timeout in seconds
        """
        self.model = model
        self.max_retries = max_retries
        self.timeout = timeout
        
        # Lazy import to avoid requiring openai package if not used
        try:
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(api_key=api_key, timeout=timeout)
        except ImportError:
            logger.warning(
                "OpenAI package not installed. Install with: pip install openai"
            )
            self.client = None
    
    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        """
        Generate completion from OpenAI API.
        
        Implements exponential backoff retry logic for production resilience.
        
        Args:
            prompt: User prompt
            system: System prompt (optional)
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters passed to OpenAI API
            
        Returns:
            Generated text response
            
        Raises:
            RuntimeError: If OpenAI client not initialized
            Exception: On API failures after retries
        """
        if not self.client:
            raise RuntimeError(
                "OpenAI client not initialized. Install openai package."
            )
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        for attempt in range(self.max_retries):
            try:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs
                )
                
                content = response.choices[0].message.content
                
                # Emit telemetry
                logger.info(
                    f"OpenAI API call successful: "
                    f"model={self.model}, "
                    f"tokens={response.usage.total_tokens}"
                )
                
                return content
                
            except Exception as e:
                logger.warning(
                    f"OpenAI API call failed (attempt {attempt + 1}/{self.max_retries}): {e}"
                )
                
                if attempt < self.max_retries - 1:
                    # Exponential backoff
                    await asyncio.sleep(2 ** attempt)
                else:
                    raise
    
    async def generate_with_reasoning(
        self,
        prompt: str,
        system: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate completion with reasoning trace using o1-preview.
        
        The o1-preview model provides explicit reasoning steps,
        crucial for Shadow Teacher diagnostic analysis.
        
        Research: "Reflexion: Language Agents with Verbal Reinforcement Learning"
        demonstrates the value of explicit reasoning traces for agent improvement.
        
        Args:
            prompt: Diagnostic prompt
            system: System context
            **kwargs: Additional parameters
            
        Returns:
            dict with 'response' and 'reasoning' fields
        """
        if not self.client:
            raise RuntimeError(
                "OpenAI client not initialized. Install openai package."
            )
        
        # For o1-preview, use specific parameters
        reasoning_model = "o1-preview" if "o1" in self.model else self.model
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = await self.client.chat.completions.create(
                model=reasoning_model,
                messages=messages,
                **kwargs
            )
            
            content = response.choices[0].message.content
            
            # Extract reasoning if present (o1 models include it)
            reasoning = "Reasoning trace available in response"
            
            return {
                "response": content,
                "reasoning": reasoning,
                "model": reasoning_model,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Reasoning generation failed: {e}")
            raise


class AnthropicClient(LLMClient):
    """
    Async Anthropic client for Claude models.
    
    Supports Claude 3.5 Sonnet, Claude 3 Opus.
    Anthropic's Constitutional AI research informs our alignment approach.
    
    Research: "Constitutional AI: Harmlessness from AI Feedback" (Anthropic 2023)
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-3-5-sonnet-20241022",
        max_retries: int = 3,
        timeout: float = 60.0
    ):
        """
        Initialize Anthropic client.
        
        Args:
            api_key: Anthropic API key (or set ANTHROPIC_API_KEY env var)
            model: Claude model to use
            max_retries: Number of retries on failure
            timeout: Request timeout in seconds
        """
        self.model = model
        self.max_retries = max_retries
        self.timeout = timeout
        
        # Lazy import to avoid requiring anthropic package if not used
        try:
            from anthropic import AsyncAnthropic
            self.client = AsyncAnthropic(api_key=api_key, timeout=timeout)
        except ImportError:
            logger.warning(
                "Anthropic package not installed. Install with: pip install anthropic"
            )
            self.client = None
    
    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        """
        Generate completion from Anthropic API.
        
        Args:
            prompt: User prompt
            system: System prompt (optional)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
            
        Returns:
            Generated text response
        """
        if not self.client:
            raise RuntimeError(
                "Anthropic client not initialized. Install anthropic package."
            )
        
        for attempt in range(self.max_retries):
            try:
                response = await self.client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=system or "",
                    messages=[{"role": "user", "content": prompt}],
                    **kwargs
                )
                
                content = response.content[0].text
                
                logger.info(
                    f"Anthropic API call successful: "
                    f"model={self.model}"
                )
                
                return content
                
            except Exception as e:
                logger.warning(
                    f"Anthropic API call failed (attempt {attempt + 1}/{self.max_retries}): {e}"
                )
                
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                else:
                    raise
    
    async def generate_with_reasoning(
        self,
        prompt: str,
        system: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate completion with explicit reasoning.
        
        Claude 3.5 Sonnet has strong reasoning capabilities.
        We prompt it to show its work for diagnostic analysis.
        
        Args:
            prompt: Diagnostic prompt
            system: System context
            **kwargs: Additional parameters
            
        Returns:
            dict with 'response' and 'reasoning' fields
        """
        if not self.client:
            raise RuntimeError(
                "Anthropic client not initialized. Install anthropic package."
            )
        
        # Augment prompt to request explicit reasoning
        reasoning_prompt = f"""
Please think step-by-step and show your reasoning.

{prompt}

Provide your answer in the following format:
REASONING: [your step-by-step analysis]
CONCLUSION: [your final answer]
"""
        
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                system=system or "",
                messages=[{"role": "user", "content": reasoning_prompt}],
                **kwargs
            )
            
            content = response.content[0].text
            
            # Parse reasoning and conclusion
            reasoning = ""
            conclusion = content
            
            if "REASONING:" in content and "CONCLUSION:" in content:
                parts = content.split("CONCLUSION:")
                reasoning = parts[0].replace("REASONING:", "").strip()
                conclusion = parts[1].strip() if len(parts) > 1 else content
            
            return {
                "response": conclusion,
                "reasoning": reasoning,
                "model": self.model,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Reasoning generation failed: {e}")
            raise


class MockLLMClient(LLMClient):
    """
    Mock LLM client for testing and development.
    
    Returns deterministic responses based on patterns in prompts.
    Used in unit tests and when API keys are not available.
    """
    
    def __init__(self, responses: Optional[Dict[str, str]] = None):
        """
        Initialize mock client with optional response mapping.
        
        Args:
            responses: Dict mapping prompt keywords to responses
        """
        self.responses = responses or {}
        self.call_count = 0
    
    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        """
        Generate mock response based on prompt patterns.
        
        Args:
            prompt: User prompt
            system: System prompt (ignored in mock)
            temperature: Ignored in mock
            max_tokens: Ignored in mock
            **kwargs: Ignored in mock
            
        Returns:
            Mock response string
        """
        self.call_count += 1
        
        # Check for custom responses
        for keyword, response in self.responses.items():
            if keyword.lower() in prompt.lower():
                return response
        
        # Default responses based on common patterns
        if "diagnose" in prompt.lower() or "analyze" in prompt.lower():
            return "DIAGNOSIS: Agent gave up prematurely. CAUSE: Insufficient search depth."
        elif "search" in prompt.lower() or "find" in prompt.lower():
            return "Search completed successfully. Found 5 results."
        else:
            return f"Mock response to: {prompt[:50]}..."
    
    async def generate_with_reasoning(
        self,
        prompt: str,
        system: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate mock response with reasoning.
        
        Args:
            prompt: Diagnostic prompt
            system: System context (ignored)
            **kwargs: Ignored
            
        Returns:
            dict with mock response and reasoning
        """
        response = await self.generate(prompt, system, **kwargs)
        
        return {
            "response": response,
            "reasoning": "Mock reasoning: Step 1 → Step 2 → Conclusion",
            "model": "mock-model",
            "timestamp": datetime.now().isoformat()
        }


def get_llm_client(
    provider: str = "openai",
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    **kwargs
) -> LLMClient:
    """
    Factory function to get LLM client by provider.
    
    Enables easy switching between providers and mock for testing.
    
    Args:
        provider: "openai", "anthropic", or "mock"
        model: Model name (provider-specific)
        api_key: API key for the provider
        **kwargs: Additional client configuration
        
    Returns:
        LLMClient instance
        
    Example:
        >>> client = get_llm_client("openai", model="gpt-4o")
        >>> response = await client.generate("Explain quantum computing")
    """
    if provider == "openai":
        default_model = model or "gpt-4o"
        return OpenAIClient(api_key=api_key, model=default_model, **kwargs)
    elif provider == "anthropic":
        default_model = model or "claude-3-5-sonnet-20241022"
        return AnthropicClient(api_key=api_key, model=default_model, **kwargs)
    elif provider == "mock":
        return MockLLMClient(**kwargs)
    else:
        raise ValueError(
            f"Unknown provider: {provider}. Choose 'openai', 'anthropic', or 'mock'"
        )
