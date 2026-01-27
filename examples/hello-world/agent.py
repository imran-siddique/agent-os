"""
Hello World - Agent OS

The simplest possible governed agent.
Run with: python agent.py
"""

import asyncio
from agent_os import KernelSpace

# Create kernel with strict policy
kernel = KernelSpace(policy="strict")


@kernel.register
async def hello_agent(name: str) -> str:
    """A simple agent that says hello - safely."""
    
    # This works fine
    message = f"Hello from a governed agent, {name}!"
    
    # Uncomment to test policy enforcement:
    # import os
    # os.system("echo dangerous")  # SIGKILL!
    
    return message


async def main():
    print("🚀 Hello World Agent")
    print("=" * 20)
    
    # Execute the agent through the kernel
    result = await kernel.execute(hello_agent, "World")
    
    print(f"✅ Agent executed successfully")
    print(f"📤 Result: {result}")


if __name__ == "__main__":
    asyncio.run(main())
