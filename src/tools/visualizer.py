#!/usr/bin/env python3
"""
Visualizer: Replay JSON traces as an adversarial debate.

This tool reads JSON trace files from the TraceLogger and displays them
as a human-readable script showing the debate between:
- The Builder (GPT-4o): Generates solutions
- The Prosecutor (Gemini): Finds flaws
- The Kernel: Makes final decisions

Usage:
    python -m src.tools.visualizer <trace_file.json>
    python -m src.tools.visualizer logs/traces/cmvk_prob_001_*.json
    python -m src.tools.visualizer --list
    python -m src.tools.visualizer --latest
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, Any, List
import glob


# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
    # Role-specific colors
    BUILDER = '\033[94m'      # Blue for GPT-4o (Builder)
    PROSECUTOR = '\033[91m'   # Red for Gemini (Prosecutor)
    KERNEL = '\033[93m'       # Yellow for Kernel (Arbiter)
    SUCCESS = '\033[92m'      # Green for success
    SYSTEM = '\033[96m'       # Cyan for system messages


def print_separator(char="=", length=80):
    """Print a separator line."""
    print(char * length)


def print_header(text: str):
    """Print a formatted header."""
    print_separator()
    print(f"{Colors.BOLD}{Colors.HEADER}{text.center(80)}{Colors.ENDC}")
    print_separator()


def print_speaker(role: str, message: str, color: str):
    """Print a message from a specific role/speaker."""
    print(f"\n{color}{Colors.BOLD}>>> {role}:{Colors.ENDC} {color}{message}{Colors.ENDC}")


def print_code_block(code: str, indent: int = 4):
    """Print a code block with indentation."""
    lines = code.strip().split('\n')
    for line in lines:
        print(f"{' ' * indent}{Colors.OKCYAN}{line}{Colors.ENDC}")


def format_strategy(strategy: str) -> str:
    """Format strategy name for display."""
    if not strategy or strategy == "unknown":
        return "Unknown Strategy"
    return strategy.replace("_", " ").title()


def replay_trace(trace_data: Dict[str, Any], speed: float = 0.5, show_code: bool = True):
    """
    Replay a trace as an adversarial debate.
    
    Args:
        trace_data: Parsed JSON trace data
        speed: Delay in seconds between messages (0 = instant)
        show_code: Whether to show full code blocks
    """
    # Print header
    print_header("🎭 ADVERSARIAL KERNEL REPLAY 🎭")
    
    # Print problem statement
    print(f"\n{Colors.BOLD}📋 Problem:{Colors.ENDC}")
    print(f"    {trace_data['input_query']}")
    
    # Print metadata
    meta = trace_data.get('meta', {})
    print(f"\n{Colors.BOLD}📊 Execution Summary:{Colors.ENDC}")
    print(f"    Total Attempts: {meta.get('total_attempts', len(trace_data['history']))}")
    print(f"    Final Status: {meta.get('final_status', 'unknown').upper()}")
    print(f"    Timestamp: {meta.get('timestamp', 'N/A')}")
    
    if trace_data.get('forbidden_strategies'):
        print(f"    Banned Strategies: {', '.join(format_strategy(s) for s in trace_data['forbidden_strategies'])}")
    
    print_separator("-")
    print(f"\n{Colors.SYSTEM}🎬 Beginning replay...{Colors.ENDC}\n")
    time.sleep(speed)
    
    # Replay each step in the history
    history = trace_data.get('history', [])
    
    for i, step in enumerate(history, 1):
        print_separator("─")
        print(f"\n{Colors.BOLD}🔄 Round {step.get('step_id', i)} of {len(history)}{Colors.ENDC}")
        time.sleep(speed)
        
        # Builder generates solution
        strategy = step.get('strategy_used', 'unknown')
        print_speaker(
            "GPT-4o (The Builder)",
            f"I'll solve this using {format_strategy(strategy)}...",
            Colors.BUILDER
        )
        time.sleep(speed * 0.5)
        
        if show_code:
            code = step.get('code_generated', '')
            if code:
                print(f"\n{Colors.BOLD}    Generated Solution:{Colors.ENDC}")
                print_code_block(code)
                time.sleep(speed)
        
        # Prosecutor reviews
        feedback = step.get('verifier_feedback', '')
        status = step.get('status', 'unknown')
        
        if status == "failed":
            print_speaker(
                "Gemini (The Prosecutor)",
                feedback,
                Colors.PROSECUTOR
            )
            time.sleep(speed)
            
            # Kernel decision
            print_speaker(
                "Kernel (The Arbiter)",
                f"⚖️  Objection Sustained. Solution REJECTED.",
                Colors.KERNEL
            )
            
            # Check if strategy was banned
            if strategy in trace_data.get('forbidden_strategies', []):
                time.sleep(speed * 0.5)
                print_speaker(
                    "Kernel (The Arbiter)",
                    f"🚫 Strategy '{format_strategy(strategy)}' is now BANNED from future attempts.",
                    Colors.KERNEL
                )
        
        elif status == "success":
            print_speaker(
                "Gemini (The Prosecutor)",
                feedback,
                Colors.SUCCESS
            )
            time.sleep(speed)
            
            print_speaker(
                "Kernel (The Arbiter)",
                "✅ Verification PASSED. Solution ACCEPTED.",
                Colors.KERNEL
            )
        
        time.sleep(speed)
    
    # Print final result
    print_separator("=")
    print(f"\n{Colors.BOLD}🏁 FINAL RESULT{Colors.ENDC}")
    print_separator("=")
    
    final_status = meta.get('final_status', 'unknown')
    if final_status == "solved":
        print(f"\n{Colors.SUCCESS}{Colors.BOLD}✅ SUCCESS:{Colors.ENDC} {Colors.SUCCESS}The Adversarial Kernel found a verified solution!{Colors.ENDC}")
        print(f"\n{Colors.BOLD}Final Solution (Verified):{Colors.ENDC}")
        if trace_data.get('current_code'):
            print_code_block(trace_data['current_code'])
    else:
        print(f"\n{Colors.FAIL}{Colors.BOLD}❌ FAILED:{Colors.ENDC} {Colors.FAIL}Max retries reached without finding a verified solution.{Colors.ENDC}")
    
    # Summary statistics
    print(f"\n{Colors.BOLD}📈 Statistics:{Colors.ENDC}")
    failed_count = sum(1 for step in history if step.get('status') == 'failed')
    success_count = sum(1 for step in history if step.get('status') == 'success')
    print(f"    Attempts: {len(history)}")
    print(f"    Failed: {failed_count}")
    print(f"    Succeeded: {success_count}")
    
    if trace_data.get('forbidden_strategies'):
        print(f"    Banned Strategies: {len(trace_data['forbidden_strategies'])}")
        for strategy in trace_data['forbidden_strategies']:
            print(f"        - {format_strategy(strategy)}")
    
    print_separator("=")


def list_traces(traces_dir: str = "logs/traces") -> List[Path]:
    """List all trace files in the traces directory."""
    trace_path = Path(traces_dir)
    if not trace_path.exists():
        print(f"{Colors.FAIL}Error: Traces directory '{traces_dir}' not found.{Colors.ENDC}")
        return []
    
    trace_files = sorted(trace_path.glob("*.json"))
    return trace_files


def get_latest_trace(traces_dir: str = "logs/traces") -> Path:
    """Get the most recent trace file."""
    trace_files = list_traces(traces_dir)
    if not trace_files:
        return None
    return max(trace_files, key=lambda p: p.stat().st_mtime)


def load_trace(filepath: str) -> Dict[str, Any]:
    """Load and parse a trace JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"{Colors.FAIL}Error: File '{filepath}' not found.{Colors.ENDC}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"{Colors.FAIL}Error: Invalid JSON in '{filepath}': {e}{Colors.ENDC}")
        sys.exit(1)


