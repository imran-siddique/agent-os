"""
IATP CLI - Command Line Interface for Inter-Agent Trust Protocol

Provides developer tools to:
- Validate capability_manifest.json files
- Scan agents for trust scores
- Test IATP configurations
"""
import json
import sys

import click
import httpx

from iatp import __version__
from iatp.models import CapabilityManifest, RetentionPolicy, ReversibilityLevel, TrustLevel


@click.group()
@click.version_option(version=__version__, prog_name="iatp")
def cli():
    """
    IATP CLI - Inter-Agent Trust Protocol Developer Tools

    Validate manifests, scan agents, and test trust configurations.
    """
    pass


@cli.command()
@click.argument('manifest_path', type=click.Path(exists=True))
@click.option('--verbose', '-v', is_flag=True, help='Show detailed validation output')
def verify(manifest_path: str, verbose: bool):
    """
    Validate a capability_manifest.json file.

    Checks for:
    - Valid JSON schema
    - Logical contradictions (e.g., retention: forever + privacy: strict)
    - Required fields
    - Enum value validity

    Example:
        iatp verify ./manifest.json
    """
    click.echo(f"🔍 Validating manifest: {manifest_path}")

    try:
        # Load the manifest file
        with open(manifest_path) as f:
            manifest_data = json.load(f)

        if verbose:
            click.echo("\n📄 Raw manifest data:")
            click.echo(json.dumps(manifest_data, indent=2))

        # Validate using Pydantic model
        try:
            manifest = CapabilityManifest(**manifest_data)
        except Exception as e:
            click.echo("\n❌ Schema validation failed:", err=True)
            click.echo(f"   {str(e)}", err=True)
            sys.exit(1)

        # Perform logical contradiction checks
        errors = []
        warnings = []

        # Check 1: Retention policy vs. privacy expectations
        if manifest.privacy_contract.retention == RetentionPolicy.PERMANENT:
            if manifest.trust_level in [TrustLevel.VERIFIED_PARTNER, TrustLevel.STANDARD]:
                warnings.append(
                    "⚠️  Permanent retention with trusted agent - consider ephemeral or temporary"
                )

        # Check 2: Reversibility vs. trust level
        if manifest.capabilities.reversibility == ReversibilityLevel.NONE:
            if manifest.trust_level == TrustLevel.UNTRUSTED:
                errors.append(
                    "❌ Untrusted agent with no reversibility is a high-risk configuration"
                )

        # Check 3: Human review with high trust
        if manifest.privacy_contract.human_review:
            if manifest.trust_level == TrustLevel.VERIFIED_PARTNER:
                warnings.append(
                    "⚠️  Human review enabled for verified partner - may not be necessary"
                )

        # Calculate trust score
        trust_score = manifest.calculate_trust_score()

        # Display results
        if errors:
            click.echo(f"\n❌ Validation failed with {len(errors)} error(s):")
            for error in errors:
                click.echo(f"   {error}")
            sys.exit(1)

        click.echo("\n✅ Schema validation passed")
        click.echo(f"   Agent ID: {manifest.agent_id}")
        click.echo(f"   Trust Level: {manifest.trust_level.value}")
        click.echo(f"   Trust Score: {trust_score}/10")

        if warnings:
            click.echo(f"\n⚠️  {len(warnings)} warning(s):")
            for warning in warnings:
                click.echo(f"   {warning}")

        if verbose:
            click.echo("\n📊 Detailed Analysis:")
            click.echo(f"   Reversibility: {manifest.capabilities.reversibility.value}")
            click.echo(f"   Idempotency: {manifest.capabilities.idempotency}")
            if manifest.capabilities.rate_limit:
                click.echo(f"   Rate Limit: {manifest.capabilities.rate_limit} req/min")
            if manifest.capabilities.sla_latency:
                click.echo(f"   SLA Latency: {manifest.capabilities.sla_latency}")
            if manifest.capabilities.undo_window:
                click.echo(f"   Undo Window: {manifest.capabilities.undo_window}")
            click.echo(f"   Retention: {manifest.privacy_contract.retention.value}")
            click.echo(f"   Human Review: {manifest.privacy_contract.human_review}")

        click.echo("\n✨ Manifest is valid and ready to use!")

    except FileNotFoundError:
        click.echo(f"❌ File not found: {manifest_path}", err=True)
        sys.exit(1)
    except json.JSONDecodeError as e:
        click.echo(f"❌ Invalid JSON: {str(e)}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Validation error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('agent_url')
@click.option('--timeout', '-t', default=10, help='Request timeout in seconds')
@click.option('--verbose', '-v', is_flag=True, help='Show detailed scan output')
def scan(agent_url: str, timeout: int, verbose: bool):
    """
    Scan an agent's capabilities endpoint and return a trust score.

    Pings the agent's /.well-known/agent-manifest endpoint and
    analyzes the exposed guarantees to calculate a trust score (0-100).

    Example:
        iatp scan http://localhost:8001
        iatp scan https://api.example.com/agent --timeout 30
    """
    click.echo(f"🔍 Scanning agent: {agent_url}")

    # Ensure URL has scheme
    if not agent_url.startswith(('http://', 'https://')):
        agent_url = f"http://{agent_url}"

    # Construct manifest endpoint URL
    manifest_url = f"{agent_url.rstrip('/')}/.well-known/agent-manifest"

    try:
        # Fetch the manifest
        with httpx.Client(timeout=timeout) as client:
            if verbose:
                click.echo(f"📡 Fetching: {manifest_url}")

            response = client.get(manifest_url)
            response.raise_for_status()

            manifest_data = response.json()

            if verbose:
                click.echo("\n📄 Received manifest:")
                click.echo(json.dumps(manifest_data, indent=2))

        # Parse into CapabilityManifest
        manifest = CapabilityManifest(**manifest_data)

        # Calculate trust score (0-10 scale, convert to 0-100)
        trust_score_10 = manifest.calculate_trust_score()
        trust_score_100 = int(trust_score_10 * 10)

        # Determine risk level
        if trust_score_100 >= 80:
            risk_level = "🟢 LOW"
            risk_emoji = "✅"
        elif trust_score_100 >= 50:
            risk_level = "🟡 MEDIUM"
            risk_emoji = "⚠️"
        else:
            risk_level = "🔴 HIGH"
            risk_emoji = "❌"

        # Display results
        click.echo(f"\n{risk_emoji} Trust Score: {trust_score_100}/100 ({risk_level})")
        click.echo("\n📊 Agent Profile:")
        click.echo(f"   Agent ID: {manifest.agent_id}")
        click.echo(f"   Trust Level: {manifest.trust_level.value}")
        click.echo(f"   Reversibility: {manifest.capabilities.reversibility.value}")
        click.echo(f"   Data Retention: {manifest.privacy_contract.retention.value}")

        # Security indicators
        click.echo("\n🔒 Security Indicators:")
        click.echo(f"   {'✅' if manifest.capabilities.idempotency else '❌'} Idempotent operations")
        click.echo(f"   {'✅' if manifest.capabilities.reversibility != ReversibilityLevel.NONE else '❌'} Reversibility support")
        click.echo(f"   {'✅' if manifest.privacy_contract.retention != RetentionPolicy.PERMANENT else '❌'} Limited data retention")
        click.echo(f"   {'⚠️' if manifest.privacy_contract.human_review else '✅'} {'Human review enabled' if manifest.privacy_contract.human_review else 'Automated processing'}")

        # Recommendations
        if trust_score_100 < 50:
            click.echo("\n⚠️  Recommendations:")
            click.echo("   • This agent has a low trust score")
            click.echo("   • Use X-User-Override: true header to proceed")
            click.echo("   • Avoid sending sensitive data")
            click.echo("   • Monitor quarantine logs")

        if verbose:
            click.echo("\n📈 Performance Guarantees:")
            if manifest.capabilities.rate_limit:
                click.echo(f"   Rate Limit: {manifest.capabilities.rate_limit} req/min")
            if manifest.capabilities.sla_latency:
                click.echo(f"   SLA Latency: {manifest.capabilities.sla_latency}")

    except httpx.TimeoutException:
        click.echo(f"\n❌ Request timeout after {timeout}s", err=True)
        click.echo("   Agent may be down or unreachable", err=True)
        sys.exit(1)
    except httpx.HTTPStatusError as e:
        click.echo(f"\n❌ HTTP {e.response.status_code}: {e.response.reason_phrase}", err=True)
        if e.response.status_code == 404:
            click.echo("   Manifest endpoint not found", err=True)
            click.echo(f"   Expected: {manifest_url}", err=True)
        sys.exit(1)
    except httpx.RequestError as e:
        click.echo(f"\n❌ Connection error: {str(e)}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"\n❌ Scan error: {str(e)}", err=True)
        if verbose:
            import traceback
            click.echo(traceback.format_exc(), err=True)
        sys.exit(1)


@cli.command()
def version():
    """Show IATP version information."""
    click.echo(f"IATP CLI v{__version__}")
    click.echo("Inter-Agent Trust Protocol")
    click.echo("https://github.com/imran-siddique/inter-agent-trust-protocol")


if __name__ == '__main__':
    cli()
