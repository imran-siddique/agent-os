"""
Base agent interface for the Cross-Model Verification Kernel.
All agent implementations (Generator, Verifier) must inherit from BaseAgent.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

from ..core.types import GenerationResult, VerificationResult

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the system.
    
    This defines the interface that all Generator and Verifier agents must implement.
    """
    
    def __init__(self, model_name: str, api_key: str, **kwargs):
        """
        Initialize the agent.
        
        Args:
            model_name: Name of the model to use (e.g., "gpt-4o", "gemini-1.5-pro")
            api_key: API key for the model provider
            **kwargs: Additional model-specific parameters
        """
        self.model_name = model_name
        self.api_key = api_key
        self.config = kwargs
        
        # Token tracking for Experiment C
        self.total_tokens_used = 0
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.call_count = 0
        
        logger.info(f"Initialized {self.__class__.__name__} with model {model_name}")
    
    @abstractmethod
    def generate(self, task: str, context: Optional[Dict[str, Any]] = None) -> GenerationResult:
        """
        Generate a solution for the given task.
        
        This method is used by Generator agents.
        
        Args:
            task: The problem statement or task description
            context: Optional context including previous feedback
            
        Returns:
            GenerationResult containing the solution
        """
        pass
    
    @abstractmethod
    def verify(self, context: Dict[str, Any]) -> VerificationResult:
        """
        Verify a solution.
        
        This method is used by Verifier agents.
        
        Args:
            context: Dictionary containing task, solution, test_cases, etc.
            
        Returns:
            VerificationResult containing the verification outcome
        """
        pass
    
    def _load_system_prompt(self, prompt_file: str) -> str:
        """
        Load a system prompt from file.
        
        Args:
            prompt_file: Path to the prompt file
            
        Returns:
            The prompt text
        """
        try:
            with open(prompt_file, 'r') as f:
                return f.read()
        except FileNotFoundError:
            logger.error(f"Prompt file not found: {prompt_file}")
            return ""
    
    def get_token_stats(self) -> Dict[str, int]:
        """
        Get token usage statistics.
        
        Returns:
            Dictionary with token usage stats
        """
        return {
            "total_tokens": self.total_tokens_used,
            "input_tokens": self.total_input_tokens,
            "output_tokens": self.total_output_tokens,
            "call_count": self.call_count,
            "avg_tokens_per_call": self.total_tokens_used / self.call_count if self.call_count > 0 else 0
        }
    
    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for a given text.
        
        This is a rough estimate: ~4 characters per token.
        For more accurate counting, use tiktoken for OpenAI or the model's tokenizer.
        
        Args:
            text: The text to estimate tokens for
            
        Returns:
            Estimated token count
        """
        return len(text) // 4
    
    def _record_token_usage(self, input_text: str, output_text: str) -> None:
        """
        Record token usage for an API call.
        
        Args:
            input_text: The input prompt text
            output_text: The generated output text
        """
        input_tokens = self._estimate_tokens(input_text)
        output_tokens = self._estimate_tokens(output_text)
        total = input_tokens + output_tokens
        
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.total_tokens_used += total
        self.call_count += 1
        
        logger.debug(f"Token usage - Input: {input_tokens}, Output: {output_tokens}, Total: {total}")
