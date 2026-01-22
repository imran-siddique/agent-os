"""
CMVK Command-Line Interface

Provides a user-friendly CLI for the Cross-Model Verification Kernel.
Usage: cmvk run --task "..." --generator gpt-4o --verifier gemini-1.5-pro
"""
import os
import sys
import json
import random
from pathlib import Path
from typing import Optional, Annotated
from enum import Enum

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint

# Import CMVK components
from . import __version__
from .core.kernel import VerificationKernel
from .core.types import KernelState
from .agents.generator_openai import OpenAIGenerator
from .agents.verifier_gemini import GeminiVerifier

app = typer.Typer(
    name="cmvk",
    help="Cross-Model Verification Kernel - Adversarial multi-model code verification",
    add_completion=True,
    no_args_is_help=True,
    rich_markup_mode="rich",
)
console = Console()


class GeneratorModel(str, Enum):
    """Available generator models."""
    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_4_TURBO = "gpt-4-turbo"
    O1 = "o1"
    O1_MINI = "o1-mini"
    O3_MINI = "o3-mini"


class VerifierModel(str, Enum):
    """Available verifier models."""
    GEMINI_15_PRO = "gemini-1.5-pro"
    GEMINI_15_FLASH = "gemini-1.5-flash"
    GEMINI_20_FLASH = "gemini-2.0-flash"
    CLAUDE_35_SONNET = "claude-3-5-sonnet-20241022"
    CLAUDE_35_HAIKU = "claude-3-5-haiku-20241022"


class OutputFormat(str, Enum):
    """Output format options."""
    PRETTY = "pretty"
    JSON = "json"
    MINIMAL = "minimal"


def version_callback(value: bool) -> None:
    """Display version information."""
    if value:
        console.print(f"[bold blue]CMVK[/bold blue] version [green]{__version__}[/green]")
        console.print("Cross-Model Verification Kernel")
        console.print("https://github.com/imran-siddique/cross-model-verification-kernel")
        raise typer.Exit()


def set_seed(seed: Optional[int]) -> None:
    """Set random seeds for reproducibility."""
    if seed is not None:
        random.seed(seed)
        try:
            import numpy as np
            np.random.seed(seed)
        except ImportError:
            pass
        console.print(f"[dim]Random seed set to: {seed}[/dim]")


@app.callback()
def main(
    version: Annotated[
        bool,
        typer.Option(
            "--version", "-v",
            help="Show version and exit.",
            callback=version_callback,
            is_eager=True,
        ),
    ] = False,
) -> None:
    """
    [bold blue]CMVK[/bold blue] - Cross-Model Verification Kernel
    
    Adversarial multi-model verification for AI code generation.
    
    [dim]"Trust, but Verify (with a different brain)."[/dim]
    """
    pass


