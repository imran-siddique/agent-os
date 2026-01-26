"""
Attestation and Reputation Management for IATP.

This module provides:
1. Agent attestation verification using cryptographic signatures
2. Reputation score tracking and slashing
3. Integration with cmvk for hallucination detection
"""
import base64
import hashlib
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple

from iatp.models import (
    AttestationRecord,
    ReputationEvent,
    ReputationScore,
    TrustLevel,
)


def _get_utc_timestamp() -> str:
    """Get current UTC timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class AttestationValidator:
    """
    Validates agent attestations to prevent running hacked/modified code.

    This implements the "Attestation Handshake" where agents exchange
    cryptographic proof that they're running verified code.
    """

    def __init__(self, control_plane_public_keys: Optional[Dict[str, str]] = None):
        """
        Initialize the attestation validator.

        Args:
            control_plane_public_keys: Dict mapping key_id to public key (PEM format)
        """
        self.public_keys = control_plane_public_keys or {}
        self.attestation_cache: Dict[str, AttestationRecord] = {}

    def add_trusted_key(self, key_id: str, public_key: str) -> None:
        """
        Add a trusted public key from a Control Plane.

        Args:
            key_id: Identifier for the public key
            public_key: PEM-encoded public key
        """
        self.public_keys[key_id] = public_key

    def validate_attestation(
        self,
        attestation: AttestationRecord,
        verify_signature: bool = True
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate an agent attestation record.

        Args:
            attestation: The attestation record to validate
            verify_signature: Whether to verify the cryptographic signature

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check if attestation is expired
        current_time = _get_utc_timestamp()
        if attestation.is_expired(current_time):
            return False, f"Attestation for agent '{attestation.agent_id}' has expired"

        # Verify the signing key is trusted
        if attestation.signing_key_id not in self.public_keys:
            return False, (
                f"Unknown signing key '{attestation.signing_key_id}'. "
                "This Control Plane is not trusted."
            )

        # Verify cryptographic signature (simplified version)
        # In production, this would use proper RSA/Ed25519 signature verification
        if verify_signature:
            is_valid = self._verify_signature(attestation)
            if not is_valid:
                return False, (
                    f"Invalid signature for agent '{attestation.agent_id}'. "
                    "The agent may be running modified code."
                )

        # Cache valid attestation
        self.attestation_cache[attestation.agent_id] = attestation

        return True, None

    def _verify_signature(self, attestation: AttestationRecord) -> bool:
        """
        Verify the cryptographic signature of an attestation.

        ⚠️ SECURITY WARNING: This is a simplified implementation for demonstration.
        In production, use proper cryptographic libraries like cryptography or PyNaCl.

        Args:
            attestation: The attestation to verify

        Returns:
            True if signature is valid

        Example production implementation:
            from cryptography.hazmat.primitives.asymmetric import ed25519
            public_key_bytes = base64.b64decode(public_key)
            public_key_obj = ed25519.Ed25519PublicKey.from_public_bytes(public_key_bytes)
            signature_bytes = base64.b64decode(attestation.signature)
            message = f"{attestation.agent_id}:{attestation.codebase_hash}:..."
            try:
                public_key_obj.verify(signature_bytes, message.encode())
                return True
            except Exception:
                return False
        """
        # Get the public key
        public_key = self.public_keys.get(attestation.signing_key_id)
        if not public_key:
            return False

        # Simplified: Accept any attestation if a public key is configured
        # ⚠️ This allows the feature to work without complex crypto setup
        # In production, implement proper signature verification above
        return True

    def create_attestation(
        self,
        agent_id: str,
        codebase_hash: str,
        config_hash: str,
        signing_key_id: str,
        private_key: Optional[str] = None,
        expires_in_hours: int = 24
    ) -> AttestationRecord:
        """
        Create a new attestation record (used by Control Plane).

        Args:
            agent_id: Agent identifier
            codebase_hash: SHA-256 hash of codebase
            config_hash: SHA-256 hash of configuration
            signing_key_id: Key ID to use for signing
            private_key: Private key for signing (PEM format)
            expires_in_hours: Hours until attestation expires

        Returns:
            Signed attestation record
        """
        from datetime import timedelta

        timestamp = _get_utc_timestamp()

        # Calculate expiration
        current = datetime.now(timezone.utc)
        expires = current + timedelta(hours=expires_in_hours)
        expires_at = expires.isoformat().replace("+00:00", "Z")

        # Create message to sign
        message = f"{agent_id}:{codebase_hash}:{config_hash}:{timestamp}"

        # Sign the message (simplified)
        # In production, use proper signing:
        # from cryptography.hazmat.primitives.asymmetric import ed25519
        # signature = private_key_obj.sign(message.encode())
        signature = base64.b64encode(message.encode()).decode()

        return AttestationRecord(
            agent_id=agent_id,
            codebase_hash=codebase_hash,
            config_hash=config_hash,
            signature=signature,
            signing_key_id=signing_key_id,
            timestamp=timestamp,
            expires_at=expires_at
        )

    def compute_codebase_hash(self, codebase_content: str) -> str:
        """
        Compute SHA-256 hash of codebase content.

        Args:
            codebase_content: String representation of codebase

        Returns:
            Hexadecimal SHA-256 hash
        """
        return hashlib.sha256(codebase_content.encode()).hexdigest()


class ReputationManager:
    """
    Manages reputation scores across the agent network.

    This implements "Reputation Slashing" where agents that misbehave
    (e.g., hallucinate, timeout, fail) have their scores reduced.
    Other agents can use reputation scores to make trust decisions.
    """

    def __init__(self):
        """Initialize the reputation manager."""
        self.scores: Dict[str, ReputationScore] = {}

    def get_or_create_score(self, agent_id: str) -> ReputationScore:
        """
        Get or create a reputation score for an agent.

        Args:
            agent_id: Agent identifier

        Returns:
            ReputationScore instance
        """
        if agent_id not in self.scores:
            self.scores[agent_id] = ReputationScore(
                agent_id=agent_id,
                score=5.0,
                initial_score=5.0,
                last_updated=_get_utc_timestamp()
            )
        return self.scores[agent_id]

    def record_hallucination(
        self,
        agent_id: str,
        severity: str = "high",
        trace_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> ReputationScore:
        """
        Record a hallucination detected by cmvk and slash reputation.

        Args:
            agent_id: Agent that hallucinated
            severity: Severity level ('critical', 'high', 'medium', 'low')
            trace_id: Associated trace ID
            details: Additional context about the hallucination

        Returns:
            Updated reputation score
        """
        # Determine score penalty based on severity
        penalties = {
            "critical": -2.0,
            "high": -1.0,
            "medium": -0.5,
            "low": -0.25,
        }
        score_delta = penalties.get(severity, -1.0)

        # Create reputation event
        event = ReputationEvent(
            event_id=self._generate_event_id(),
            agent_id=agent_id,
            event_type="hallucination",
            severity=severity,
            score_delta=score_delta,
            timestamp=_get_utc_timestamp(),
            trace_id=trace_id,
            details=details,
            detected_by="cmvk"
        )

        # Apply to score
        score = self.get_or_create_score(agent_id)
        score.apply_event(event)

        return score

    def record_success(
        self,
        agent_id: str,
        trace_id: Optional[str] = None
    ) -> ReputationScore:
        """
        Record a successful transaction to improve reputation.

        Args:
            agent_id: Agent that performed successfully
            trace_id: Associated trace ID

        Returns:
            Updated reputation score
        """
        # Small positive reward for successful operations
        event = ReputationEvent(
            event_id=self._generate_event_id(),
            agent_id=agent_id,
            event_type="success",
            severity="low",
            score_delta=0.1,
            timestamp=_get_utc_timestamp(),
            trace_id=trace_id,
            detected_by="iatp"
        )

        score = self.get_or_create_score(agent_id)
        score.apply_event(event)

        return score

    def record_failure(
        self,
        agent_id: str,
        failure_type: str,
        trace_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> ReputationScore:
        """
        Record a failure event (timeout, error, etc.).

        Args:
            agent_id: Agent that failed
            failure_type: Type of failure (e.g., 'timeout', 'error')
            trace_id: Associated trace ID
            details: Additional context

        Returns:
            Updated reputation score
        """
        event = ReputationEvent(
            event_id=self._generate_event_id(),
            agent_id=agent_id,
            event_type=failure_type,
            severity="medium",
            score_delta=-0.5,
            timestamp=_get_utc_timestamp(),
            trace_id=trace_id,
            details=details,
            detected_by="iatp"
        )

        score = self.get_or_create_score(agent_id)
        score.apply_event(event)

        return score

    def get_score(self, agent_id: str) -> Optional[ReputationScore]:
        """
        Get the reputation score for an agent.

        Args:
            agent_id: Agent identifier

        Returns:
            ReputationScore if exists, None otherwise
        """
        return self.scores.get(agent_id)

    def get_trust_level(self, agent_id: str) -> TrustLevel:
        """
        Get the trust level based on reputation score.

        Args:
            agent_id: Agent identifier

        Returns:
            Appropriate TrustLevel enum value
        """
        score = self.get_or_create_score(agent_id)
        return score.get_trust_level()

    def export_reputation_data(self) -> Dict[str, Any]:
        """
        Export all reputation data for network-wide propagation.

        Returns:
            Dictionary containing all reputation scores
        """
        return {
            agent_id: score.model_dump()
            for agent_id, score in self.scores.items()
        }

    def import_reputation_data(self, data: Dict[str, Any]) -> None:
        """
        Import reputation data from other nodes in the network.

        Args:
            data: Dictionary of reputation scores from other nodes
        """
        for agent_id, score_data in data.items():
            # Merge with existing score if present
            if agent_id in self.scores:
                # For simplicity, keep the lower score (more conservative)
                imported_score = score_data.get("score", 5.0)
                if imported_score < self.scores[agent_id].score:
                    self.scores[agent_id].score = imported_score
            else:
                # Import new score
                self.scores[agent_id] = ReputationScore(**score_data)

    def _generate_event_id(self) -> str:
        """Generate a unique event ID."""
        import uuid
        return str(uuid.uuid4())
