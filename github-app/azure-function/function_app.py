"""Azure Functions webhook handler for Agent OS Governance Bot."""
import json
import logging
import sys
from pathlib import Path

import azure.functions as func

# Ensure the parent directory is importable so webhook/app modules resolve
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from webhook import GitHubApp

logger = logging.getLogger(__name__)

app = func.FunctionApp()


@app.function_name(name="governance-webhook")
@app.route(route="webhook", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def webhook_handler(req: func.HttpRequest) -> func.HttpResponse:
    """Handle incoming GitHub webhook events."""
    try:
        headers = dict(req.headers)
        body = req.get_body()

        github_app = GitHubApp()
        result = github_app.handle_webhook(headers, body)

        status_code = 200 if result["status"] == "ok" else 400
        return func.HttpResponse(
            body=json.dumps(result),
            status_code=status_code,
            mimetype="application/json",
        )
    except Exception as exc:
        logger.exception("Unhandled error in webhook handler")
        return func.HttpResponse(
            body=json.dumps({"status": "error", "message": str(exc)}),
            status_code=500,
            mimetype="application/json",
        )


@app.function_name(name="governance-health")
@app.route(route="health", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def health_handler(req: func.HttpRequest) -> func.HttpResponse:
    """Health check endpoint."""
    return func.HttpResponse(
        body=json.dumps({"status": "healthy"}),
        status_code=200,
        mimetype="application/json",
    )