@app.command()
def run(
    task: Annotated[
        str,
        typer.Option(
            "--task", "-t",
            help="The task or problem description for code generation.",
        ),
    ],
    generator: Annotated[
        GeneratorModel,
        typer.Option(
            "--generator", "-g",
            help="Generator model to use.",
        ),
    ] = GeneratorModel.GPT_4O,
    verifier: Annotated[
        VerifierModel,
        typer.Option(
            "--verifier", "-V",
            help="Verifier model to use.",
        ),
    ] = VerifierModel.GEMINI_15_PRO,
    max_loops: Annotated[
        int,
        typer.Option(
            "--max-loops", "-l",
            help="Maximum verification loops.",
            min=1,
            max=20,
        ),
    ] = 5,
    confidence: Annotated[
        float,
        typer.Option(
            "--confidence", "-c",
            help="Minimum confidence threshold to accept solution.",
            min=0.0,
            max=1.0,
        ),
    ] = 0.85,
    output: Annotated[
        OutputFormat,
        typer.Option(
            "--output", "-o",
            help="Output format.",
        ),
    ] = OutputFormat.PRETTY,
    trace: Annotated[
        bool,
        typer.Option(
            "--trace",
            help="Enable trace logging for debugging/research.",
        ),
    ] = False,
    seed: Annotated[
        Optional[int],
        typer.Option(
            "--seed", "-s",
            help="Random seed for reproducibility.",
        ),
    ] = None,
    config: Annotated[
        Optional[Path],
        typer.Option(
            "--config",
            help="Path to configuration file.",
            exists=True,
            dir_okay=False,
        ),
    ] = None,
    temperature_generator: Annotated[
        float,
        typer.Option(
            "--temp-gen",
            help="Temperature for generator model.",
            min=0.0,
            max=2.0,
        ),
    ] = 0.7,
    temperature_verifier: Annotated[
        float,
        typer.Option(
            "--temp-ver",
            help="Temperature for verifier model.",
            min=0.0,
            max=2.0,
        ),
    ] = 0.3,
) -> None:
    """
    Run the verification kernel on a task.
    
    Example:
        cmvk run --task "Write a function to find the longest palindromic substring"
    """
    # Set seed for reproducibility
    set_seed(seed)
    
    # Validate API keys
    if not os.getenv("OPENAI_API_KEY"):
        console.print("[red]Error:[/red] OPENAI_API_KEY environment variable not set.")
        raise typer.Exit(1)
    
    if verifier.value.startswith("gemini") and not os.getenv("GOOGLE_API_KEY"):
        console.print("[red]Error:[/red] GOOGLE_API_KEY environment variable not set.")
        raise typer.Exit(1)
    
    if verifier.value.startswith("claude") and not os.getenv("ANTHROPIC_API_KEY"):
        console.print("[red]Error:[/red] ANTHROPIC_API_KEY environment variable not set.")
        raise typer.Exit(1)
    
    # Display configuration
    if output == OutputFormat.PRETTY:
        console.print(Panel.fit(
            f"[bold]Task:[/bold] {task}\n"
            f"[bold]Generator:[/bold] {generator.value} (temp={temperature_generator})\n"
            f"[bold]Verifier:[/bold] {verifier.value} (temp={temperature_verifier})\n"
            f"[bold]Max Loops:[/bold] {max_loops}\n"
            f"[bold]Confidence:[/bold] {confidence}",
            title="[bold blue]CMVK Configuration[/bold blue]",
            border_style="blue",
        ))
    
    try:
        # Initialize agents
        gen_agent = OpenAIGenerator(
            model_name=generator.value,
            temperature=temperature_generator,
        )
        
        # Choose verifier based on model
        if verifier.value.startswith("gemini"):
            ver_agent = GeminiVerifier(
                model_name=verifier.value,
                temperature=temperature_verifier,
            )
        elif verifier.value.startswith("claude"):
            # Import Anthropic verifier if available
            try:
                from .agents.verifier_anthropic import AnthropicVerifier
                ver_agent = AnthropicVerifier(
                    model_name=verifier.value,
                    temperature=temperature_verifier,
                )
            except ImportError:
                console.print("[red]Error:[/red] Anthropic verifier not available.")
                raise typer.Exit(1)
        else:
            console.print(f"[red]Error:[/red] Unknown verifier model: {verifier.value}")
            raise typer.Exit(1)
        
        # Initialize kernel
        config_path = str(config) if config else "config/settings.yaml"
        kernel = VerificationKernel(
            generator=gen_agent,
            verifier=ver_agent,
            config_path=config_path if Path(config_path).exists() else None,
            enable_trace_logging=trace,
        )
        
        # Override config
        kernel.max_loops = max_loops
        kernel.confidence_threshold = confidence
        
        # Execute with progress indicator
        if output == OutputFormat.PRETTY:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                progress.add_task("Running verification loop...", total=None)
                result: KernelState = kernel.execute(task)
        else:
            result: KernelState = kernel.execute(task)
        
        # Display results
        _display_result(result, output)
        
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        if trace:
            console.print_exception()
        raise typer.Exit(1)


