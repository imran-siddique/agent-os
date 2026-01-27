# Agent OS Quickstart Script for Windows
# Run with: powershell -ExecutionPolicy Bypass -File quickstart.ps1

$ErrorActionPreference = "Stop"

Write-Host "[Agent OS] Quickstart" -ForegroundColor Cyan
Write-Host "======================"

# Check for Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[OK] Found $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python is required. Install from https://python.org" -ForegroundColor Red
    exit 1
}

# Install Agent OS
Write-Host ""
Write-Host "[*] Installing Agent OS..." -ForegroundColor Yellow
pip install --quiet agent-os
Write-Host "[OK] Agent OS installed" -ForegroundColor Green

# Create demo project
$DemoDir = "agent-os-demo"
Write-Host ""
Write-Host "[*] Creating demo project in .\$DemoDir" -ForegroundColor Yellow

New-Item -ItemType Directory -Path $DemoDir -Force | Out-Null
Set-Location $DemoDir

# Create agent.py
$AgentCode = @"
"""Agent OS Demo - Your First Governed Agent"""
import asyncio
from agent_os import KernelSpace

kernel = KernelSpace(policy="strict")

@kernel.register
async def my_agent(task: str) -> str:
    return f"Processed: {task.upper()}"

async def main():
    print("[Agent OS] Demo")
    print("=" * 40)
    result = await kernel.execute(my_agent, "Hello, Agent OS!")
    print(f"[OK] Result: {result}")
    print("")
    print("Success! Your agent ran safely under kernel governance!")

if __name__ == "__main__":
    asyncio.run(main())
"@

$AgentCode | Out-File -FilePath "agent.py" -Encoding ASCII

Write-Host "[OK] Created agent.py" -ForegroundColor Green

# Run the demo
Write-Host ""
Write-Host "[*] Running your first governed agent..." -ForegroundColor Yellow
Write-Host ""
python agent.py

Write-Host ""
Write-Host "[SUCCESS] Quickstart Complete!" -ForegroundColor Green
Write-Host "   Project: $(Get-Location)"
Write-Host "   Docs: https://agent-os.dev/docs"
