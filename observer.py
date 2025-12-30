"""
Observer Agent - Asynchronous Learning System

The Observer is a separate process that consumes telemetry events offline,
analyzes execution traces, determines root causes of failure/success,
and updates the Wisdom Database with learned lessons.
"""

import json
import os
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

from telemetry import EventStream, TelemetryEvent
from agent import MemorySystem

# Load environment variables
load_dotenv()


class ObserverAgent:
    """
    The Observer (Shadow Learner) that learns offline from execution traces.
    """
    
    def __init__(self,
                 wisdom_file: str = "system_instructions.json",
                 stream_file: str = "telemetry_events.jsonl",
                 checkpoint_file: str = "observer_checkpoint.json"):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.wisdom = MemorySystem(wisdom_file)
        self.event_stream = EventStream(stream_file)
        self.checkpoint_file = checkpoint_file
        
        # Model configuration - can use more powerful models for learning
        self.reflection_model = os.getenv("REFLECTION_MODEL", "gpt-4o-mini")
        self.evolution_model = os.getenv("EVOLUTION_MODEL", "gpt-4o-mini")
        self.score_threshold = float(os.getenv("SCORE_THRESHOLD", "0.8"))
        
        # Load checkpoint
        self.checkpoint = self._load_checkpoint()
    
    def _load_checkpoint(self) -> Dict[str, Any]:
        """Load the last processing checkpoint."""
        if os.path.exists(self.checkpoint_file):
            with open(self.checkpoint_file, 'r') as f:
                return json.load(f)
        return {
            "last_processed_timestamp": None,
            "lessons_learned": 0
        }
    
    def _save_checkpoint(self) -> None:
        """Save the current processing checkpoint."""
        with open(self.checkpoint_file, 'w') as f:
            json.dump(self.checkpoint, f, indent=2)
    
    def reflect(self, query: str, agent_response: str) -> Tuple[float, str]:
        """
        Evaluate the agent's response quality.
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
            return 0.5, f"Reflection error: {str(e)}"
    
    def evolve(self, critique: str, query: str, agent_response: str) -> str:
        """
        Generate improved system instructions based on critique.
        """
        current_instructions = self.wisdom.get_system_prompt()
        
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
            return current_instructions
    
    def analyze_trace(self, event: TelemetryEvent, verbose: bool = False) -> Optional[Dict[str, Any]]:
        """
        Analyze a single execution trace and determine if learning is needed.
        Returns analysis results or None if no learning needed.
        """
        if event.event_type != "task_complete":
            return None
        
        if not event.agent_response:
            return None
        
        if verbose:
            print(f"\n[OBSERVER] Analyzing trace from {event.timestamp}")
            print(f"Query: {event.query}")
        
        # Reflect on the execution
        score, critique = self.reflect(event.query, event.agent_response)
        
        if verbose:
            print(f"Score: {score:.2f}")
            print(f"Critique: {critique}")
        
        analysis = {
            "event": event,
            "score": score,
            "critique": critique,
            "needs_learning": score < self.score_threshold
        }
        
        return analysis
    
    def learn_from_analysis(self, analysis: Dict[str, Any], verbose: bool = False) -> bool:
        """
        Update the wisdom database based on analysis.
        Returns True if wisdom was updated.
        """
        if not analysis["needs_learning"]:
            if verbose:
                print("[OBSERVER] Score meets threshold, no learning needed")
            return False
        
        event = analysis["event"]
        
        if verbose:
            print(f"[OBSERVER] Learning from low-score execution (score: {analysis['score']:.2f})")
        
        # Evolve instructions
        new_instructions = self.evolve(
            analysis["critique"],
            event.query,
            event.agent_response
        )
        
        # Update wisdom database
        self.wisdom.update_instructions(new_instructions, analysis["critique"])
        
        if verbose:
            print(f"[OBSERVER] Updated wisdom database to version {self.wisdom.instructions['version']}")
        
        return True
    
    def process_events(self, verbose: bool = True) -> Dict[str, Any]:
        """
        Process all unprocessed events from the stream.
        This is the main offline learning loop.
        """
        if verbose:
            print("="*60)
            print("OBSERVER: Starting Event Processing")
            print("="*60)
        
        # Get unprocessed events
        last_timestamp = self.checkpoint.get("last_processed_timestamp")
        events = self.event_stream.read_unprocessed(last_timestamp)
        
        if not events:
            if verbose:
                print("\nNo new events to process.")
            return {
                "events_processed": 0,
                "lessons_learned": 0
            }
        
        if verbose:
            print(f"\nFound {len(events)} unprocessed events")
        
        results = {
            "events_processed": 0,
            "lessons_learned": 0,
            "analyses": []
        }
        
        # Process each event
        for event in events:
            analysis = self.analyze_trace(event, verbose=verbose)
            
            if analysis:
                results["analyses"].append(analysis)
                
                # Learn if needed
                if self.learn_from_analysis(analysis, verbose=verbose):
                    results["lessons_learned"] += 1
                    self.checkpoint["lessons_learned"] += 1
            
            results["events_processed"] += 1
        
        # Update checkpoint
        if events:
            self.checkpoint["last_processed_timestamp"] = events[-1].timestamp
            self._save_checkpoint()
        
        if verbose:
            print("\n" + "="*60)
            print("OBSERVER: Processing Complete")
            print("="*60)
            print(f"Events Processed: {results['events_processed']}")
            print(f"Lessons Learned: {results['lessons_learned']}")
            print(f"Wisdom Version: {self.wisdom.instructions['version']}")
        
        return results


def main():
    """Run the observer to process accumulated events."""
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not found in environment variables")
        print("Please create a .env file with your OpenAI API key")
        return
    
    print("Observer Agent - Offline Learning System")
    print("="*60)
    
    # Initialize observer
    observer = ObserverAgent()
    
    # Process all unprocessed events
    results = observer.process_events(verbose=True)
    
    print(f"\n\nSummary:")
    print(f"- Total events processed: {results['events_processed']}")
    print(f"- New lessons learned: {results['lessons_learned']}")
    print(f"- Total lessons learned (lifetime): {observer.checkpoint['lessons_learned']}")


if __name__ == "__main__":
    main()