def _display_result(result: KernelState, output_format: OutputFormat) -> None:
    """Display the verification result."""
    if output_format == OutputFormat.JSON:
        output = {
            "success": result.is_complete,
            "loops": result.current_loop,
            "solution": result.final_result,
            "verification_count": len(result.verification_history),
        }
        console.print(json.dumps(output, indent=2))
    
    elif output_format == OutputFormat.MINIMAL:
        if result.is_complete and result.final_result:
            console.print(result.final_result)
        else:
            console.print("[red]Verification failed[/red]")
    
    else:  # PRETTY
        # Result panel
        status = "[green]✓ Success[/green]" if result.is_complete else "[red]✗ Failed[/red]"
        console.print()
        console.print(Panel.fit(
            f"[bold]Status:[/bold] {status}\n"
            f"[bold]Loops:[/bold] {result.current_loop}\n"
            f"[bold]Verifications:[/bold] {len(result.verification_history)}",
            title="[bold blue]Result[/bold blue]",
            border_style="green" if result.is_complete else "red",
        ))
        
        # Solution
        if result.final_result:
            console.print()
            console.print("[bold]Solution:[/bold]")
            syntax = Syntax(result.final_result, "python", theme="monokai", line_numbers=True)
            console.print(syntax)


@app.command()
def config(
    show: Annotated[
        bool,
        typer.Option("--show", "-s", help="Show current configuration."),
    ] = False,
    init: Annotated[
        bool,
        typer.Option("--init", "-i", help="Initialize default configuration file."),
    ] = False,
    path: Annotated[
        Path,
        typer.Option("--path", "-p", help="Configuration file path."),
    ] = Path("config/settings.yaml"),
) -> None:
    """
    Manage CMVK configuration.
    """
    if show:
        if path.exists():
            with open(path) as f:
                content = f.read()
            syntax = Syntax(content, "yaml", theme="monokai", line_numbers=True)
            console.print(Panel(syntax, title=f"[bold]{path}[/bold]"))
        else:
            console.print(f"[yellow]Config file not found:[/yellow] {path}")
    
    elif init:
        default_config = """# Cross-Model Verification Kernel Configuration
# Generated by: cmvk config --init

# API Keys (Use environment variables in production)
api_keys:
  openai_key: ${OPENAI_API_KEY}
  google_key: ${GOOGLE_API_KEY}
  anthropic_key: ${ANTHROPIC_API_KEY}

# Model Configuration
models:
  generator:
    provider: "openai"
    model_name: "gpt-4o"
    temperature: 0.7
    max_tokens: 2000
    
  verifier:
    provider: "google"
    model_name: "gemini-1.5-pro"
    temperature: 0.3
    max_tokens: 2000

# Kernel Configuration
kernel:
  max_loops: 5
  confidence_threshold: 0.85
  enable_graph_memory: true
  enable_runtime_testing: true
  seed: null  # Set for reproducibility

# Sandbox Configuration
sandbox:
  timeout_seconds: 30
  memory_limit_mb: 512
  enable_docker: false

# Logging
logging:
  level: "INFO"
  log_file: "logs/cmvk.log"
"""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            f.write(default_config)
        console.print(f"[green]✓[/green] Configuration initialized at: {path}")
    
    else:
        console.print("Use --show to display config or --init to create default config.")


@app.command()
def benchmark(
    dataset: Annotated[
        str,
        typer.Option("--dataset", "-d", help="Dataset to run benchmark on."),
    ] = "humaneval_sample",
    generator: Annotated[
        GeneratorModel,
        typer.Option("--generator", "-g", help="Generator model."),
    ] = GeneratorModel.GPT_4O,
    verifier: Annotated[
        VerifierModel,
        typer.Option("--verifier", "-V", help="Verifier model."),
    ] = VerifierModel.GEMINI_15_PRO,
    output_dir: Annotated[
        Path,
        typer.Option("--output-dir", "-o", help="Output directory for results."),
    ] = Path("experiments/results"),
    seed: Annotated[
        Optional[int],
        typer.Option("--seed", "-s", help="Random seed for reproducibility."),
    ] = 42,
) -> None:
    """
    Run benchmark experiments on standard datasets.
    
    Example:
        cmvk benchmark --dataset humaneval_50 --generator gpt-4o --verifier gemini-1.5-pro
    """
    set_seed(seed)
    
    console.print(Panel.fit(
        f"[bold]Dataset:[/bold] {dataset}\n"
        f"[bold]Generator:[/bold] {generator.value}\n"
        f"[bold]Verifier:[/bold] {verifier.value}\n"
        f"[bold]Seed:[/bold] {seed}",
        title="[bold blue]Benchmark Configuration[/bold blue]",
        border_style="blue",
    ))
    
    # Load dataset
    dataset_path = Path(f"experiments/datasets/{dataset}.json")
    if not dataset_path.exists():
        console.print(f"[red]Error:[/red] Dataset not found: {dataset_path}")
        console.print("Available datasets: humaneval_sample, humaneval_50, humaneval_full, sabotage")
        raise typer.Exit(1)
    
    with open(dataset_path) as f:
        problems = json.load(f)
    
    console.print(f"[dim]Loaded {len(problems)} problems from {dataset}[/dim]")
    console.print("[yellow]Benchmark execution not fully implemented yet.[/yellow]")
    console.print("Use 'python experiments/experiment_runner.py' for full benchmarks.")


