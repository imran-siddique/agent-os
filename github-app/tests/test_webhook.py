"""Tests for GitHub App webhook handler."""
import hashlib
import hmac
import json

import pytest
from unittest.mock import MagicMock, patch, PropertyMock

from webhook import GitHubApp, create_webhook_app

try:
    from fastapi.testclient import TestClient
except ImportError:
    TestClient = None  # type: ignore[misc,assignment]


# =====================================================================
# Helpers
# =====================================================================

WEBHOOK_SECRET = "test-secret-key-12345"


def _sign(payload: bytes, secret: str = WEBHOOK_SECRET) -> str:
    """Compute X-Hub-Signature-256 for a payload."""
    return "sha256=" + hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()


def _pr_payload(action: str = "opened") -> dict:
    """Minimal pull_request webhook payload."""
    return {
        "action": action,
        "installation": {"id": 12345},
        "repository": {"full_name": "owner/repo"},
        "pull_request": {
            "number": 42,
            "head": {"sha": "abc123"},
        },
    }


# =====================================================================
# TestSignatureVerification
# =====================================================================


class TestSignatureVerification:
    """Tests for HMAC signature verification."""

    def test_valid_signature_passes(self):
        app = GitHubApp(webhook_secret=WEBHOOK_SECRET)
        payload = b'{"action": "opened"}'
        sig = _sign(payload)
        assert app.verify_signature(payload, sig) is True

    def test_invalid_signature_rejected(self):
        app = GitHubApp(webhook_secret=WEBHOOK_SECRET)
        payload = b'{"action": "opened"}'
        assert app.verify_signature(payload, "sha256=invalid") is False

    def test_missing_secret_logs_warning_returns_false(self):
        app = GitHubApp(webhook_secret=None)
        # Clear env var to ensure it's truly None
        app.webhook_secret = None
        payload = b'{"action": "opened"}'
        assert app.verify_signature(payload, "sha256=anything") is False

    def test_empty_signature_rejected(self):
        app = GitHubApp(webhook_secret=WEBHOOK_SECRET)
        payload = b'{"action": "opened"}'
        assert app.verify_signature(payload, "") is False


# =====================================================================
# TestWebhookRouting
# =====================================================================


class TestWebhookRouting:
    """Tests for event routing in handle_webhook."""

    def test_ping_event_returns_pong(self):
        app = GitHubApp(webhook_secret=WEBHOOK_SECRET)
        payload = b'{"zen": "test"}'
        headers = {
            "x-github-event": "ping",
            "x-hub-signature-256": _sign(payload),
        }
        result = app.handle_webhook(headers, payload)
        assert result["status"] == "ok"
        assert result["message"] == "pong"

    def test_unknown_event_ignored(self):
        app = GitHubApp(webhook_secret=WEBHOOK_SECRET)
        payload = b'{"action": "created"}'
        headers = {
            "x-github-event": "issues",
            "x-hub-signature-256": _sign(payload),
        }
        result = app.handle_webhook(headers, payload)
        assert result["status"] == "ok"
        assert "ignored" in result["message"].lower()

    def test_pull_request_event_routes_to_handler(self):
        app = GitHubApp(webhook_secret=WEBHOOK_SECRET)
        pr = _pr_payload("closed")
        body = json.dumps(pr).encode()
        headers = {
            "x-github-event": "pull_request",
            "x-hub-signature-256": _sign(body),
        }
        result = app.handle_webhook(headers, body)
        assert result["status"] == "ok"
        assert "closed" in result["message"].lower()

    def test_invalid_signature_returns_error(self):
        app = GitHubApp(webhook_secret=WEBHOOK_SECRET)
        payload = b'{"action": "opened"}'
        headers = {
            "x-github-event": "pull_request",
            "x-hub-signature-256": "sha256=bad",
        }
        result = app.handle_webhook(headers, payload)
        assert result["status"] == "error"

    def test_invalid_json_returns_error(self):
        app = GitHubApp(webhook_secret=WEBHOOK_SECRET)
        payload = b"not json"
        headers = {
            "x-github-event": "pull_request",
            "x-hub-signature-256": _sign(payload),
        }
        result = app.handle_webhook(headers, payload)
        assert result["status"] == "error"
        assert "json" in result["message"].lower()


# =====================================================================
# TestPREventHandling
# =====================================================================


class TestPREventHandling:
    """Tests for _handle_pull_request_event action filtering."""

    def test_opened_action_processed(self):
        app = GitHubApp(webhook_secret=WEBHOOK_SECRET)
        payload = _pr_payload("opened")
        with patch.object(app, "get_installation_token", return_value="fake-token"):
            with patch("github.Github") as mock_gh:
                mock_repo = MagicMock()
                mock_pull = MagicMock()
                mock_pull.get_files.return_value = []
                mock_repo.get_pull.return_value = mock_pull
                mock_repo.get_contents.side_effect = Exception("not found")
                mock_gh.return_value.get_repo.return_value = mock_repo
                result = app._handle_pull_request_event(payload)
        assert result["status"] == "ok"

    def test_synchronize_action_processed(self):
        app = GitHubApp(webhook_secret=WEBHOOK_SECRET)
        payload = _pr_payload("synchronize")
        with patch.object(app, "get_installation_token", return_value="fake-token"):
            with patch("github.Github") as mock_gh:
                mock_repo = MagicMock()
                mock_pull = MagicMock()
                mock_pull.get_files.return_value = []
                mock_repo.get_pull.return_value = mock_pull
                mock_repo.get_contents.side_effect = Exception("not found")
                mock_gh.return_value.get_repo.return_value = mock_repo
                result = app._handle_pull_request_event(payload)
        assert result["status"] == "ok"

    def test_closed_action_ignored(self):
        app = GitHubApp(webhook_secret=WEBHOOK_SECRET)
        payload = _pr_payload("closed")
        result = app._handle_pull_request_event(payload)
        assert result["status"] == "ok"
        assert "ignored" in result["message"].lower()

    def test_labeled_action_ignored(self):
        app = GitHubApp(webhook_secret=WEBHOOK_SECRET)
        payload = _pr_payload("labeled")
        result = app._handle_pull_request_event(payload)
        assert result["status"] == "ok"
        assert "ignored" in result["message"].lower()


# =====================================================================
# TestWebhookApp
# =====================================================================


@pytest.mark.skipif(TestClient is None, reason="fastapi not installed")
class TestWebhookApp:
    """Tests for the FastAPI application."""

    def _get_client(self):
        app = create_webhook_app()
        return TestClient(app)

    def test_health_endpoint(self):
        client = self._get_client()
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_info_endpoint(self):
        client = self._get_client()
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "Agent OS" in data["app"]
        assert "/webhook" in data["endpoints"]

    @patch.object(GitHubApp, "handle_webhook", return_value={"status": "ok", "message": "pong"})
    def test_webhook_endpoint_valid(self, mock_handle):
        client = self._get_client()
        response = client.post(
            "/webhook",
            content=b'{"zen": "test"}',
            headers={
                "x-github-event": "ping",
                "x-hub-signature-256": "sha256=abc",
                "content-type": "application/json",
            },
        )
        assert response.status_code == 200

    @patch.object(
        GitHubApp, "handle_webhook",
        return_value={"status": "error", "message": "Invalid signature"},
    )
    def test_webhook_endpoint_invalid_signature(self, mock_handle):
        client = self._get_client()
        response = client.post(
            "/webhook",
            content=b'{}',
            headers={
                "x-github-event": "pull_request",
                "x-hub-signature-256": "sha256=bad",
                "content-type": "application/json",
            },
        )
        assert response.status_code == 400
