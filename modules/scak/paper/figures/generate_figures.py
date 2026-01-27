"""
Generate all 6 figures for the SCAK paper.

Figures:
1. fig1_ooda_architecture - Dual-Loop OODA Architecture
2. fig2_memory_hierarchy - Three-Tier Memory Hierarchy
3. fig3_gaia_results - GAIA Benchmark Bar Chart
4. fig4_ablation_heatmap - Ablation Study Heatmap
5. fig5_context_reduction - Context Token Reduction Line Chart
6. fig6_mttr_boxplot - Chaos Engineering MTTR Box Plot
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import os

# Output directory (relative to script location)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = SCRIPT_DIR

# Set global style for academic figures
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.labelsize'] = 10


def draw_box(ax, xy, width, height, label, color='#e0e0e0', edge='black', fontsize=9):
    """Helper to draw a styled box with label."""
    box = patches.FancyBboxPatch(
        xy, width, height,
        boxstyle='round,pad=0.05',
        linewidth=1.5,
        edgecolor=edge,
        facecolor=color,
        zorder=2
    )
    ax.add_patch(box)
    ax.text(
        xy[0] + width/2, xy[1] + height/2, label,
        ha='center', va='center', fontweight='bold',
        fontsize=fontsize, zorder=3, color='black'
    )
    return box


def create_fig1_ooda_architecture():
    """Figure 1: Dual-Loop OODA Architecture."""
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # User Query at top
    draw_box(ax, (4.5, 9.0), 3, 0.7, "USER QUERY", color='#ffffff', edge='#333')
    
    # Loop 1: Runtime (Blue background)
    loop1_bg = patches.FancyBboxPatch(
        (0.5, 5.0), 11, 3.5,
        boxstyle='round,pad=0.1',
        linewidth=2,
        edgecolor='#1565C0',
        facecolor='#E3F2FD',
        zorder=0
    )
    ax.add_patch(loop1_bg)
    ax.text(1.0, 8.2, "LOOP 1: RUNTIME (OBSERVE → ACT)", fontsize=11, 
            fontweight='bold', color='#0D47A1')
    
    # Loop 1 components
    draw_box(ax, (1.0, 6.5), 2.2, 1.2, "TRIAGE\nENGINE\n(Sync/Async)", 
             color='#FF9800', edge='#E65100', fontsize=8)
    draw_box(ax, (4.0, 6.5), 2.2, 1.2, "EXECUTE\nAGENT\n(GPT-4o)", 
             color='#FFCC80', edge='#E65100', fontsize=8)
    draw_box(ax, (7.0, 6.5), 2.2, 1.2, "RESPOND\n\n(Return)", 
             color='#C8E6C9', edge='#2E7D32', fontsize=8)
    draw_box(ax, (4.0, 5.2), 2.2, 1.0, "GIVE-UP\nDETECTOR", 
             color='#FFCDD2', edge='#C62828', fontsize=8)
    
    # Loop 2: Alignment (Green background)
    loop2_bg = patches.FancyBboxPatch(
        (0.5, 0.5), 11, 4.0,
        boxstyle='round,pad=0.1',
        linewidth=2,
        edgecolor='#2E7D32',
        facecolor='#E8F5E9',
        zorder=0
    )
    ax.add_patch(loop2_bg)
    ax.text(1.0, 4.2, "LOOP 2: ALIGNMENT (ORIENT → DECIDE)", fontsize=11, 
            fontweight='bold', color='#1B5E20')
    
    # Loop 2 components
    draw_box(ax, (1.0, 2.5), 2.2, 1.2, "COMPLETENESS\nAUDITOR\n(Diff Audit)", 
             color='#E1BEE7', edge='#7B1FA2', fontsize=8)
    draw_box(ax, (4.0, 2.5), 2.2, 1.2, "SHADOW\nTEACHER\n(o1-preview)", 
             color='#9C27B0', edge='#4A148C', fontsize=8)
    draw_box(ax, (7.0, 2.5), 2.2, 1.2, "MEMORY\nCONTROLLER\n(Tiered)", 
             color='#009688', edge='#004D40', fontsize=8)
    draw_box(ax, (4.0, 0.8), 2.2, 1.2, "GAP ANALYSIS\n→ PATCH", 
             color='#B2DFDB', edge='#00695C', fontsize=8)
    draw_box(ax, (7.0, 0.8), 2.2, 1.0, "APPLY PATCH\nto Memory", 
             color='#80CBC4', edge='#00695C', fontsize=8)
    
    # Arrows
    arrow_props = dict(arrowstyle='->', lw=2, color='#424242')
    
    # User -> Triage
    ax.annotate("", xy=(2.1, 8.5), xytext=(5.0, 9.0), arrowprops=arrow_props)
    # Triage -> Execute
    ax.annotate("", xy=(4.0, 7.1), xytext=(3.2, 7.1), arrowprops=arrow_props)
    # Execute -> Respond
    ax.annotate("", xy=(7.0, 7.1), xytext=(6.2, 7.1), arrowprops=arrow_props)
    # Respond -> User
    ax.annotate("", xy=(10.5, 8.5), xytext=(8.5, 7.7), arrowprops=arrow_props)
    ax.text(10.2, 8.0, "User", fontsize=9)
    # Execute -> Give-up detector
    ax.annotate("", xy=(5.1, 6.5), xytext=(5.1, 6.2), arrowprops=arrow_props)
    # Give-up -> Auditor (async)
    ax.annotate("", xy=(3.2, 3.7), xytext=(5.1, 5.2), 
                arrowprops=dict(arrowstyle='->', lw=2, color='#F44336', linestyle='dashed'))
    ax.text(3.5, 4.6, "5-10%\n(async)", fontsize=8, color='#F44336', ha='center')
    
    # Loop 2 internal arrows
    ax.annotate("", xy=(4.0, 3.1), xytext=(3.2, 3.1), arrowprops=arrow_props)
    ax.annotate("", xy=(7.0, 3.1), xytext=(6.2, 3.1), arrowprops=arrow_props)
    ax.annotate("", xy=(5.1, 2.5), xytext=(5.1, 2.0), arrowprops=arrow_props)
    ax.annotate("", xy=(7.0, 1.3), xytext=(6.2, 1.4), arrowprops=arrow_props)
    
    plt.title("Figure 1: SCAK Dual-Loop Architecture", fontweight='bold', fontsize=14, pad=20)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'fig1_ooda_architecture.png'), dpi=300, bbox_inches='tight')
    plt.savefig(os.path.join(OUTPUT_DIR, 'fig1_ooda_architecture.pdf'), bbox_inches='tight')
    plt.close()
    print("Created fig1_ooda_architecture.png/pdf")


def create_fig2_memory_hierarchy():
    """Figure 2: Three-Tier Memory Hierarchy with Type A/B Lifecycle."""
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Tier 1: Kernel (top, red/orange)
    draw_box(ax, (4.5, 8.0), 3, 1.5, "TIER 1: KERNEL\n(System Prompt)\n\n500 tokens\nALWAYS active", 
             color='#FFCDD2', edge='#C62828', fontsize=9)
    
    # Tier 2: Cache (left)
    draw_box(ax, (1.0, 5.5), 3, 1.8, "TIER 2: CACHE\n(Redis)\n\n10K entries\nConditional\nTool-specific", 
             color='#FFF9C4', edge='#F9A825', fontsize=9)
    
    # Promotion/Demotion (center)
    draw_box(ax, (4.5, 5.5), 3, 1.8, "PROMOTION\n/DEMOTION\n\n>10 hits/week → ↑\n<1 hit/month → ↓", 
             color='#E0E0E0', edge='#616161', fontsize=9)
    
    # Tier 3: Archive (right)
    draw_box(ax, (8.0, 5.5), 3, 1.8, "TIER 3: ARCHIVE\n(Vector DB)\n\nUnlimited\nOn-demand RAG\nLong-tail", 
             color='#BBDEFB', edge='#1565C0', fontsize=9)
    
    # Arrows from Tier 1
    ax.annotate("", xy=(2.5, 7.3), xytext=(4.5, 8.5), arrowprops=dict(arrowstyle='->', lw=2, color='#666'))
    ax.annotate("", xy=(6.0, 7.3), xytext=(6.0, 8.0), arrowprops=dict(arrowstyle='->', lw=2, color='#666'))
    ax.annotate("", xy=(9.5, 7.3), xytext=(7.5, 8.5), arrowprops=dict(arrowstyle='->', lw=2, color='#666'))
    
    # Bidirectional arrows between tiers
    ax.annotate("", xy=(4.5, 6.4), xytext=(4.0, 6.4), arrowprops=dict(arrowstyle='<->', lw=2, color='#666'))
    ax.annotate("", xy=(8.0, 6.4), xytext=(7.5, 6.4), arrowprops=dict(arrowstyle='<->', lw=2, color='#666'))
    
    # Type A/B boxes at bottom
    # Type A (left)
    type_a_bg = patches.FancyBboxPatch(
        (0.5, 0.5), 5, 4.0,
        boxstyle='round,pad=0.1',
        linewidth=2,
        edgecolor='#9E9E9E',
        facecolor='#ECEFF1',
        zorder=0
    )
    ax.add_patch(type_a_bg)
    ax.text(3.0, 4.2, "TYPE A PATCHES (Syntax/Capability)", fontsize=10, 
            fontweight='bold', color='#616161', ha='center')
    ax.text(3.0, 3.5, "• \"Output valid JSON\"\n• \"Use ISO 8601 dates\"\n• \"Limit to 10 results\"", 
            fontsize=9, ha='center', va='top')
    ax.text(3.0, 1.8, "HIGH DECAY\nDelete on model upgrade\n~50 patches purged", 
            fontsize=9, ha='center', va='top', color='#D32F2F', fontweight='bold')
    
    # Type B (right)
    type_b_bg = patches.FancyBboxPatch(
        (6.5, 0.5), 5, 4.0,
        boxstyle='round,pad=0.1',
        linewidth=2,
        edgecolor='#388E3C',
        facecolor='#C8E6C9',
        zorder=0
    )
    ax.add_patch(type_b_bg)
    ax.text(9.0, 4.2, "TYPE B PATCHES (Business/Context)", fontsize=10, 
            fontweight='bold', color='#1B5E20', ha='center')
    ax.text(9.0, 3.5, "• \"Fiscal year: July 1\"\n• \"Project_Alpha: archived\"\n• \"VIP users: priority\"", 
            fontsize=9, ha='center', va='top')
    ax.text(9.0, 1.8, "ZERO DECAY\nRetain indefinitely\n~10 patches kept", 
            fontsize=9, ha='center', va='top', color='#1B5E20', fontweight='bold')
    
    plt.title("Figure 2: Three-Tier Memory Hierarchy with Type A/B Lifecycle", 
              fontweight='bold', fontsize=14, pad=20)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'fig2_memory_hierarchy.png'), dpi=300, bbox_inches='tight')
    plt.savefig(os.path.join(OUTPUT_DIR, 'fig2_memory_hierarchy.pdf'), bbox_inches='tight')
    plt.close()
    print("Created fig2_memory_hierarchy.png/pdf")


def create_fig3_gaia_results():
    """Figure 3: GAIA Benchmark Results Bar Chart."""
    # Data from spec
    methods = ['GPT-4o\n(baseline)', 'AutoGen', 'LangGraph', 'o1-preview\nalone', 'Self-\nCritique', 'SCAK\n(ours)']
    correction_rates = [8, 15, 0, 40, 40, 72]
    post_patch_success = [8, 18, 5, 45, 48, 82]
    
    colors = ['#BDBDBD', '#FF9800', '#2196F3', '#9C27B0', '#009688', '#4CAF50']
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    x = np.arange(len(methods))
    width = 0.35
    
    # Bars
    bars1 = ax.bar(x - width/2, correction_rates, width, label='Correction Rate', 
                   color=colors, edgecolor='black', linewidth=1)
    bars2 = ax.bar(x + width/2, post_patch_success, width, label='Post-Patch Success',
                   color=[c + '80' for c in colors], edgecolor='black', linewidth=1, alpha=0.7)
    
    # Add SCAK highlight border
    bars1[-1].set_edgecolor('#FFD700')
    bars1[-1].set_linewidth(3)
    bars2[-1].set_edgecolor('#FFD700')
    bars2[-1].set_linewidth(3)
    
    # Error bar for SCAK only
    ax.errorbar(x[-1] - width/2, correction_rates[-1], yerr=4.2, fmt='none', 
                color='black', capsize=5, capthick=2)
    ax.errorbar(x[-1] + width/2, post_patch_success[-1], yerr=3.1, fmt='none', 
                color='black', capsize=5, capthick=2)
    
    # Labels and formatting
    ax.set_ylabel('Rate (%)', fontsize=12)
    ax.set_xlabel('Method', fontsize=12)
    ax.set_title('GAIA Laziness Benchmark: Correction Rate Comparison', fontweight='bold', fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels(methods)
    ax.set_ylim(0, 100)
    ax.legend(loc='upper left')
    ax.grid(axis='y', linestyle='--', alpha=0.3)
    
    # Add significance stars for SCAK
    ax.text(x[-1], 88, '***', ha='center', fontsize=14, fontweight='bold')
    ax.text(x[-1], 92, 'p<0.001', ha='center', fontsize=8)
    
    # Value labels on bars
    for i, bar1 in enumerate(bars1):
        ax.text(bar1.get_x() + bar1.get_width()/2, bar1.get_height() + 2, 
                f'{int(correction_rates[i])}%', ha='center', fontsize=8, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'fig3_gaia_results.png'), dpi=300, bbox_inches='tight')
    plt.savefig(os.path.join(OUTPUT_DIR, 'fig3_gaia_results.pdf'), bbox_inches='tight')
    plt.close()
    print("Created fig3_gaia_results.png/pdf")


def create_fig4_ablation_heatmap():
    """Figure 4: Ablation Study Heatmap."""
    import matplotlib.colors as mcolors
    
    # Data from spec
    configs = ['Full SCAK', '− Semantic Purge', '− Teacher (o1)', 
               '− Tiered Memory', '− Diff Audit', 'Self-Critique Only']
    detection = [100, 100, 45, 92, 0, 100]
    correction = [72, 68, 28, 55, 0, 40]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
    
    # Custom colormap: green (high) -> yellow (mid) -> red (low)
    cmap = mcolors.LinearSegmentedColormap.from_list('custom', 
           ['#E57373', '#FFB74D', '#FFF176', '#81C784', '#1B5E20'])
    
    # Detection Rate bars
    bars1 = ax1.barh(configs, detection, color=[cmap(d/100) for d in detection], edgecolor='black')
    ax1.set_xlabel('Detection Rate (%)', fontsize=12)
    ax1.set_title('Detection Rate', fontweight='bold', fontsize=12)
    ax1.set_xlim(0, 110)
    ax1.axvline(x=100, color='green', linestyle='--', alpha=0.5)
    
    # Add value labels
    for i, (bar, val) in enumerate(zip(bars1, detection)):
        ax1.text(val + 2, bar.get_y() + bar.get_height()/2, f'{val}%', 
                va='center', fontsize=10, fontweight='bold')
    
    # Correction Rate bars
    bars2 = ax2.barh(configs, correction, color=[cmap(c/100) for c in correction], edgecolor='black')
    ax2.set_xlabel('Correction Rate (%)', fontsize=12)
    ax2.set_title('Correction Rate', fontweight='bold', fontsize=12)
    ax2.set_xlim(0, 85)
    ax2.axvline(x=72, color='green', linestyle='--', alpha=0.5)
    
    # Add value labels and significance
    significance = ['', '*', '***', '**', '***', '***']
    for i, (bar, val, sig) in enumerate(zip(bars2, correction, significance)):
        label = f'{val}%'
        if sig:
            label += f' {sig}'
        ax2.text(val + 2, bar.get_y() + bar.get_height()/2, label, 
                va='center', fontsize=10, fontweight='bold')
    
    # Highlight Full SCAK row
    for bar in [bars1[0], bars2[0]]:
        bar.set_edgecolor('#FFD700')
        bar.set_linewidth(3)
    
    plt.suptitle('Figure 4: Ablation Study - Component Contributions', 
                 fontweight='bold', fontsize=14, y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'fig4_ablation_heatmap.png'), dpi=300, bbox_inches='tight')
    plt.savefig(os.path.join(OUTPUT_DIR, 'fig4_ablation_heatmap.pdf'), bbox_inches='tight')
    plt.close()
    print("Created fig4_ablation_heatmap.png/pdf")


def create_fig5_context_reduction():
    """Figure 5: Context Token Reduction Line Chart."""
    # Data from spec
    time_points = ['T0', '+10', '+20', '+30', '+40', '+50', 'UPG', '+60', '+70']
    no_purge = [800, 960, 1120, 1280, 1440, 1600, 1600, 1760, 1920]
    with_scak = [800, 960, 1120, 1280, 1440, 1600, 880, 1040, 1200]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    x = np.arange(len(time_points))
    
    # Lines
    ax.plot(x, no_purge, 'o-', color='#F44336', linewidth=2, markersize=8, 
            label='No Purge (unbounded)')
    ax.plot(x, with_scak, 's-', color='#4CAF50', linewidth=2, markersize=8, 
            label='SCAK (with Semantic Purge)')
    
    # Vertical line at model upgrade
    upgrade_idx = 6
    ax.axvline(x=upgrade_idx, color='#2196F3', linestyle='--', linewidth=2, alpha=0.7)
    ax.text(upgrade_idx + 0.1, 1800, 'Model Upgrade\n(GPT-4o → GPT-5)', 
            fontsize=10, color='#2196F3', fontweight='bold')
    
    # Shade the reduction area
    ax.fill_between(x[upgrade_idx:], with_scak[upgrade_idx:], no_purge[upgrade_idx:], 
                   alpha=0.2, color='#BBDEFB')
    
    # Annotation for 45% reduction
    ax.annotate('45% reduction', xy=(7, 1050), xytext=(8, 1400),
               arrowprops=dict(arrowstyle='->', color='#1565C0', lw=2),
               fontsize=11, fontweight='bold', color='#1565C0')
    
    ax.set_xlabel('Patches Added', fontsize=12)
    ax.set_ylabel('Context Tokens', fontsize=12)
    ax.set_title('Context Token Growth: With and Without Semantic Purge', 
                fontweight='bold', fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels(time_points)
    ax.set_ylim(600, 2100)
    ax.legend(loc='upper left')
    ax.grid(True, linestyle='--', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'fig5_context_reduction.png'), dpi=300, bbox_inches='tight')
    plt.savefig(os.path.join(OUTPUT_DIR, 'fig5_context_reduction.pdf'), bbox_inches='tight')
    plt.close()
    print("Created fig5_context_reduction.png/pdf")


def create_fig6_mttr_boxplot():
    """Figure 6: MTTR Comparison Box Plot."""
    # Raw data from spec
    simple_retry = [95, 180, 110, 75, 145, 160, 90, 130, 85, 120, 
                   155, 100, 140, 70, 125, 115, 165, 80, 135, 105]
    exp_backoff = [60, 95, 70, 110, 85, 75, 90, 100, 65, 80,
                  105, 55, 95, 120, 70, 85, 90, 75, 100, 80]
    scak = [25, 32, 28, 22, 35, 30, 26, 28, 24, 31,
            29, 27, 33, 25, 28, 30, 22, 35, 27, 28]
    
    data = [simple_retry, exp_backoff, scak]
    labels = ['Simple Retry\n(3x)', 'Exponential\nBackoff', 'SCAK\n(ours)']
    colors = ['#F44336', '#FF9800', '#4CAF50']
    
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Box plots
    bp = ax.boxplot(data, labels=labels, patch_artist=True, widths=0.6)
    
    # Color the boxes
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    
    # Style whiskers and caps
    for whisker in bp['whiskers']:
        whisker.set(color='#666', linewidth=1.5)
    for cap in bp['caps']:
        cap.set(color='#666', linewidth=1.5)
    for median in bp['medians']:
        median.set(color='black', linewidth=2)
    
    # Add horizontal threshold line
    ax.axhline(y=30, color='green', linestyle='--', linewidth=2, alpha=0.7)
    ax.text(0.6, 32, 'Acceptable threshold (30s)', fontsize=10, color='green')
    
    # Add significance annotation
    ax.text(3, 45, '***', ha='center', fontsize=16, fontweight='bold')
    ax.text(3, 50, 'p<0.001', ha='center', fontsize=9)
    
    # Add mean values
    means = [np.mean(d) for d in data]
    for i, (m, label) in enumerate(zip(means, ['120s', '85s', '28s'])):
        ax.text(i+1, m + 10, f'μ={label}', ha='center', fontsize=10, fontweight='bold')
    
    ax.set_ylabel('MTTR (seconds)', fontsize=12)
    ax.set_title('Chaos Engineering: Mean Time To Recovery (MTTR)', 
                fontweight='bold', fontsize=14)
    ax.set_ylim(0, 220)
    ax.grid(axis='y', linestyle='--', alpha=0.3)
    
    # Add text annotation
    ax.text(2.5, 200, '4.3× faster than retry\n85% recovery rate', 
           fontsize=10, ha='center', style='italic',
           bbox=dict(boxstyle='round', facecolor='#E8F5E9', edgecolor='#4CAF50'))
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'fig6_mttr_boxplot.png'), dpi=300, bbox_inches='tight')
    plt.savefig(os.path.join(OUTPUT_DIR, 'fig6_mttr_boxplot.pdf'), bbox_inches='tight')
    plt.close()
    print("Created fig6_mttr_boxplot.png/pdf")


if __name__ == "__main__":
    print("Generating all 6 figures for SCAK paper...")
    print(f"Output directory: {OUTPUT_DIR}")
    print()
    
    create_fig1_ooda_architecture()
    create_fig2_memory_hierarchy()
    create_fig3_gaia_results()
    create_fig4_ablation_heatmap()
    create_fig5_context_reduction()
    create_fig6_mttr_boxplot()
    
    print()
    print("Done! Generated figures:")
    print("  - fig1_ooda_architecture.png/pdf")
    print("  - fig2_memory_hierarchy.png/pdf")
    print("  - fig3_gaia_results.png/pdf")
    print("  - fig4_ablation_heatmap.png/pdf")
    print("  - fig5_context_reduction.png/pdf")
    print("  - fig6_mttr_boxplot.png/pdf")
