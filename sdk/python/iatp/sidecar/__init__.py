"""
IATP Sidecar Proxy Server

This is the main sidecar that sits in front of an agent and handles:
- Capability manifest exchange
- Security validation
- Privacy checks
- Request routing
- Telemetry and tracing
"""
import time
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import httpx
from fastapi import FastAPI, HTTPException, Header, Request, Response
from fastapi.responses import JSONResponse

from iatp.models import (
    CapabilityManifest,
    QuarantineSession,
    TrustLevel,
)
from iatp.security import SecurityValidator, PrivacyScrubber
from iatp.telemetry import FlightRecorder, TraceIDGenerator, _get_utc_timestamp


class SidecarProxy:
    """
    The Sidecar Proxy that wraps an agent.
    
    Architecture:
    - External requests hit the sidecar (e.g., localhost:8001)
    - Sidecar validates, scrubs, and routes to the actual agent (e.g., localhost:8000)
    - All telemetry and security checks happen in the sidecar
    """
    
    def __init__(
        self,
        agent_url: str,
        manifest: CapabilityManifest,
        sidecar_host: str = "0.0.0.0",
        sidecar_port: int = 8001
    ):
        self.agent_url = agent_url
        self.manifest = manifest
        self.sidecar_host = sidecar_host
        self.sidecar_port = sidecar_port
        
        self.app = FastAPI(title=f"IATP Sidecar for {manifest.agent_id}")
        self.validator = SecurityValidator()
        self.scrubber = PrivacyScrubber()
        self.flight_recorder = FlightRecorder()
        self.quarantine_sessions: Dict[str, QuarantineSession] = {}
        
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup FastAPI routes."""
        
        @self.app.get("/.well-known/agent-manifest")
        async def get_manifest():
            """
            Return the capability manifest.
            This is the "handshake" endpoint.
            """
            return self.manifest.model_dump()
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            return {"status": "healthy", "agent_id": self.manifest.agent_id}
        
        @self.app.post("/proxy")
        async def proxy_request(
            request: Request,
            x_user_override: Optional[str] = Header(None),
            x_agent_trace_id: Optional[str] = Header(None)
        ):
            """
            Main proxy endpoint that forwards requests to the backend agent.
            
            Headers:
            - X-User-Override: Set to "true" to bypass security warnings
            - X-Agent-Trace-ID: Optional trace ID for distributed tracing
            """
            # Generate or use provided trace ID
            trace_id = x_agent_trace_id or TraceIDGenerator.generate()
            
            # Parse request body
            try:
                payload = await request.json()
            except Exception as e:
                return JSONResponse(
                    status_code=400,
                    content={"error": "Invalid JSON payload", "trace_id": trace_id}
                )
            
            # Validate privacy policy
            is_valid, error_message = self.validator.validate_privacy_policy(
                self.manifest, payload
            )
            
            if not is_valid:
                # BLOCK the request
                self.flight_recorder.log_blocked_request(
                    trace_id=trace_id,
                    agent_id=self.manifest.agent_id,
                    payload=payload,
                    reason=error_message,
                    manifest=self.manifest
                )
                return JSONResponse(
                    status_code=403,
                    content={
                        "error": error_message,
                        "trace_id": trace_id,
                        "blocked": True
                    }
                )
            
            # Check if warning is needed
            warning = self.validator.generate_warning_message(self.manifest, payload)
            should_quarantine = self.validator.should_quarantine(self.manifest)
            
            # If there's a warning and no user override, return the warning
            if warning and not x_user_override:
                trust_score = self.manifest.calculate_trust_score()
                return JSONResponse(
                    status_code=449,  # Custom status for "Retry With User Override"
                    content={
                        "warning": warning,
                        "trust_score": trust_score,
                        "requires_override": True,
                        "trace_id": trace_id,
                        "message": (
                            "This request requires user confirmation. "
                            "To proceed, retry with header 'X-User-Override: true'"
                        )
                    }
                )
            
            # Create quarantine session if needed
            if should_quarantine and x_user_override:
                session = QuarantineSession(
                    session_id=TraceIDGenerator.generate(),
                    trace_id=trace_id,
                    warning_message=warning or "Low trust agent",
                    user_override=True,
                    timestamp=_get_utc_timestamp(),
                    manifest=self.manifest
                )
                self.quarantine_sessions[trace_id] = session
                self.flight_recorder.log_user_override(
                    trace_id=trace_id,
                    agent_id=self.manifest.agent_id,
                    warning=warning or "Low trust agent",
                    quarantine_session=session
                )
            
            # Log the request
            self.flight_recorder.log_request(
                trace_id=trace_id,
                agent_id=self.manifest.agent_id,
                payload=payload,
                manifest=self.manifest,
                quarantined=should_quarantine
            )
            
            # Forward to backend agent
            start_time = time.time()
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        self.agent_url,
                        json=payload,
                        headers={
                            "X-Agent-Trace-ID": trace_id,
                            "Content-Type": "application/json"
                        },
                        timeout=30.0
                    )
                    latency_ms = (time.time() - start_time) * 1000
                    
                    # Log the response
                    try:
                        response_data = response.json() if 200 <= response.status_code < 300 else {}
                    except Exception:
                        response_data = {}
                    
                    self.flight_recorder.log_response(
                        trace_id=trace_id,
                        agent_id=self.manifest.agent_id,
                        response=response_data,
                        status_code=response.status_code,
                        latency_ms=latency_ms
                    )
                    
                    # Add tracing headers to response
                    headers = {
                        "X-Agent-Trace-ID": trace_id,
                        "X-Agent-Latency-Ms": str(int(latency_ms)),
                        "X-Agent-Trust-Score": str(self.manifest.calculate_trust_score())
                    }
                    
                    if should_quarantine:
                        headers["X-Agent-Quarantined"] = "true"
                    
                    return Response(
                        content=response.content,
                        status_code=response.status_code,
                        headers=headers,
                        media_type="application/json"
                    )
                    
            except httpx.TimeoutException:
                self.flight_recorder.log_error(
                    trace_id=trace_id,
                    agent_id=self.manifest.agent_id,
                    error="Request timeout",
                    details={"timeout_seconds": 30}
                )
                return JSONResponse(
                    status_code=504,
                    content={
                        "error": "Backend agent timeout",
                        "trace_id": trace_id
                    }
                )
            except Exception as e:
                self.flight_recorder.log_error(
                    trace_id=trace_id,
                    agent_id=self.manifest.agent_id,
                    error=str(e),
                    details={"exception_type": type(e).__name__}
                )
                return JSONResponse(
                    status_code=502,
                    content={
                        "error": f"Backend agent error: {str(e)}",
                        "trace_id": trace_id
                    }
                )
        
        @self.app.get("/trace/{trace_id}")
        async def get_trace(trace_id: str):
            """Retrieve flight recorder logs for a trace ID."""
            logs = self.flight_recorder.get_trace_logs(trace_id)
            if not logs:
                raise HTTPException(status_code=404, detail="Trace not found")
            return {"trace_id": trace_id, "logs": logs}
        
        @self.app.get("/quarantine/{trace_id}")
        async def get_quarantine_session(trace_id: str):
            """Get quarantine session info."""
            session = self.quarantine_sessions.get(trace_id)
            if not session:
                raise HTTPException(status_code=404, detail="Quarantine session not found")
            return session.model_dump()
    
    def run(self):
        """Run the sidecar server."""
        import uvicorn
        uvicorn.run(
            self.app,
            host=self.sidecar_host,
            port=self.sidecar_port
        )


def create_sidecar(
    agent_url: str,
    manifest: CapabilityManifest,
    host: str = "0.0.0.0",
    port: int = 8001
) -> SidecarProxy:
    """
    Factory function to create a sidecar proxy.
    
    Args:
        agent_url: URL of the backend agent (e.g., "http://localhost:8000")
        manifest: Capability manifest for this agent
        host: Host to bind the sidecar to
        port: Port to bind the sidecar to
    
    Returns:
        Configured SidecarProxy instance
    """
    return SidecarProxy(
        agent_url=agent_url,
        manifest=manifest,
        sidecar_host=host,
        sidecar_port=port
    )