@app.command()
def visualize(
    trace_file: Annotated[
        Path,
        typer.Argument(help="Path to trace JSON file."),
    ],
    format: Annotated[
        str,
        typer.Option("--format", "-f", help="Output format (html, png, terminal)."),
    ] = "terminal",
) -> None:
    """
    Visualize a verification trace.
    
    Example:
        cmvk visualize logs/traces/demo_HumanEval_0.json
    """
    if not trace_file.exists():
        console.print(f"[red]Error:[/red] Trace file not found: {trace_file}")
        raise typer.Exit(1)
    
    with open(trace_file) as f:
        trace = json.load(f)
    
    # Display trace summary
    table = Table(title="Verification Trace Summary")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Task ID", trace.get("task_id", "N/A"))
    table.add_row("Task", trace.get("task_description", "N/A")[:50] + "...")
    table.add_row("Total Loops", str(trace.get("total_loops", 0)))
    table.add_row("Success", str(trace.get("success", False)))
    table.add_row("Generator", trace.get("generator_model", "N/A"))
    table.add_row("Verifier", trace.get("verifier_model", "N/A"))
    
    console.print(table)
    
    # Show conversation trace
    if "conversation_trace" in trace:
        console.print("\n[bold]Conversation Trace:[/bold]")
        for i, entry in enumerate(trace["conversation_trace"][:10]):  # Limit to first 10
            console.print(f"  {i+1}. [{entry.get('type', 'unknown')}] Loop {entry.get('loop', '?')}")


@app.command()
def models() -> None:
    """
    List available models for generator and verifier.
    """
    # Generator models table
    gen_table = Table(title="Generator Models (OpenAI)")
    gen_table.add_column("Model", style="cyan")
    gen_table.add_column("Description", style="white")
    
    gen_table.add_row("gpt-4o", "GPT-4o - Fast, capable, multimodal")
    gen_table.add_row("gpt-4o-mini", "GPT-4o Mini - Smaller, faster, cheaper")
    gen_table.add_row("gpt-4-turbo", "GPT-4 Turbo - High capability")
    gen_table.add_row("o1", "o1 - Advanced reasoning")
    gen_table.add_row("o1-mini", "o1 Mini - Efficient reasoning")
    gen_table.add_row("o3-mini", "o3 Mini - Latest reasoning model")
    
    console.print(gen_table)
    console.print()
    
    # Verifier models table
    ver_table = Table(title="Verifier Models")
    ver_table.add_column("Model", style="cyan")
    ver_table.add_column("Provider", style="yellow")
    ver_table.add_column("Description", style="white")
    
    ver_table.add_row("gemini-1.5-pro", "Google", "Gemini 1.5 Pro - High capability")
    ver_table.add_row("gemini-1.5-flash", "Google", "Gemini 1.5 Flash - Fast")
    ver_table.add_row("gemini-2.0-flash", "Google", "Gemini 2.0 Flash - Latest")
    ver_table.add_row("claude-3-5-sonnet-20241022", "Anthropic", "Claude 3.5 Sonnet")
    ver_table.add_row("claude-3-5-haiku-20241022", "Anthropic", "Claude 3.5 Haiku - Fast")
    
    console.print(ver_table)


if __name__ == "__main__":
    app()
