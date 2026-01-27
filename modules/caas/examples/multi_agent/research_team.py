"""
Multi-Agent Collaboration Example: Research Team

Demonstrates how multiple AI agents can collaborate using shared CaaS context.

Scenario:
- Researcher Agent: Investigates a topic using CaaS context
- Critic Agent: Reviews findings for accuracy and completeness
- Summarizer Agent: Creates final summary report

This example shows:
1. Shared context access across agents
2. Context-based agent coordination
3. Iterative refinement through multi-agent dialogue
"""

import sys
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from caas.storage.document_store import DocumentStore
from caas.enrichment import MetadataEnricher
from caas.triad import ContextTriad


@dataclass
class AgentMessage:
    """Message from an agent."""
    agent_name: str
    role: str
    content: str
    context_used: List[str]  # Which documents/chunks were referenced


class BaseAgent:
    """Base class for all agents."""
    
    def __init__(self, name: str, role: str, context_triad: ContextTriad):
        self.name = name
        self.role = role
        self.context_triad = context_triad
        self.conversation_history: List[AgentMessage] = []
    
    def add_to_history(self, message: AgentMessage):
        """Add a message to conversation history."""
        self.conversation_history.append(message)
    
    def get_context(self, query: str, context_type: str = "hot") -> Dict[str, Any]:
        """
        Retrieve context from CaaS based on query.
        
        Args:
            query: Query to retrieve context for
            context_type: Type of context (hot/warm/cold)
            
        Returns:
            Context dictionary with content and metadata
        """
        if context_type == "hot":
            context = self.context_triad.hot_context.get_context(query, max_tokens=2000)
        elif context_type == "warm":
            context = self.context_triad.warm_context.get_context(query, max_tokens=4000)
        else:  # cold
            context = self.context_triad.cold_context.get_context(query, max_tokens=8000)
        
        return context


class ResearcherAgent(BaseAgent):
    """Agent that conducts research using CaaS context."""
    
    def __init__(self, context_triad: ContextTriad):
        super().__init__("Dr. Research", "Researcher", context_triad)
    
    def investigate(self, topic: str) -> AgentMessage:
        """
        Investigate a topic using CaaS context.
        
        Args:
            topic: Research topic/question
            
        Returns:
            AgentMessage with findings
        """
        print(f"\n{'='*70}")
        print(f"🔬 {self.name} (Researcher): Investigating '{topic}'")
        print(f"{'='*70}")
        
        # Get hot context (most relevant, recent information)
        hot_context = self.get_context(topic, "hot")
        
        # Extract key findings
        findings = []
        sources_used = []
        
        for chunk in hot_context.get("chunks", [])[:3]:  # Top 3 chunks
            content = chunk.get("content", "")
            source = chunk.get("metadata", {}).get("source", "Unknown")
            sources_used.append(source)
            findings.append(f"- {content[:200]}... [Source: {source}]")
        
        # Simulate analysis
        analysis = f"""
Based on my investigation of '{topic}', I found:

{chr(10).join(findings)}

Key Insights:
- Found {len(hot_context.get('chunks', []))} relevant chunks
- Sources include: {', '.join(set(sources_used))}
- Context confidence: {hot_context.get('metadata', {}).get('confidence', 'N/A')}
"""
        
        message = AgentMessage(
            agent_name=self.name,
            role=self.role,
            content=analysis,
            context_used=sources_used
        )
        
        self.add_to_history(message)
        print(analysis)
        
        return message


class CriticAgent(BaseAgent):
    """Agent that reviews and critiques findings."""
    
    def __init__(self, context_triad: ContextTriad):
        super().__init__("Dr. Critique", "Critic", context_triad)
    
    def review(self, research_message: AgentMessage, topic: str) -> AgentMessage:
        """
        Review research findings for accuracy and completeness.
        
        Args:
            research_message: Message from researcher agent
            topic: Original research topic
            
        Returns:
            AgentMessage with review
        """
        print(f"\n{'='*70}")
        print(f"🎯 {self.name} (Critic): Reviewing research on '{topic}'")
        print(f"{'='*70}")
        
        # Get warm context (broader coverage) to verify claims
        warm_context = self.get_context(topic, "warm")
        
        # Check for additional relevant sources not mentioned
        research_sources = set(research_message.context_used)
        all_sources = set([
            chunk.get("metadata", {}).get("source", "Unknown")
            for chunk in warm_context.get("chunks", [])
        ])
        
        missing_sources = all_sources - research_sources
        
        # Simulate critique
        critique = f"""
REVIEW OF RESEARCH:

Strengths:
✓ Research covered {len(research_sources)} sources
✓ Used hot context (most relevant information)
✓ Findings are well-cited

Areas for Improvement:
"""
        
        if missing_sources:
            critique += f"⚠ Missing {len(missing_sources)} potentially relevant sources:\n"
            for source in list(missing_sources)[:3]:
                critique += f"  - {source}\n"
        else:
            critique += "✓ All major sources covered\n"
        
        # Check for conflicts in context
        has_conflicts = warm_context.get("metadata", {}).get("has_conflicts", False)
        if has_conflicts:
            critique += "⚠ WARNING: Detected conflicting information in sources\n"
            critique += "  Recommend cross-validation of key claims\n"
        else:
            critique += "✓ No major conflicts detected between sources\n"
        
        critique += f"\nRecommendation: {'APPROVED with minor revisions' if not has_conflicts else 'NEEDS REVISION'}"
        
        message = AgentMessage(
            agent_name=self.name,
            role=self.role,
            content=critique,
            context_used=list(all_sources)
        )
        
        self.add_to_history(message)
        print(critique)
        
        return message


