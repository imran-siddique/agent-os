"""
Self-Evolving Agent POC

This module implements a self-evolving agent that:
1. Receives queries and attempts to solve them using tools
2. Evaluates its own performance using an LLM reflection system
3. Evolves its system instructions based on critique when performance is below threshold
4. Retries with improved instructions
"""

import json
import os
import ast
import operator
from typing import Dict, List, Any, Tuple
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class MemorySystem:
    """Manages the agent's system instructions stored in JSON."""
    
    def __init__(self, memory_file: str = "system_instructions.json"):
        self.memory_file = memory_file
        self.instructions = self.load_instructions()
    
    def load_instructions(self) -> Dict[str, Any]:
        """Load system instructions from JSON file."""
        if os.path.exists(self.memory_file):
            with open(self.memory_file, 'r') as f:
                return json.load(f)
        else:
            # Default instructions
            return {
                "version": 1,
                "instructions": "You are a helpful AI assistant.",
                "improvements": []
            }
    
    def save_instructions(self, instructions: Dict[str, Any]) -> None:
        """Save system instructions to JSON file."""
        with open(self.memory_file, 'w') as f:
            json.dump(instructions, f, indent=2)
        self.instructions = instructions
    
    def get_system_prompt(self) -> str:
        """Get the current system instructions as a prompt."""
        return self.instructions.get("instructions", "")
    
    def update_instructions(self, new_instructions: str, critique: str) -> None:
        """Update instructions with new version and log the improvement."""
        self.instructions["version"] = self.instructions.get("version", 0) + 1
        self.instructions["instructions"] = new_instructions
        self.instructions["improvements"].append({
            "version": self.instructions["version"],
            "timestamp": datetime.now().isoformat(),
            "critique": critique
        })
        self.save_instructions(self.instructions)


class AgentTools:
    """Simple tools the agent can use."""
    
    @staticmethod
    def calculate(expression: str) -> str:
        """Safely evaluate a mathematical expression using AST parsing."""
        # Safe mathematical operators
        operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
            ast.USub: operator.neg,
        }
        
        def eval_node(node):
            if isinstance(node, ast.Constant):  # Python 3.8+
                return node.value
            elif isinstance(node, ast.Num):  # Fallback for older Python
                return node.n
            elif isinstance(node, ast.BinOp):
                left = eval_node(node.left)
                right = eval_node(node.right)
                return operators[type(node.op)](left, right)
            elif isinstance(node, ast.UnaryOp):
                operand = eval_node(node.operand)
                return operators[type(node.op)](operand)
            else:
                raise ValueError(f"Unsupported operation: {type(node).__name__}")
        
        try:
            # Parse the expression
            tree = ast.parse(expression, mode='eval')
            result = eval_node(tree.body)
            return f"Result: {result}"
        except (ValueError, KeyError, SyntaxError, TypeError) as e:
            return f"Error: Invalid mathematical expression - {str(e)}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    @staticmethod
    def get_current_time() -> str:
        """Get the current time."""
        return f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    @staticmethod
    def string_length(text: str) -> str:
        """Get the length of a string."""
        return f"Length: {len(text)}"
    
    @staticmethod
    def get_available_tools() -> str:
        """List available tools."""
        return """Available tools:
1. calculate(expression) - Evaluate mathematical expressions
2. get_current_time() - Get current date and time
3. string_length(text) - Get length of a string
"""


