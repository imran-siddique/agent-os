"""GitHub App webhook handler with signature verification and API integration."""
import hashlib
import hmac
import json
import logging
import os
from typing import Any, Dict, Optional

from app import handle_pull_request, Review

logger = logging.getLogger(__name__)


class GitHubApp:
    """Handles GitHub webhook events with signature verification and API calls."""

    def __init__(
        self,
        app_id: Optional[str] = None,
        private_key: Optional[str] = None,
        webhook_secret: Optional[str] = None,
    ) -> None:
        self.app_id = app_id or os.environ.get("GITHUB_APP_ID")
        self.private_key = private_key or os.environ.get("GITHUB_APP_PRIVATE_KEY")
        self.webhook_secret = webhook_secret or os.environ.get("GITHUB_WEBHOOK_SECRET")

    def verify_signature(self, payload: bytes, signature: str) -> bool:
        """Verify X-Hub-Signature-256 header using HMAC SHA-256."""
        if not self.webhook_secret:
            logger.warning("No webhook secret configured — signature verification skipped")
            return False
        expected = "sha256=" + hmac.new(
            self.webhook_secret.encode(),
            payload,
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(expected, signature)

    def get_installation_token(self, installation_id: int) -> str:
        """Generate a JWT and exchange it for an installation access token."""
        from github import GithubIntegration

        integration = GithubIntegration(
            integration_id=int(self.app_id),
            private_key=self.private_key,
        )
        token = integration.get_access_token(installation_id).token
        return token

    def handle_webhook(self, headers: dict, body: bytes) -> dict:
        """Route a webhook event to the appropriate handler."""
        signature = headers.get("x-hub-signature-256", headers.get("X-Hub-Signature-256", ""))
        if not self.verify_signature(body, signature):
            return {"status": "error", "message": "Invalid signature"}

        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            return {"status": "error", "message": "Invalid JSON payload"}

        event_type = headers.get("x-github-event", headers.get("X-GitHub-Event", ""))

        if event_type == "ping":
            return {"status": "ok", "message": "pong"}

        if event_type == "pull_request":
            return self._handle_pull_request_event(payload)

        return {"status": "ok", "message": f"Event '{event_type}' ignored"}

    def _handle_pull_request_event(self, payload: dict) -> dict:
        """Process a pull_request webhook event."""
        action = payload.get("action", "")
        if action not in ("opened", "synchronize", "reopened"):
            return {"status": "ok", "message": f"Action '{action}' ignored"}

        try:
            from github import Github

            installation_id = payload["installation"]["id"]
            repo_full_name = payload["repository"]["full_name"]
            pr_number = payload["pull_request"]["number"]
            head_sha = payload["pull_request"]["head"]["sha"]

            token = self.get_installation_token(installation_id)
            gh = Github(token)
            repo = gh.get_repo(repo_full_name)
            pull = repo.get_pull(pr_number)

            # Fetch changed files
            files: Dict[str, str] = {}
            for f in pull.get_files():
                if f.status == "removed":
                    continue
                try:
                    content = repo.get_contents(f.filename, ref=head_sha)
                    files[f.filename] = content.decoded_content.decode("utf-8", errors="replace")
                except Exception:
                    logger.warning("Could not fetch content for %s", f.filename)

            # Fetch governance config
            config_yaml: Optional[str] = None
            try:
                cfg_file = repo.get_contents(".github/agent-governance.yml", ref=head_sha)
                config_yaml = cfg_file.decoded_content.decode("utf-8")
            except Exception:
                logger.info("No .github/agent-governance.yml found — using defaults")

            # Run analysis
            event = {"config_yaml": config_yaml, "files": files}
            review = handle_pull_request(event)

            # Post results
            self._post_review(gh, repo_full_name, pr_number, review)
            self._create_check_run(gh, repo_full_name, head_sha, review)

            return {
                "status": "ok",
                "message": f"Review posted on {repo_full_name}#{pr_number}",
                "conclusion": review.conclusion,
            }

        except Exception as exc:
            logger.exception("Error handling pull_request event")
            return {"status": "error", "message": str(exc)}

    def _post_review(self, gh, repo_name: str, pr_number: int, review: Review) -> None:
        """Post a PR review with inline comments."""
        try:
            repo = gh.get_repo(repo_name)
            pull = repo.get_pull(pr_number)

            event = "APPROVE" if review.conclusion == "approve" else "REQUEST_CHANGES"

            comments = []
            for c in review.comments:
                comments.append({
                    "path": c["path"],
                    "line": c["line"],
                    "body": c["body"],
                })

            pull.create_review(
                body=review.body,
                event=event,
                comments=comments,
            )
        except Exception:
            logger.exception("Failed to post review on %s#%d", repo_name, pr_number)

    def _create_check_run(self, gh, repo_name: str, head_sha: str, review: Review) -> None:
        """Create a check run summarizing the governance review."""
        try:
            repo = gh.get_repo(repo_name)
            conclusion = "success" if review.conclusion == "approve" else "failure"
            repo.create_check_run(
                name="Agent OS Governance",
                head_sha=head_sha,
                conclusion=conclusion,
                output={
                    "title": "Agent OS Governance Review",
                    "summary": review.body,
                },
            )
        except Exception:
            logger.exception("Failed to create check run on %s @ %s", repo_name, head_sha)


def create_webhook_app():
    """Create a FastAPI app with webhook endpoint."""
    from fastapi import FastAPI, Request
    from fastapi.responses import JSONResponse

    app = FastAPI(title="Agent OS Governance Bot")
    github_app = GitHubApp()

    @app.post("/webhook")
    async def webhook(request: Request):
        body = await request.body()
        headers = dict(request.headers)
        result = github_app.handle_webhook(headers, body)
        status_code = 200 if result["status"] == "ok" else 400
        return JSONResponse(content=result, status_code=status_code)

    @app.get("/health")
    async def health():
        return {"status": "healthy"}

    @app.get("/")
    async def info():
        return {
            "app": "Agent OS Governance Bot",
            "version": "1.0.0",
            "endpoints": ["/webhook", "/health"],
        }

    return app


if __name__ == "__main__":
    import uvicorn

    application = create_webhook_app()
    uvicorn.run(application, host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))