def main():
    """Main entry point for the visualizer CLI."""
    parser = argparse.ArgumentParser(
        description="Replay JSON traces as adversarial debates",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m src.tools.visualizer logs/traces/cmvk_prob_001.json
  python -m src.tools.visualizer --list
  python -m src.tools.visualizer --latest
  python -m src.tools.visualizer trace.json --speed 1.0 --no-code
        """
    )
    
    parser.add_argument(
        'trace_file',
        nargs='?',
        help='Path to the trace JSON file (supports wildcards)'
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='List all available trace files'
    )
    parser.add_argument(
        '--latest',
        action='store_true',
        help='Replay the most recent trace file'
    )
    parser.add_argument(
        '--speed',
        type=float,
        default=0.5,
        help='Playback speed in seconds between messages (default: 0.5, use 0 for instant)'
    )
    parser.add_argument(
        '--no-code',
        action='store_true',
        help='Hide code blocks in the output'
    )
    parser.add_argument(
        '--traces-dir',
        default='logs/traces',
        help='Directory containing trace files (default: logs/traces)'
    )
    
    args = parser.parse_args()
    
    # Handle --list option
    if args.list:
        trace_files = list_traces(args.traces_dir)
        if not trace_files:
            print("No trace files found.")
            return
        
        print(f"\n{Colors.BOLD}Available Trace Files:{Colors.ENDC}")
        for i, trace_file in enumerate(trace_files, 1):
            mtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(trace_file.stat().st_mtime))
            size = trace_file.stat().st_size
            print(f"  {i}. {trace_file.name}")
            print(f"     Modified: {mtime} | Size: {size} bytes")
        return
    
    # Handle --latest option
    if args.latest:
        latest = get_latest_trace(args.traces_dir)
        if not latest:
            print(f"{Colors.FAIL}No trace files found in '{args.traces_dir}'.{Colors.ENDC}")
            return
        trace_file = str(latest)
        print(f"{Colors.SYSTEM}Loading latest trace: {latest.name}{Colors.ENDC}\n")
    elif args.trace_file:
        # Handle wildcards
        if '*' in args.trace_file or '?' in args.trace_file:
            matches = glob.glob(args.trace_file)
            if not matches:
                print(f"{Colors.FAIL}No files matching pattern '{args.trace_file}'{Colors.ENDC}")
                return
            trace_file = matches[0]
            if len(matches) > 1:
                print(f"{Colors.WARNING}Multiple files match pattern. Using: {trace_file}{Colors.ENDC}\n")
        else:
            trace_file = args.trace_file
    else:
        parser.print_help()
        return
    
    # Load and replay the trace
    trace_data = load_trace(trace_file)
    replay_trace(trace_data, speed=args.speed, show_code=not args.no_code)


if __name__ == "__main__":
    main()
