import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patches as patches
import numpy as np
import os

# Get script directory for output
script_dir = os.path.dirname(os.path.abspath(__file__))

# Set style for academic paper
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams.update({
    'font.family': 'serif',
    'axes.labelsize': 12,
    'axes.titlesize': 14,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    'figure.titlesize': 16
})

def save_fig(name):
    plt.tight_layout()
    pdf_path = os.path.join(script_dir, f"{name}.pdf")
    png_path = os.path.join(script_dir, f"{name}.png")
    plt.savefig(pdf_path, format='pdf', bbox_inches='tight')
    plt.savefig(png_path, format='png', dpi=300, bbox_inches='tight')
    print(f"Generated {name}.pdf and {name}.png")
    plt.close()

# ==========================================
# Figure 1: Architecture Diagram
# ==========================================
def draw_architecture():
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Colors
    header_color = '#2C3E50'
    component_color = '#3498DB'
    enforcement_color = '#E74C3C'
    output_color = '#27AE60'
    
    # Main container
    main_box = patches.FancyBboxPatch((0.5, 0.5), 11, 9, 
                                       boxstyle="round,pad=0.05",
                                       facecolor='#ECF0F1', edgecolor=header_color, linewidth=2)
    ax.add_patch(main_box)
    
    # Header
    ax.text(6, 9.2, 'Agent Control Plane', fontsize=16, fontweight='bold', 
            ha='center', va='center', color=header_color)
    
    # Top row components
    components_top = [
        (2, 7.5, 'Policy\nEngine', component_color),
        (6, 7.5, 'Constraint\nGraphs', component_color),
        (10, 7.5, 'Shadow\nMode', component_color),
    ]
    
    for x, y, label, color in components_top:
        box = patches.FancyBboxPatch((x-1.2, y-0.7), 2.4, 1.4,
                                      boxstyle="round,pad=0.05",
                                      facecolor=color, edgecolor='white', linewidth=2)
        ax.add_patch(box)
        ax.text(x, y, label, fontsize=10, fontweight='bold', 
                ha='center', va='center', color='white')
    
    # Arrows down to kernel
    for x in [2, 6, 10]:
        ax.annotate('', xy=(x, 5.3), xytext=(x, 6.8),
                    arrowprops=dict(arrowstyle='->', color='#7F8C8D', lw=2))
    
    # Agent Kernel (enforcement layer)
    kernel_box = patches.FancyBboxPatch((1.5, 4.3), 9, 1.4,
                                         boxstyle="round,pad=0.05",
                                         facecolor=enforcement_color, edgecolor='white', linewidth=2)
    ax.add_patch(kernel_box)
    ax.text(6, 5, 'Agent Kernel (Enforcement Layer)', fontsize=12, fontweight='bold',
            ha='center', va='center', color='white')
    
    # Arrow down from kernel
    ax.annotate('', xy=(6, 3), xytext=(6, 4.3),
                arrowprops=dict(arrowstyle='->', color='#7F8C8D', lw=2))
    
    # Bottom row components
    components_bottom = [
        (2, 2, 'Mute\nAgent', output_color),
        (6, 2, 'Execution\nEngine', output_color),
        (10, 2, 'Flight\nRecorder', output_color),
    ]
    
    for x, y, label, color in components_bottom:
        box = patches.FancyBboxPatch((x-1.2, y-0.7), 2.4, 1.4,
                                      boxstyle="round,pad=0.05",
                                      facecolor=color, edgecolor='white', linewidth=2)
        ax.add_patch(box)
        ax.text(x, y, label, fontsize=10, fontweight='bold',
                ha='center', va='center', color='white')
    
    # Arrows from kernel to bottom components
    ax.annotate('', xy=(2, 2.7), xytext=(4.5, 4.3),
                arrowprops=dict(arrowstyle='->', color='#7F8C8D', lw=2))
    ax.annotate('', xy=(6, 2.7), xytext=(6, 4.3),
                arrowprops=dict(arrowstyle='->', color='#7F8C8D', lw=2))
    ax.annotate('', xy=(10, 2.7), xytext=(7.5, 4.3),
                arrowprops=dict(arrowstyle='->', color='#7F8C8D', lw=2))
    
    # Labels
    ax.text(2, 0.9, 'Blocked → NULL', fontsize=9, ha='center', style='italic', color='#7F8C8D')
    ax.text(6, 0.9, 'Permitted → Execute', fontsize=9, ha='center', style='italic', color='#7F8C8D')
    ax.text(10, 0.9, 'All → Audit Log', fontsize=9, ha='center', style='italic', color='#7F8C8D')
    
    save_fig("architecture")