class SummarizerAgent(BaseAgent):
    """Agent that creates final summary reports."""
    
    def __init__(self, context_triad: ContextTriad):
        super().__init__("Dr. Summary", "Summarizer", context_triad)
    
    def summarize(
        self,
        topic: str,
        research_msg: AgentMessage,
        critique_msg: AgentMessage
    ) -> AgentMessage:
        """
        Create final summary incorporating research and critique.
        
        Args:
            topic: Research topic
            research_msg: Message from researcher
            critique_msg: Message from critic
            
        Returns:
            AgentMessage with final summary
        """
        print(f"\n{'='*70}")
        print(f"📝 {self.name} (Summarizer): Creating final report on '{topic}'")
        print(f"{'='*70}")
        
        # Get cold context (comprehensive background)
        cold_context = self.get_context(topic, "cold")
        
        # Compile all sources
        all_sources = set(research_msg.context_used + critique_msg.context_used)
        
        summary = f"""
{'='*70}
FINAL RESEARCH REPORT: {topic}
{'='*70}

EXECUTIVE SUMMARY:
This report synthesizes findings from {len(all_sources)} sources, incorporating
feedback from peer review process.

RESEARCH FINDINGS:
{research_msg.content}

PEER REVIEW:
{critique_msg.content}

COMPREHENSIVE ANALYSIS:
Based on the complete context (Hot + Warm + Cold), including historical
information and background knowledge, the following conclusions are drawn:

- Topic thoroughly investigated using CaaS multi-tier context
- {len(cold_context.get('chunks', []))} total contextual chunks analyzed
- Findings cross-validated across multiple agents
- Recommendations incorporate peer feedback

METHODOLOGY:
1. Hot Context (Recent/Relevant): Initial research phase
2. Warm Context (Broader Coverage): Validation phase  
3. Cold Context (Comprehensive): Final synthesis phase
4. Multi-agent review for quality assurance

SOURCES CONSULTED:
{chr(10).join([f'- {s}' for s in sorted(all_sources)])}

CONFIDENCE: High (Multi-agent validation complete)
DATE: {cold_context.get('metadata', {}).get('timestamp', 'N/A')}
{'='*70}
"""
        
        message = AgentMessage(
            agent_name=self.name,
            role=self.role,
            content=summary,
            context_used=list(all_sources)
        )
        
        self.add_to_history(message)
        print(summary)
        
        return message


def multi_agent_research_workflow(topic: str):
    """
    Execute a multi-agent research workflow.
    
    Args:
        topic: Research topic/question
    """
    print("\n" + "="*70)
    print("MULTI-AGENT COLLABORATION DEMO")
    print("Context-as-a-Service: Shared Context Architecture")
    print("="*70)
    
    # Initialize document store (in real scenario, would be populated)
    doc_store = DocumentStore()
    
    # Create context triad (shared across all agents)
    context_triad = ContextTriad(doc_store)
    
    # Initialize agents
    researcher = ResearcherAgent(context_triad)
    critic = CriticAgent(context_triad)
    summarizer = SummarizerAgent(context_triad)
    
    # Execute workflow
    print(f"\nResearch Topic: {topic}")
    print("\nWorkflow: Researcher → Critic → Summarizer")
    print("All agents share the same CaaS context instance\n")
    
    # Step 1: Research
    research_findings = researcher.investigate(topic)
    
    # Step 2: Critique
    review = critic.review(research_findings, topic)
    
    # Step 3: Summarize
    final_report = summarizer.summarize(topic, research_findings, review)
    
    print("\n" + "="*70)
    print("WORKFLOW COMPLETE")
    print("="*70)
    print(f"\nTotal agents involved: 3")
    print(f"Total messages exchanged: 3")
    print(f"Shared context enabled seamless collaboration")
    print("="*70 + "\n")


if __name__ == "__main__":
    # Example usage
    topic = "How to implement the Trust Gateway for on-premises deployment?"
    
    print("""
    This demo shows how multiple AI agents can collaborate using CaaS:
    
    1. ResearcherAgent: Investigates using HOT context (most relevant)
    2. CriticAgent: Reviews using WARM context (broader coverage)
    3. SummarizerAgent: Synthesizes using COLD context (comprehensive)
    
    All agents share the same ContextTriad instance, enabling:
    - Consistent context across the team
    - No redundant context fetching
    - Collaborative refinement of findings
    """)
    
    # Run the workflow
    multi_agent_research_workflow(topic)
    
    print("""
    KEY BENEFITS OF MULTI-AGENT CaaS:
    
    ✓ Shared Context: All agents use the same context source
    ✓ Role Specialization: Each agent uses appropriate context tier
    ✓ Iterative Improvement: Findings refined through collaboration
    ✓ Source Tracking: All claims traceable to sources
    ✓ Efficiency: No redundant context fetching
    
    INTEGRATION WITH FRAMEWORKS:
    - AutoGen: Use CaaS as shared memory/context provider
    - LangGraph: Integrate as state management layer
    - CrewAI: Provide context for crew members
    """)
