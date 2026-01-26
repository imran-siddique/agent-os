#!/usr/bin/env python3
"""
Agent C - Database Agent

This agent simulates a database that can execute commands.
It should block dangerous commands when protected by IATP.
"""

from fastapi import FastAPI
import sys

app = FastAPI()


@app.post("/execute")
async def execute(request: dict):
    """Execute database command"""
    data = request.get("data", {})
    action = data.get("action", "SELECT")
    table = data.get("table", "unknown")
    
    print(f"[Agent C] Received command: {action} on table {table}", file=sys.stderr)
    
    # Check if this is a dangerous operation
    if action == "DELETE":
        if data.get("poison_injected"):
            print("[Agent C] ⚠️  DANGER: Poisoned DELETE command detected!", file=sys.stderr)
        print(f"[Agent C] 🔥 EXECUTING DELETE on table '{table}'", file=sys.stderr)
        return {
            "status": "success",
            "message": f"Deleted all rows from table '{table}'",
            "dangerous": True,
            "poison_injected": data.get("poison_injected", False)
        }
    else:
        print(f"[Agent C] ✅ Safe operation: {action}", file=sys.stderr)
        return {
            "status": "success",
            "message": f"Executed {action} on table '{table}'",
            "dangerous": False
        }


if __name__ == "__main__":
    import uvicorn
    print("[Agent C] Starting Database Agent on port 8011...")
    uvicorn.run(app, host="0.0.0.0", port=8011, log_level="info")
