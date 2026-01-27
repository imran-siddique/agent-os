"""Integrations for Self-Correcting Agent Kernel (SCAK).

Layer 4 (Extension/Plugin) integrations:

1. Control Plane Integration (agent-control-plane)
   - SCAKExtension: Register SCAK as a Control Plane extension
   - MockControlPlane: For testing without the actual package

2. CMVK Integration (cmvk)
   - MockCMVKVerifier: For testing without the actual package
   - ProductionCMVKVerifier: For production with real CMVK

3. LangChain Integration (langchain)
   - SCAKMemory: SCAK-powered memory for LangChain
   - SelfCorrectingRunnable: Self-correcting chain wrapper

Usage:
    # With Control Plane
    from agent_control_plane import ControlPlane
    from scak.integrations import SCAKExtension
    
    cp = ControlPlane()
    scak = SCAKExtension()
    cp.register_extension(scak)
    
    # With CMVK
    from cmvk import Verifier
    from scak.integrations import ProductionCMVKVerifier
    
    verifier = ProductionCMVKVerifier(cmvk_client=Verifier())
"""

# Control Plane Integration
from .control_plane_adapter import (
    AgentOutcome,
    CorrectionPatch,
    MockControlPlane,
    SCAKExtension,
    ProductionControlPlaneAdapter,
    create_control_plane,
    create_scak_extension,
)

# CMVK Integration
from .cmvk_adapter import (
    VerificationOutcome,
    MockCMVKVerifier,
    ProductionCMVKVerifier,
    create_verifier,
)

# LangChain Integration
from .langchain_integration import (
    SCAKMemory,
    SCAKCallbackHandler,
    SelfCorrectingRunnable,
    create_scak_agent,
)

__all__ = [
    # Control Plane
    "AgentOutcome",
    "CorrectionPatch",
    "MockControlPlane",
    "SCAKExtension",
    "ProductionControlPlaneAdapter",
    "create_control_plane",
    "create_scak_extension",
    
    # CMVK
    "VerificationOutcome",
    "MockCMVKVerifier",
    "ProductionCMVKVerifier",
    "create_verifier",
    
    # LangChain
    "SCAKMemory",
    "SCAKCallbackHandler",
    "SelfCorrectingRunnable",
    "create_scak_agent",
]