class SelfEvolvingAgent:
    """Main self-evolving agent with reflection and evolution capabilities."""
    
    def __init__(self, 
                 memory_file: str = "system_instructions.json",
                 score_threshold: float = 0.8,
                 max_retries: int = 3):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.memory = MemorySystem(memory_file)
        self.tools = AgentTools()
        self.score_threshold = score_threshold
        self.max_retries = max_retries
        
        # Model configuration
        self.agent_model = os.getenv("AGENT_MODEL", "gpt-4o-mini")
        self.reflection_model = os.getenv("REFLECTION_MODEL", "gpt-4o-mini")
        self.evolution_model = os.getenv("EVOLUTION_MODEL", "gpt-4o-mini")
    
    def execute_tool(self, tool_name: str, *args) -> str:
        """Execute a tool by name."""
        if hasattr(self.tools, tool_name):
            return getattr(self.tools, tool_name)(*args)
        return f"Error: Tool '{tool_name}' not found"
    
    def act(self, query: str) -> str:
        """
        Agent attempts to solve the query using its current system instructions.
        """
        system_prompt = self.memory.get_system_prompt()
        
        # Add tool information to the system prompt
        full_system_prompt = f"{system_prompt}\n\n{self.tools.get_available_tools()}"
        full_system_prompt += "\nIf you need to use a tool, explain which tool you would use and why."
        
        messages = [
            {"role": "system", "content": full_system_prompt},
            {"role": "user", "content": query}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.agent_model,
                messages=messages,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error executing agent: {str(e)}"
    
    def reflect(self, query: str, agent_response: str) -> Tuple[float, str]:
        """
        Separate LLM call to evaluate the agent's output.
        Returns a score (0-1) and critique.
        """
        reflection_prompt = f"""You are an evaluator assessing an AI agent's response.

User Query: {query}

Agent Response: {agent_response}

Evaluate the response on the following criteria:
1. Correctness: Did the agent answer the question correctly?
2. Completeness: Did the agent provide a complete answer?
3. Clarity: Is the response clear and well-explained?
4. Tool Usage: Did the agent appropriately identify and explain tool usage when needed?

Provide your evaluation as JSON with:
- score: A number between 0 and 1 (0 = poor, 1 = excellent)
- critique: A detailed explanation of what was good and what could be improved

Return ONLY valid JSON in this format:
{{"score": 0.85, "critique": "Your detailed critique here"}}
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.reflection_model,
                messages=[{"role": "user", "content": reflection_prompt}],
                temperature=0.3
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Extract JSON from response (handle markdown code blocks)
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(result_text)
            return result["score"], result["critique"]
        except Exception as e:
            print(f"Error in reflection: {str(e)}")
            # Default to low score if reflection fails
            return 0.5, f"Reflection error: {str(e)}"
    
    def evolve(self, critique: str, query: str, agent_response: str) -> str:
        """
        Third LLM call that reads critique and rewrites system instructions.
        """
        current_instructions = self.memory.get_system_prompt()
        
        evolution_prompt = f"""You are a meta-learning system that improves AI agent instructions.

Current System Instructions:
{current_instructions}

Recent Query: {query}
Agent Response: {agent_response}

Evaluation Critique:
{critique}

Your task is to rewrite the system instructions to address the issues identified in the critique.
The new instructions should help the agent perform better on similar queries in the future.

Guidelines:
- Keep the instructions clear and concise
- Add specific guidance to address the critique
- Maintain the helpful and accurate nature of the agent
- Include any necessary improvements for tool usage
- Don't make the instructions overly long or complex

Return ONLY the new system instructions as plain text (no JSON, no formatting):
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.evolution_model,
                messages=[{"role": "user", "content": evolution_prompt}],
                temperature=0.7
            )
            
            new_instructions = response.choices[0].message.content.strip()
            return new_instructions
        except Exception as e:
            print(f"Error in evolution: {str(e)}")
            return current_instructions  # Return unchanged if evolution fails
    
    def run(self, query: str, verbose: bool = True) -> Dict[str, Any]:
        """
        Main loop: Task -> Act -> Reflect -> Evolve -> Retry
        """
        results = {
            "query": query,
            "attempts": []
        }
        
        for attempt in range(self.max_retries):
            if verbose:
                print(f"\n{'='*60}")
                print(f"ATTEMPT {attempt + 1}/{self.max_retries}")
                print(f"{'='*60}")
                print(f"Current Instructions Version: {self.memory.instructions['version']}")
            
            # ACT: Agent tries to solve the query
            if verbose:
                print(f"\n[ACTING] Processing query...")
            agent_response = self.act(query)
            if verbose:
                print(f"Agent Response: {agent_response}")
            
            # REFLECT: Evaluate the response
            if verbose:
                print(f"\n[REFLECTING] Evaluating response...")
            score, critique = self.reflect(query, agent_response)
            if verbose:
                print(f"Score: {score}")
                print(f"Critique: {critique}")
            
            # Store attempt results
            attempt_result = {
                "attempt": attempt + 1,
                "response": agent_response,
                "score": score,
                "critique": critique,
                "instructions_version": self.memory.instructions['version']
            }
            results["attempts"].append(attempt_result)
            
            # Check if score meets threshold
            if score >= self.score_threshold:
                if verbose:
                    print(f"\n[SUCCESS] Score {score} meets threshold {self.score_threshold}")
                results["success"] = True
                results["final_response"] = agent_response
                results["final_score"] = score
                return results
            
            # EVOLVE: If score < threshold and we have retries left
            if attempt < self.max_retries - 1:
                if verbose:
                    print(f"\n[EVOLVING] Score {score} below threshold {self.score_threshold}")
                    print("Rewriting system instructions...")
                
                new_instructions = self.evolve(critique, query, agent_response)
                self.memory.update_instructions(new_instructions, critique)
                
                if verbose:
                    print(f"Updated to version {self.memory.instructions['version']}")
                    print(f"New instructions: {new_instructions[:200]}...")
        
        # Max retries reached
        if verbose:
            print(f"\n[EXHAUSTED] Max retries reached. Best score: {max(a['score'] for a in results['attempts'])}")
        
        results["success"] = False
        best_attempt = max(results["attempts"], key=lambda x: x["score"])
        results["final_response"] = best_attempt["response"]
        results["final_score"] = best_attempt["score"]
        return results


def main():
    """Example usage of the self-evolving agent."""
    print("Self-Evolving Agent POC")
    print("=" * 60)
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not found in environment variables")
        print("Please create a .env file with your OpenAI API key")
        return
    
    # Initialize agent
    agent = SelfEvolvingAgent(
        score_threshold=float(os.getenv("SCORE_THRESHOLD", "0.8")),
        max_retries=int(os.getenv("MAX_RETRIES", "3"))
    )
    
    # Example queries
    queries = [
        "What is 15 * 24 + 100?",
        "What is the length of the word 'supercalifragilisticexpialidocious'?",
        "What time is it right now?"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n\n{'#'*60}")
        print(f"QUERY {i}: {query}")
        print(f"{'#'*60}")
        
        results = agent.run(query, verbose=True)
        
        print(f"\n\nFINAL RESULTS:")
        print(f"Success: {results['success']}")
        print(f"Final Score: {results['final_score']}")
        print(f"Total Attempts: {len(results['attempts'])}")
        print(f"Final Response: {results['final_response']}")
        
        # Wait for user input between queries (optional)
        if i < len(queries):
            input("\nPress Enter to continue to next query...")


if __name__ == "__main__":
    main()
