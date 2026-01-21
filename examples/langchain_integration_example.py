"""
Example: LangChain Integration with Self-Correcting Agent Kernel (SCAK).

This example demonstrates how to integrate SCAK with a LangChain agent to enable:
1. Automatic laziness detection
2. Dynamic memory management with 3-Tier hierarchy
3. Runtime failure handling and self-correction

Requirements:
    pip install langchain langchain-core langchain-openai scak
"""

import os
from typing import List

# LangChain imports
try:
    from langchain.agents import AgentExecutor, create_openai_tools_agent
    from langchain_openai import ChatOpenAI
    from langchain.tools import Tool
    from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
    LANGCHAIN_AVAILABLE = True
except ImportError:
    print("LangChain not available. Install with: pip install langchain langchain-core langchain-openai")
    LANGCHAIN_AVAILABLE = False

# SCAK imports
from src.integrations.langchain_integration import (
    SCAKMemory,
    SCAKCallbackHandler,
    SelfCorrectingRunnable,
    create_scak_agent
)


# ============================================================================
# Example 1: Basic Integration - Add SCAK to existing LangChain agent
# ============================================================================

def example_basic_integration():
    """
    Basic example: Add SCAK monitoring to an existing LangChain agent.
    
    This adds laziness detection without changing the agent logic.
    """
    if not LANGCHAIN_AVAILABLE:
        print("Skipping example - LangChain not available")
        return
    
    print("=" * 80)
    print("EXAMPLE 1: Basic SCAK Integration")
    print("=" * 80)
    
    # 1. Create standard LangChain components
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    
    # Define some tools
    def search_logs(query: str) -> str:
        """Search application logs."""
        # Simulate tool that sometimes returns empty
        if "error_500" in query.lower():
            return ""  # Empty result - might trigger laziness
        return f"Found 5 log entries for: {query}"
    
    tools = [
        Tool(
            name="search_logs",
            func=search_logs,
            description="Search application logs for a query"
        )
    ]
    
    # 2. Initialize SCAK Callback Handler
    scak_handler = SCAKCallbackHandler(agent_id="example_agent")
    
    # 3. Create agent with standard prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant that searches logs."),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    agent = create_openai_tools_agent(llm, tools, prompt)
    
    # 4. Create executor with SCAK callback
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        callbacks=[scak_handler],  # Add SCAK monitoring
        verbose=True
    )
    
    # 5. Run agent
    print("\n>>> Running agent with SCAK monitoring...")
    
    try:
        result = agent_executor.invoke({
            "input": "Find logs for error_500"
        })
        print(f"\nResult: {result['output']}")
    except Exception as e:
        print(f"\nError: {e}")
    
    # 6. Check statistics
    print(f"\n📊 SCAK Statistics:")
    print(f"   Total executions: {scak_handler.total_executions}")
    print(f"   Give-up signals detected: {scak_handler.give_up_count}")
    print(f"   Audits triggered: {scak_handler.audit_count}")


# ============================================================================
# Example 2: Full Integration - SCAK Memory + Callbacks + Self-Correction
# ============================================================================

