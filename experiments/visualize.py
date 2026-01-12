"""
Visualization Module for Mute Agent Benchmarks

Generates charts showing the "Cost of Curiosity":
- Cost vs. Ambiguity chart
- Token efficiency comparisons
- Latency comparisons

Key insight from PRD:
"Mute Agent is a flat line (cost is constant).
Interactive Agent cost explodes as ambiguity rises."
"""

import json
import sys
import os
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib not available. Install with: pip install matplotlib")


@dataclass
class AmbiguityDataPoint:
    """A data point for the Cost vs. Ambiguity chart."""
    ambiguity_level: float  # 0.0 to 1.0 (0% to 100%)
    mute_tokens: int
    interactive_tokens: int
    scenario_title: str


def generate_cost_vs_ambiguity_chart(
    results: List[Dict[str, Any]],
    output_path: str = "cost_vs_ambiguity.png",
    title: str = "The Cost of Curiosity: Token Cost vs. Ambiguity"
):
    """
    Generate the key chart from the PRD:
    X-Axis: Ambiguity Level (0% to 100%)
    Y-Axis: Token Cost
    
    Expected:
    - Mute Agent: Flat line (cost is constant regardless of ambiguity)
    - Interactive Agent: Cost explodes as ambiguity increases (more reflection loops)
    
    Args:
        results: List of benchmark results
        output_path: Where to save the chart
        title: Chart title
    """
    if not MATPLOTLIB_AVAILABLE:
        print("Cannot generate chart: matplotlib not installed")
        return
    
    # Extract data points
    data_points: List[AmbiguityDataPoint] = []
    
    for result in results:
        # Calculate ambiguity level based on scenario characteristics
        ambiguity = _calculate_ambiguity_level(result)
        
        data_points.append(AmbiguityDataPoint(
            ambiguity_level=ambiguity,
            mute_tokens=result.get("mute_tokens", 0),
            interactive_tokens=result.get("interactive_tokens", 0),
            scenario_title=result.get("scenario_title", "Unknown")
        ))
    
    # Sort by ambiguity level
    data_points.sort(key=lambda x: x.ambiguity_level)
    
    # Extract data for plotting
    ambiguity_levels = [dp.ambiguity_level * 100 for dp in data_points]  # Convert to percentage
    mute_tokens = [dp.mute_tokens for dp in data_points]
    interactive_tokens = [dp.interactive_tokens for dp in data_points]
    
    # Create figure
    plt.figure(figsize=(12, 7))
    
    # Plot lines
    plt.plot(ambiguity_levels, mute_tokens, 
             marker='o', linewidth=2, markersize=8,
             color='#2ecc71', label='Mute Agent (Graph-Constrained)',
             alpha=0.8)
    
    plt.plot(ambiguity_levels, interactive_tokens,
             marker='s', linewidth=2, markersize=8,
             color='#e74c3c', label='Interactive Agent (SOTA)',
             alpha=0.8)
    
    # Add mean lines
    mute_mean = sum(mute_tokens) / len(mute_tokens) if mute_tokens else 0
    interactive_mean = sum(interactive_tokens) / len(interactive_tokens) if interactive_tokens else 0
    
    plt.axhline(y=mute_mean, color='#2ecc71', linestyle='--', 
                alpha=0.5, linewidth=1, label=f'Mute Avg: {mute_mean:.0f} tokens')
    plt.axhline(y=interactive_mean, color='#e74c3c', linestyle='--',
                alpha=0.5, linewidth=1, label=f'Interactive Avg: {interactive_mean:.0f} tokens')
    
    # Styling
    plt.xlabel('Ambiguity Level (%)', fontsize=12, fontweight='bold')
    plt.ylabel('Token Cost', fontsize=12, fontweight='bold')
    plt.title(title, fontsize=14, fontweight='bold', pad=20)
    plt.legend(loc='upper left', fontsize=10)
    plt.grid(True, alpha=0.3, linestyle='--')
    
    # Add annotation
    if data_points:
        max_ambiguity_point = max(data_points, key=lambda x: x.ambiguity_level)
        reduction = ((max_ambiguity_point.interactive_tokens - max_ambiguity_point.mute_tokens) / 
                    max_ambiguity_point.interactive_tokens * 100)
        
        plt.text(0.5, 0.95, 
                f'At High Ambiguity: {reduction:.1f}% Token Reduction\n'
                f'Mute Agent: Constant Cost (Graph Constraints)\n'
                f'Interactive Agent: Increasing Cost (Reflection Loops)',
                transform=plt.gca().transAxes,
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
                verticalalignment='top',
                horizontalalignment='center',
                fontsize=9)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Chart saved to: {output_path}")
    plt.close()


