"""
Generator Module

Implements the Generator component that creates code using one model.
The Generator is intentionally decoupled from the Verifier to enable adversarial verification.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from .models import ModelProvider, BaseModelInterface, MockModelInterface


@dataclass
class GeneratorConfig:
    """Configuration for the Generator"""
    model: ModelProvider
    temperature: float = 0.7
    max_tokens: int = 2000
    api_key: Optional[str] = None
    custom_instructions: Optional[str] = None


@dataclass
class GeneratedCode:
    """Container for generated code"""
    code: str
    language: str
    description: str
    model_used: str
    metadata: Optional[Dict[str, Any]] = None


class Generator:
    """
    Generator component that creates code using a specified model.
    
    This component is intentionally decoupled from verification to enable
    adversarial testing with different models.
    """
    
    def __init__(self, config: GeneratorConfig, model_interface: Optional[BaseModelInterface] = None):
        """
        Initialize the Generator
        
        Args:
            config: Generator configuration
            model_interface: Optional custom model interface (uses mock if not provided)
        """
        self.config = config
        self.model_interface = model_interface or MockModelInterface(
            model=config.model,
            api_key=config.api_key
        )
        self.generation_count = 0
    
    def generate_code(
        self,
        task_description: str,
        language: str = "python",
        **kwargs
    ) -> GeneratedCode:
        """
        Generate code based on a task description
        
        Args:
            task_description: Description of what the code should do
            language: Programming language (default: python)
            **kwargs: Additional generation parameters
        
        Returns:
            GeneratedCode object containing the generated code and metadata
        """
        self.generation_count += 1
        
        # Build the prompt for code generation
        prompt = self._build_generation_prompt(task_description, language)
        
        # Add custom instructions if provided
        if self.config.custom_instructions:
            prompt = f"{self.config.custom_instructions}\n\n{prompt}"
        
        # Generate using the model
        response = self.model_interface.generate(
            prompt,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            **kwargs
        )
        
        return GeneratedCode(
            code=response.content,
            language=language,
            description=task_description,
            model_used=response.model,
            metadata={
                "generation_count": self.generation_count,
                "provider": response.provider.value,
                "response_metadata": response.metadata
            }
        )
    
    def _build_generation_prompt(self, task_description: str, language: str) -> str:
        """Build the prompt for code generation"""
        return f"""Generate {language} code for the following task:

Task: {task_description}

Requirements:
- Write clean, functional code
- Include necessary imports
- Focus on correctness and readability

Generate the code:"""
    
    def get_stats(self) -> Dict[str, Any]:
        """Get generator statistics"""
        return {
            "model": self.config.model.value,
            "generation_count": self.generation_count,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens
        }