# ==========================================
# Figure 2: Main Benchmark Results
# ==========================================
def draw_results_chart():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))
    
    configs = ['Baseline\n(No ACP)', 'With ACP']
    
    # Safety Violation Rate
    svr = [26.67, 0.0]
    svr_err = [2.1, 0.0]
    colors1 = ['#E74C3C', '#27AE60']
    
    bars1 = ax1.bar(configs, svr, yerr=svr_err, capsize=5, color=colors1, edgecolor='white', linewidth=2)
    ax1.set_ylabel('Safety Violation Rate (%)', fontweight='bold')
    ax1.set_title('Safety Performance', fontweight='bold')
    ax1.set_ylim(0, 35)
    
    # Add value labels
    for bar, val in zip(bars1, svr):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2, 
                 f'{val:.2f}%', ha='center', va='bottom', fontweight='bold')
    
    # Add improvement annotation
    ax1.annotate('', xy=(1, 3), xytext=(0, 24),
                 arrowprops=dict(arrowstyle='->', color='green', lw=2))
    ax1.text(0.5, 14, '-26.67 pp', ha='center', fontsize=11, fontweight='bold', color='green')
    
    # Tokens per Blocked Request
    tokens = [127.4, 0.5]
    tokens_err = [18.6, 0.1]
    colors2 = ['#E74C3C', '#27AE60']
    
    bars2 = ax2.bar(configs, tokens, yerr=tokens_err, capsize=5, color=colors2, edgecolor='white', linewidth=2)
    ax2.set_ylabel('Tokens per Blocked Request', fontweight='bold')
    ax2.set_title('Token Efficiency', fontweight='bold')
    ax2.set_ylim(0, 160)
    
    # Add value labels
    for bar, val in zip(bars2, tokens):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                 f'{val:.1f}', ha='center', va='bottom', fontweight='bold')
    
    # Add improvement annotation
    ax2.annotate('98.1%\nreduction', xy=(1, 10), xytext=(0.5, 80),
                 arrowprops=dict(arrowstyle='->', color='green', lw=2),
                 fontsize=11, fontweight='bold', color='green', ha='center')
    
    save_fig("results_chart")

# ==========================================
# Figure 3: Ablation Study
# ==========================================
def draw_ablation_chart():
    fig, ax = plt.subplots(figsize=(10, 6))
    
    configs = ['Full\nKernel', 'No\nPolicyEngine', 'No\nConstraintGraphs', 'No\nMuteAgent', 'No\nSupervisorAgents']
    svr = [0.0, 40.0, 3.33, 0.0, 0.0]
    svr_err = [0.0, 5.2, 1.8, 0.0, 0.0]
    
    colors = ['#27AE60', '#E74C3C', '#F39C12', '#27AE60', '#27AE60']
    
    bars = ax.bar(configs, svr, yerr=svr_err, capsize=5, color=colors, edgecolor='white', linewidth=2)
    
    ax.set_ylabel('Safety Violation Rate (%)', fontweight='bold')
    ax.set_title('Ablation Study: Component Criticality', fontweight='bold')
    ax.set_ylim(0, 50)
    
    # Add value labels
    for bar, val in zip(bars, svr):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1.5,
                f'{val:.2f}%', ha='center', va='bottom', fontweight='bold')
    
    # Highlight critical component
    ax.annotate('CRITICAL\np < 0.0001\nd = 8.7', xy=(1, 42), xytext=(1, 47),
                ha='center', fontsize=10, fontweight='bold', color='#E74C3C',
                bbox=dict(boxstyle='round', facecolor='#FADBD8', edgecolor='#E74C3C'))
    
    # Add significance markers
    ax.text(2, 6, '*', fontsize=16, ha='center', fontweight='bold')
    
    save_fig("ablation_chart")

# ==========================================
# Figure 4: Constraint Graphs Visualization
# ==========================================
def draw_constraint_graphs():
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis('off')
    
    # Three overlapping circles (Venn-like)
    circle_data = patches.Circle((3, 4.5), 2.2, facecolor='#AED6F1', edgecolor='#2980B9', 
                                   linewidth=2, alpha=0.7, label='Data Graph')
    circle_policy = patches.Circle((5, 4.5), 2.2, facecolor='#ABEBC6', edgecolor='#27AE60',
                                    linewidth=2, alpha=0.7, label='Policy Graph')
    circle_temporal = patches.Circle((4, 2.5), 2.2, facecolor='#F9E79F', edgecolor='#F39C12',
                                      linewidth=2, alpha=0.7, label='Temporal Graph')
    
    ax.add_patch(circle_data)
    ax.add_patch(circle_policy)
    ax.add_patch(circle_temporal)
    
    # Labels
    ax.text(2, 5.5, 'Data\nGraph', fontsize=11, fontweight='bold', ha='center', color='#2980B9')
    ax.text(6, 5.5, 'Policy\nGraph', fontsize=11, fontweight='bold', ha='center', color='#27AE60')
    ax.text(4, 1.2, 'Temporal Graph', fontsize=11, fontweight='bold', ha='center', color='#F39C12')
    
    # Center intersection
    ax.text(4, 4, 'OK', fontsize=18, ha='center', va='center', color='#27AE60', fontweight='bold')
    ax.text(4, 3.3, 'PERMIT', fontsize=10, ha='center', va='center', fontweight='bold', color='#27AE60')
    
    # Title
    ax.text(5, 7.5, 'Multi-Dimensional Constraint Validation', fontsize=14, 
            fontweight='bold', ha='center')
    ax.text(5, 7, 'Request must satisfy ALL graphs to proceed', fontsize=10,
            ha='center', style='italic', color='#7F8C8D')
    
    # Examples
    ax.text(1, 0.3, 'Data: "User A can access Table X"', fontsize=9, color='#2980B9')
    ax.text(4, 0.3, 'Policy: "No PII to external APIs"', fontsize=9, color='#27AE60')
    ax.text(7, 0.3, 'Temporal: "No writes 2-4 AM"', fontsize=9, color='#F39C12')
    
    save_fig("constraint_graphs")

# Run all
if __name__ == "__main__":
    print("Generating ACP paper figures...")
    draw_architecture()
    draw_results_chart()
    draw_ablation_chart()
    draw_constraint_graphs()
    print("\nAll figures generated successfully!")