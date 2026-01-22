"""
Model Provider Interface

Defines the interface for different LLM providers (GPT-4o, Gemini 1.5 Pro, etc.)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any


class ModelProvider(Enum):
    """Supported model providers for generator and verifier"""

    GPT4O = "gpt-4o"
    GPT4_TURBO = "gpt-4-turbo"
    GEMINI_15_PRO = "gemini-1.5-pro"
    GEMINI_15_FLASH = "gemini-1.5-flash"
    CLAUDE_35_SONNET = "claude-3.5-sonnet"
    CLAUDE_3_OPUS = "claude-3-opus"


@dataclass
class ModelResponse:
    """Response from a model provider"""

    content: str
    model: str
    provider: ModelProvider
    metadata: dict[str, Any] | None = None
    reasoning: str | None = None


class BaseModelInterface(ABC):
    """Abstract base class for model interfaces"""

    def __init__(self, model: ModelProvider, api_key: str | None = None):
        self.model = model
        self.api_key = api_key

    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> ModelResponse:
        """Generate a response from the model"""
        pass

    @abstractmethod
    def get_model_info(self) -> dict[str, Any]:
        """Get information about the model"""
        pass


class MockModelInterface(BaseModelInterface):
    """Mock model interface for testing and demonstration"""

    def __init__(self, model: ModelProvider, api_key: str | None = None):
        super().__init__(model, api_key)
        self._call_count = 0

    def generate(self, prompt: str, **kwargs) -> ModelResponse:
        """Generate a mock response"""
        self._call_count += 1

        # Different responses based on model type to simulate diversity
        if self.model in [ModelProvider.GPT4O, ModelProvider.GPT4_TURBO]:
            content = self._generate_gpt_style_response(prompt)
        elif self.model in [ModelProvider.GEMINI_15_PRO, ModelProvider.GEMINI_15_FLASH]:
            content = self._generate_gemini_style_response(prompt)
        else:
            content = self._generate_claude_style_response(prompt)

        return ModelResponse(
            content=content,
            model=self.model.value,
            provider=self.model,
            metadata={"call_count": self._call_count, "prompt_length": len(prompt)},
        )

    def _generate_gpt_style_response(self, prompt: str) -> str:
        """Simulate GPT-style response"""
        if "generate" in prompt.lower() or "code" in prompt.lower():
            return """def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)"""
        return f"GPT-4 response to: {prompt[:50]}..."

    def _generate_gemini_style_response(self, prompt: str) -> str:
        """Simulate Gemini-style response with different perspective"""
        if "verify" in prompt.lower() or "review" in prompt.lower():
            return """CRITICAL ISSUES FOUND:
1. No input validation - negative numbers will cause stack overflow
2. Missing edge case handling for n=0
3. Exponential time complexity O(2^n) - inefficient
4. No memoization or dynamic programming optimization
5. Type hints missing
SEVERITY: HIGH - This implementation has serious performance and safety issues."""
        return f"Gemini response to: {prompt[:50]}..."

    def _generate_claude_style_response(self, prompt: str) -> str:
        """Simulate Claude-style response"""
        return f"Claude response with careful analysis: {prompt[:50]}..."

    def get_model_info(self) -> dict[str, Any]:
        """Get mock model information"""
        return {
            "model": self.model.value,
            "provider": self.model.name,
            "call_count": self._call_count,
            "capabilities": ["text-generation", "code-analysis"],
        }
