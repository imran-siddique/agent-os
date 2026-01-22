"""
Simplified Kernel for Feature 2 and 3 integration.

This module provides a simplified kernel interface that uses NodeState
for tracking and integrates with the TraceLogger for research purposes.
"""

from cross_model_verification_kernel.agents.generator_openai import OpenAIGenerator
from cross_model_verification_kernel.agents.verifier_gemini import GeminiVerifier
from cross_model_verification_kernel.core.trace_logger import TraceLogger
from cross_model_verification_kernel.core.types import ExecutionTrace, NodeState


class SimpleVerificationKernel:
    """
    Simplified Verification Kernel with TraceLogger integration.

    This kernel is designed for the Features 2 and 3 implementation,
    providing a straightforward solve() interface with full traceability.
    """

    def __init__(self, max_retries: int = 5):
        """
        Initialize the simplified verification kernel.

        Args:
            max_retries: Maximum number of retry attempts (default: 5)
        """
        self.max_retries = max_retries
        self.generator = OpenAIGenerator()
        self.verifier = GeminiVerifier()
        self.logger = TraceLogger()  # Initialize Logger

    def solve(self, query: str, run_id: str = "experiment") -> str | None:
        """
        Solve a query using the adversarial verification loop.

        This method implements:
        - Feature 1: Generator -> Verifier loop
        - Feature 2: Strategy banning (Lateral Thinking)
        - Feature 3: Trace logging (The Witness)

        Args:
            query: The problem statement to solve
            run_id: Identifier for this run (used in trace filename)

        Returns:
            str: The verified solution code, or None if max retries reached
        """
        state = NodeState(input_query=query)
        print(f"🚀 Starting Kernel for: {query}")

        final_code = None

        for attempt in range(self.max_retries):
            print(f"\n🔄 Attempt {attempt + 1}/{self.max_retries}")

            # 1. Generate Solution
            # Pass forbidden strategies to the generator
            code = self.generator.generate_solution(
                query=query,
                context="Previous attempts failed. Try a different approach.",
                forbidden_strategies=state.forbidden_strategies,
            )

            # 2. Verify Solution
            # In a real implementation, we'd call the verifier's verify method
            # For now, we'll use a simplified approach
            try:
                verification_result = self._verify_code(code, query)
                is_valid = verification_result.get("passed", False)
                feedback = verification_result.get("feedback", "No feedback")
            except Exception as e:
                is_valid = False
                feedback = f"Verification error: {str(e)}"

            # 3. Record in History
            strategy_used = self._detect_strategy(code)
            trace = ExecutionTrace(
                step_id=attempt + 1,
                code_generated=code,
                verifier_feedback=feedback,
                status="success" if is_valid else "failed",
                strategy_used=strategy_used,
            )
            state.history.append(trace)

            # 4. Decision Logic
            if is_valid:
                print("✅ Verified! Solution found.")
                state.current_code = code
                state.status = "verified"
                final_code = code
                break
            else:
                print(f"❌ Verification failed: {feedback}")
                # Feature 2: Add to forbidden_strategies if failed multiple times
                if strategy_used and strategy_used not in state.forbidden_strategies:
                    # Ban strategy if it failed twice
                    strategy_fail_count = sum(
                        1
                        for t in state.history
                        if t.strategy_used == strategy_used and t.status == "failed"
                    )
                    if strategy_fail_count >= 2:
                        state.forbidden_strategies.append(strategy_used)
                        print(f"🚫 Banning strategy: {strategy_used}")

                state.status = "rejected"

        # --- FEATURE 3: SAVE TRACE ---
        self.logger.save_trace(run_id, state)

        if final_code:
            return final_code
        else:
            print("💀 Max retries reached.")
            return None

    def _verify_code(self, code: str, query: str) -> dict:
        """
        Verify the generated code.

        Args:
            code: The generated code
            query: The original query

        Returns:
            dict: Verification result with 'passed' and 'feedback' keys
        """
        try:
            # Use the verifier to check the code
            context = {"task": query, "solution": code, "explanation": "", "test_cases": ""}
            result = self.verifier.verify(context)

            # Check if verification passed
            from cross_model_verification_kernel.core.types import VerificationOutcome

            passed = result.outcome == VerificationOutcome.PASS and not result.has_critical_issues()

            feedback = result.reasoning or "No specific feedback"
            if result.critical_issues:
                feedback += f"\nCritical Issues: {', '.join(result.critical_issues)}"

            return {"passed": passed, "feedback": feedback}
        except Exception as e:
            return {"passed": False, "feedback": f"Verification error: {str(e)}"}

    def _detect_strategy(self, code: str) -> str | None:
        """
        Detect the algorithmic strategy used in the code.

        Args:
            code: The generated code

        Returns:
            str: The detected strategy (e.g., "recursive", "iterative", "numpy")
        """
        code_lower = code.lower()

        # Simple heuristic-based detection
        if "def " in code_lower and "return " in code_lower and code_lower.count("def ") > 1:
            # Check if function calls itself (recursive)
            lines = code.split("\n")
            for line in lines:
                if "def " in line:
                    func_name = line.split("def ")[1].split("(")[0].strip()
                    if func_name in code[code.index(line) :]:
                        return "recursive"

        if "while " in code_lower or "for " in code_lower:
            return "iterative"

        if "numpy" in code_lower or "np." in code_lower:
            return "numpy"

        if "sorted(" in code_lower or ".sort(" in code_lower:
            return "built_in_sort"

        if "re." in code_lower or "import re" in code_lower:
            return "regex"

        return "unknown"
