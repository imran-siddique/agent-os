"""
OpenAI Generator Agent - System 1 thinking.
This agent uses GPT-4o or similar models to generate creative solutions.
"""

import logging
import os
from pathlib import Path
from typing import Any

from ..core.types import GenerationResult, VerificationResult
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class OpenAIGenerator(BaseAgent):
    """
    Generator agent using OpenAI models (GPT-4o, o1-mini, etc.).

    Role: High creativity, high speed builder with System 1 thinking.
    """

    def __init__(self, model_name: str = "gpt-4o", api_key: str | None = None, **kwargs):
        """
        Initialize the OpenAI generator.

        Args:
            model_name: OpenAI model to use (default: gpt-4o)
            api_key: OpenAI API key (if None, reads from environment)
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
        """
        if api_key is None:
            api_key = os.environ.get("OPENAI_API_KEY", "")

        super().__init__(model_name, api_key, **kwargs)

        # Load system prompt
        prompt_path = (
            Path(__file__).parent.parent.parent / "config" / "prompts" / "generator_v1.txt"
        )
        self.system_prompt = self._load_system_prompt(str(prompt_path))

        # Initialize OpenAI client (lazy import to avoid dependency issues)
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize the OpenAI client."""
        try:
            from openai import OpenAI

            self.client = OpenAI(api_key=self.api_key)
            logger.info("OpenAI client initialized successfully")
        except ImportError:
            logger.warning("OpenAI package not installed. Install with: pip install openai")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")

    def generate(self, task: str, context: dict[str, Any] | None = None) -> GenerationResult:
        """
        Generate a solution for the given task.

        Args:
            task: The problem statement
            context: Optional context including iteration number and previous feedback

        Returns:
            GenerationResult containing the solution
        """
        logger.info(f"Generating solution with {self.model_name}")

        # Build the prompt
        user_prompt = self._build_prompt(task, context)

        # Call OpenAI API
        try:
            if self.client is None:
                # Fallback for testing without API
                return self._mock_generation(task)

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=self.config.get("temperature", 0.7),
                max_tokens=self.config.get("max_tokens", 2000),
            )

            content = response.choices[0].message.content

            # Parse the response (expecting structured output)
            result = self._parse_generation_response(content)
            logger.info("Solution generated successfully")
            return result

        except Exception as e:
            logger.error(f"Error during generation: {e}")
            return self._mock_generation(task)

    def generate_solution(
        self,
        query: str,
        context: str | None = None,
        forbidden_strategies: list[str] | None = None,
    ) -> str:
        """
        Generate a solution for the given query with optional constraints.

        This method is designed for use with the Lateral Thinking feature (Feature 2).
        It enforces constraints on forbidden strategies to enable branching to different approaches.

        Args:
            query: The problem statement
            context: Optional context string (e.g., previous failure feedback)
            forbidden_strategies: List of strategies to avoid (e.g., ["recursive", "brute_force"])

        Returns:
            String containing the generated Python code
        """
        logger.info(f"Generating solution with {self.model_name}")

        # 1. Construct the Constraint Block
        constraint_prompt = ""
        if forbidden_strategies and len(forbidden_strategies) > 0:
            constraint_prompt = "\n\nCRITICAL CONSTRAINTS - DO NOT USE THE FOLLOWING STRATEGIES:\n"
            for strategy in forbidden_strategies:
                constraint_prompt += f"- {strategy}\n"
            constraint_prompt += "You MUST choose a fundamentally different algorithmic approach.\n"

        # 2. Build Full Prompt
        full_prompt = f"""
GOAL: Write Python code to solve the following problem.
PROBLEM: {query}

CONTEXT: {context if context else "None"}

{constraint_prompt}

OUTPUT: Return ONLY the Python code block.
"""

        # 3. Call OpenAI API
        try:
            if self.client is None:
                # Fallback for testing without API
                logger.warning("Using mock generation (API not available)")
                return f"# Mock solution for: {query}\npass"

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": full_prompt},
                ],
                temperature=self.config.get("temperature", 0.7),
                max_tokens=self.config.get("max_tokens", 2000),
            )

            content = response.choices[0].message.content
            logger.info("Solution generated successfully")
            return content

        except Exception as e:
            logger.error(f"Error during generation: {e}")
            return f"# Error generating solution: {e}\npass"

    def verify(self, context: dict[str, Any]) -> VerificationResult:
        """
        Not implemented for Generator agent.
        Generators don't verify - they only generate.
        """
        raise NotImplementedError("Generator agents don't perform verification")

    def _build_prompt(self, task: str, context: dict[str, Any] | None = None) -> str:
        """Build the user prompt including task and context."""
        prompt_parts = [f"Task: {task}"]

        if context and context.get("previous_feedback"):
            feedback = context["previous_feedback"]
            prompt_parts.append("\n\nPrevious Verification Feedback:")
            prompt_parts.append(f"Outcome: {feedback.get('outcome', 'N/A')}")

            critical_issues = feedback.get("critical_issues", [])
            if critical_issues:
                prompt_parts.append(f"Critical Issues: {', '.join(critical_issues)}")
            logic_flaws = feedback.get("logic_flaws", [])
            if logic_flaws:
                prompt_parts.append(f"Logic Flaws: {', '.join(logic_flaws)}")
            missing_edge_cases = feedback.get("missing_edge_cases", [])
            if missing_edge_cases:
                prompt_parts.append(f"Missing Edge Cases: {', '.join(missing_edge_cases)}")

            prompt_parts.append("\nPlease address these issues in your solution.")

        return "\n".join(prompt_parts)

    def _parse_generation_response(self, content: str) -> GenerationResult:
        """
        Parse the model's response into a structured GenerationResult.

        This is a simplified parser - in production, you might use more sophisticated parsing.
        """
        # TODO: Implement proper parsing based on expected format
        # For now, return a basic result
        return GenerationResult(
            solution=content,
            explanation="Generated solution",
            test_cases="# TODO: Extract test cases from response",
            edge_cases=[],
        )

    def _mock_generation(self, task: str) -> GenerationResult:
        """Generate a mock result for testing when API is not available."""
        logger.warning("Using mock generation (API not available)")
        return GenerationResult(
            solution=f"# Mock solution for: {task}\npass",
            explanation="This is a mock solution for testing purposes",
            test_cases="# Mock test cases",
            edge_cases=["Mock edge case 1"],
        )
