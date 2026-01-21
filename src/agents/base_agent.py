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
