#!/usr/bin/env python3
"""
Agent A - User Agent

This is the initiating agent that starts the request chain.
It simulates a user request that will flow through Agent B to Agent C.
"""

from fastapi import FastAPI
import httpx
import sys

app = FastAPI()

AGENT_B_URL = "http://localhost:8010"  # Agent B (Summarizer)


@app.post("/request")
async def make_request(request: dict):
    """Forward user request to Agent B"""
    print(f"[Agent A] Received request: {request}", file=sys.stderr)
    
    # Forward to Agent B (Summarizer)
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{AGENT_B_URL}/summarize",
                json=request
            )
            result = response.json()
            print(f"[Agent A] Response from chain: {result}", file=sys.stderr)
            return result
        except Exception as e:
            print(f"[Agent A] Error: {e}", file=sys.stderr)
            return {"error": str(e), "agent": "A"}


if __name__ == "__main__":
    import uvicorn
    print("[Agent A] Starting User Agent on port 8009...")
    uvicorn.run(app, host="0.0.0.0", port=8009, log_level="info")
