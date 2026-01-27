# Agent OS Quickstart Script for Windows
# Run with: iwr -useb https://get.agent-os.dev/win | iex

$ErrorActionPreference = "Stop"

Write-Host "🛡️  Agent OS Quickstart" -ForegroundColor Cyan
Write-Host "========================"

# Check for Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Found $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python is required. Install from https://python.org" -ForegroundColor Red
    exit 1
}

# Install Agent OS
Write-Host "`n📦 Installing Agent OS..." -ForegroundColor Yellow
pip install --quiet agent-os
Write-Host "✅ Agent OS installed" -ForegroundColor Green

# Create demo project
$DEMO_DIR = "agent-os-demo"
Write-Host "`n📁 Creating demo project in .\$DEMO_DIR" -ForegroundColor Yellow

New-Item -ItemType Directory -Path $DEMO_DIR -Force | Out-Null
Set-Location $DEMO_DIR

# Create agent.py
@'
"""Agent OS Demo - Your First Governed Agent"""
import asyncio
from agent_os import KernelSpace

kernel = KernelSpace(policy="strict")

@kernel.register
async def my_agent(task: str) -> str:
    return f"Processed: {task.upper()}"

async def main():
    print("🛡️  Agent OS Demo")
    print("=" * 40)
    result = await kernel.execute(my_agent, "Hello, Agent OS!")
    print(f"✅ Result: {result}")
    print("\n🎉 Your agent ran safely under kernel governance!")

if __name__ == "__main__":
    asyncio.run(main())
'@ | Out-File -FilePath "agent.py" -Encoding UTF8

Write-Host "✅ Created agent.py" -ForegroundColor Green

# Run the demo
Write-Host "`n🚀 Running your first governed agent...`n" -ForegroundColor Yellow
python agent.py

Write-Host "`n🎉 Quickstart Complete!" -ForegroundColor Green
Write-Host "   Project: $(Get-Location)"
Write-Host "   Docs: https://agent-os.dev/docs"