def example_full_integration():
    """
    Full example: Use all SCAK components for maximum reliability.
    
    This includes:
    - SCAKMemory for dynamic context injection
    - SCAKCallbackHandler for laziness detection
    - SelfCorrectingRunnable for runtime error handling
    """
    if not LANGCHAIN_AVAILABLE:
        print("Skipping example - LangChain not available")
        return
    
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Full SCAK Integration")
    print("=" * 80)
    
    # 1. Initialize SCAK Components
    scak_memory = SCAKMemory()
    scak_handler = SCAKCallbackHandler(agent_id="full_example_agent")
    
    # 2. Create LangChain agent with SCAK memory
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    
    # Define tools
    def search_database(query: str) -> str:
        """Search database."""
        if "user_123" in query:
            return "User found: John Doe"
        return ""  # Empty result
    
    def execute_query(sql: str) -> str:
        """Execute SQL query."""
        # Simulate occasional failure
        if "DROP" in sql.upper():
            raise PermissionError("DROP TABLE is not allowed")
        return f"Query executed: {sql}"
    
    tools = [
        Tool(name="search_database", func=search_database, 
             description="Search database for records"),
        Tool(name="execute_query", func=execute_query,
             description="Execute SQL query")
    ]
    
    # 3. Create prompt with SCAK memory placeholder
    prompt = ChatPromptTemplate.from_messages([
        ("system", "{system_patch}\n\nYou are a database assistant."),
        MessagesPlaceholder(variable_name="history"),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    agent = create_openai_tools_agent(llm, tools, prompt)
    
    # 4. Create executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=scak_memory,  # Use SCAK memory
        callbacks=[scak_handler],  # Add SCAK monitoring
        verbose=True
    )
    
    # 5. Wrap with self-correction
    correcting_agent = SelfCorrectingRunnable(
        agent=agent_executor,
        agent_id="full_example_agent"
    )
    
    # 6. Test scenarios
    test_cases = [
        "Find user_123 in the database",
        "Search for user_999",  # Will likely give up
        "Execute: SELECT * FROM users",  # Should work
        # "Execute: DROP TABLE users",  # Would trigger correction
    ]
    
    print("\n>>> Running test scenarios with full SCAK integration...")
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"\n--- Test {i}: {test_input} ---")
        try:
            # Load memory variables manually for demo
            memory_vars = scak_memory.load_memory_variables({
                "input": test_input,
                "tools": tools
            })
            
            # Prepare input with memory
            full_input = {
                "input": test_input,
                "system_patch": memory_vars["system_patch"],
                "history": memory_vars["history"]
            }
            
            result = correcting_agent.invoke(full_input)
            print(f"✓ Result: {result.get('output', result)[:100]}")
            
            # Save context
            scak_memory.save_context(
                {"input": test_input},
                {"output": str(result)}
            )
            
        except Exception as e:
            print(f"✗ Error: {type(e).__name__}: {e}")
    
    # 7. Print statistics
    print(f"\n📊 Final Statistics:")
    print(f"   Agent executions: {correcting_agent.execution_count}")
    print(f"   Failures detected: {correcting_agent.failure_count}")
    print(f"   Auto-corrections: {correcting_agent.correction_count}")
    print(f"   Give-up signals: {scak_handler.give_up_count}")
    print(f"   Shadow audits: {scak_handler.audit_count}")
    print(f"   Chat history length: {len(scak_memory.chat_history)}")


# ============================================================================
# Example 3: Convenience Function - Quick Setup
# ============================================================================

def example_convenience_function():
    """
    Convenience example: Use create_scak_agent for quick setup.
    
    This is the easiest way to add SCAK to an existing agent.
    """
    if not LANGCHAIN_AVAILABLE:
        print("Skipping example - LangChain not available")
        return
    
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Quick Setup with create_scak_agent()")
    print("=" * 80)
    
    # 1. Create base agent (standard LangChain)
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    
    def analyze_logs(query: str) -> str:
        """Analyze logs."""
        return f"Analysis: {query}"
    
    tools = [Tool(name="analyze_logs", func=analyze_logs,
                  description="Analyze application logs")]
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a log analysis assistant."),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    agent = create_openai_tools_agent(llm, tools, prompt)
    base_agent = AgentExecutor(agent=agent, tools=tools, verbose=True)
    
    # 2. Wrap with SCAK in one line!
    scak_agent = create_scak_agent(
        base_agent,
        callback_handler=SCAKCallbackHandler(),
        enable_correction=True,
        agent_id="convenience_agent"
    )
    
    # 3. Use normally
    print("\n>>> Running SCAK-enabled agent...")
    
    try:
        result = scak_agent.invoke({
            "input": "Analyze recent error logs"
        })
        print(f"\n✓ Result: {result.get('output', result)[:100]}")
    except Exception as e:
        print(f"\n✗ Error: {e}")
    
    print("\n✨ SCAK integration complete with just one function call!")


# ============================================================================
# Main
# ============================================================================

def main():
    """Run all examples."""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   LangChain Integration Examples for Self-Correcting Agent Kernel (SCAK)    ║
║                                                                              ║
║   These examples demonstrate three integration patterns:                    ║
║   1. Basic: Add laziness monitoring to existing agents                      ║
║   2. Full: Use all SCAK components for maximum reliability                  ║
║   3. Convenience: Quick setup with create_scak_agent()                      ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    if not LANGCHAIN_AVAILABLE:
        print("⚠️  LangChain is not installed.")
        print("   Install with: pip install langchain langchain-core langchain-openai")
        print("   Then set OPENAI_API_KEY environment variable.")
        return
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  OPENAI_API_KEY environment variable not set.")
        print("   Set it with: export OPENAI_API_KEY='your-key'")
        print("\n   Running examples in mock mode...")
    
    # Run examples
    try:
        example_basic_integration()
        example_full_integration()
        example_convenience_function()
    except Exception as e:
        print(f"\n❌ Example failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("✅ All examples completed!")
    print("=" * 80)


if __name__ == "__main__":
    main()