def generate_metrics_comparison_chart(
    report: Dict[str, Any],
    output_path: str = "metrics_comparison.png"
):
    """
    Generate a bar chart comparing key metrics.
    
    Args:
        report: Benchmark report dictionary
        output_path: Where to save the chart
    """
    if not MATPLOTLIB_AVAILABLE:
        print("Cannot generate chart: matplotlib not installed")
        return
    
    # Extract metrics
    metrics = {
        'Avg Tokens': {
            'Mute': report.get('mute_avg_tokens', 0),
            'Interactive': report.get('interactive_avg_tokens', 0),
            'unit': 'tokens'
        },
        'Avg Latency': {
            'Mute': report.get('mute_avg_latency_ms', 0),
            'Interactive': report.get('interactive_avg_latency_ms', 0),
            'unit': 'ms'
        },
        'Avg Turns': {
            'Mute': report.get('mute_avg_turns', 0),
            'Interactive': report.get('interactive_avg_turns', 0),
            'unit': 'turns'
        },
        'User Interactions': {
            'Mute': report.get('mute_total_user_interactions', 0),
            'Interactive': report.get('interactive_total_user_interactions', 0),
            'unit': 'count'
        }
    }
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Mute Agent vs Interactive Agent: Key Metrics Comparison', 
                 fontsize=16, fontweight='bold')
    
    colors = ['#2ecc71', '#e74c3c']  # Green for Mute, Red for Interactive
    
    for idx, (metric_name, metric_data) in enumerate(metrics.items()):
        ax = axes[idx // 2, idx % 2]
        
        values = [metric_data['Mute'], metric_data['Interactive']]
        bars = ax.bar(['Mute Agent', 'Interactive Agent'], values, color=colors, alpha=0.8)
        
        ax.set_title(metric_name, fontsize=12, fontweight='bold')
        ax.set_ylabel(metric_data['unit'], fontsize=10)
        ax.grid(True, alpha=0.3, axis='y', linestyle='--')
        
        # Add value labels on bars
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{value:.1f}',
                   ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        # Add improvement percentage
        if metric_data['Interactive'] > 0 and metric_data['Mute'] < metric_data['Interactive']:
            improvement = ((metric_data['Interactive'] - metric_data['Mute']) / 
                         metric_data['Interactive'] * 100)
            ax.text(0.5, 0.95, f'↓ {improvement:.1f}% improvement',
                   transform=ax.transAxes,
                   ha='center', va='top',
                   bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7),
                   fontsize=9)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Metrics comparison chart saved to: {output_path}")
    plt.close()


def generate_scenario_class_breakdown(
    results: List[Dict[str, Any]],
    output_path: str = "scenario_breakdown.png"
):
    """
    Generate a breakdown by scenario class (stale_state, ghost_resource, privilege_escalation).
    
    Args:
        results: List of benchmark results
        output_path: Where to save the chart
    """
    if not MATPLOTLIB_AVAILABLE:
        print("Cannot generate chart: matplotlib not installed")
        return
    
    # Group by scenario class
    classes = {}
    for result in results:
        scenario_class = result.get('scenario_id', '').split('_')[0] + '_' + result.get('scenario_id', '').split('_')[1]
        if scenario_class not in classes:
            classes[scenario_class] = {
                'mute_tokens': [],
                'interactive_tokens': [],
                'count': 0
            }
        
        classes[scenario_class]['mute_tokens'].append(result.get('mute_tokens', 0))
        classes[scenario_class]['interactive_tokens'].append(result.get('interactive_tokens', 0))
        classes[scenario_class]['count'] += 1
    
    # Calculate averages
    class_names = []
    mute_avgs = []
    interactive_avgs = []
    
    for class_name, data in classes.items():
        class_names.append(class_name.replace('_', ' ').title())
        mute_avgs.append(sum(data['mute_tokens']) / len(data['mute_tokens']) if data['mute_tokens'] else 0)
        interactive_avgs.append(sum(data['interactive_tokens']) / len(data['interactive_tokens']) if data['interactive_tokens'] else 0)
    
    # Create grouped bar chart
    x = range(len(class_names))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    bars1 = ax.bar([i - width/2 for i in x], mute_avgs, width, 
                   label='Mute Agent', color='#2ecc71', alpha=0.8)
    bars2 = ax.bar([i + width/2 for i in x], interactive_avgs, width,
                   label='Interactive Agent', color='#e74c3c', alpha=0.8)
    
    ax.set_xlabel('Scenario Class', fontsize=12, fontweight='bold')
    ax.set_ylabel('Average Token Cost', fontsize=12, fontweight='bold')
    ax.set_title('Token Cost by Scenario Class', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(class_names, rotation=15, ha='right')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3, axis='y', linestyle='--')
    
    # Add value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.0f}',
                   ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Scenario breakdown chart saved to: {output_path}")
    plt.close()


def _calculate_ambiguity_level(result: Dict[str, Any]) -> float:
    """
    Calculate ambiguity level for a scenario (0.0 to 1.0).
    
    Factors that increase ambiguity:
    - Multiple services with same name
    - Pronoun usage ("it", "the service")
    - Stale context
    - Partial state
    
    Args:
        result: Benchmark result dictionary
    
    Returns:
        Ambiguity level from 0.0 (clear) to 1.0 (highly ambiguous)
    """
    scenario_id = result.get('scenario_id', '')
    
    # Base ambiguity by scenario class
    if 'stale_state' in scenario_id:
        base_ambiguity = 0.7  # High ambiguity - context is unclear
    elif 'ghost_resource' in scenario_id:
        base_ambiguity = 0.5  # Medium ambiguity - state is unclear
    elif 'privilege' in scenario_id:
        base_ambiguity = 0.3  # Low ambiguity - permissions are policy-based
    else:
        base_ambiguity = 0.5
    
    # Adjust based on whether Interactive Agent needed clarification
    if result.get('interactive_needed_clarification', False):
        base_ambiguity = min(1.0, base_ambiguity + 0.2)
    
    # Adjust based on number of turns taken
    turns = result.get('interactive_turns', 1)
    if turns > 1:
        base_ambiguity = min(1.0, base_ambiguity + (turns - 1) * 0.1)
    
    return base_ambiguity


def generate_all_visualizations(
    benchmark_results_path: str,
    output_dir: str = "."
):
    """
    Generate all visualizations from a benchmark results file.
    
    Args:
        benchmark_results_path: Path to benchmark results JSON
        output_dir: Directory to save charts
    """
    if not MATPLOTLIB_AVAILABLE:
        print("Cannot generate visualizations: matplotlib not installed")
        print("Install with: pip install matplotlib")
        return
    
    # Load results
    with open(benchmark_results_path, 'r') as f:
        report = json.load(f)
    
    results = report.get('results', [])
    
    if not results:
        print("No results found in benchmark report")
        return
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate all charts
    print("Generating visualizations...")
    
    generate_cost_vs_ambiguity_chart(
        results,
        output_path=os.path.join(output_dir, "cost_vs_ambiguity.png")
    )
    
    generate_metrics_comparison_chart(
        report,
        output_path=os.path.join(output_dir, "metrics_comparison.png")
    )
    
    generate_scenario_class_breakdown(
        results,
        output_path=os.path.join(output_dir, "scenario_breakdown.png")
    )
    
    print(f"\nAll visualizations saved to: {output_dir}")


def main():
    """CLI for generating visualizations."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate visualizations from benchmark results"
    )
    parser.add_argument(
        "results_file",
        help="Path to benchmark results JSON file"
    )
    parser.add_argument(
        "--output-dir",
        default=".",
        help="Directory to save charts (default: current directory)"
    )
    
    args = parser.parse_args()
    
    generate_all_visualizations(args.results_file, args.output_dir)


if __name__ == "__main__":
    main()
