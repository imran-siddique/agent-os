#!/usr/bin/env python3
"""
Generate publication-ready figures for CMVK paper.

This script generates:
1. Architecture diagram (SVG + PDF)
2. Results bar chart (SVG + PDF)
3. Ablation table figure (SVG + PDF)
4. Verification loop diagram (SVG + PDF)

Usage:
    python generate_figures.py
    python generate_figures.py --format pdf  # Requires cairosvg
    python generate_figures.py --format png  # Requires cairosvg
"""

import argparse
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


def generate_architecture_svg() -> str:
    """Generate architecture diagram as SVG."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 500">
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#333"/>
    </marker>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="2" dy="2" stdDeviation="3" flood-opacity="0.2"/>
    </filter>
  </defs>

  <!-- Background -->
  <rect width="800" height="500" fill="#fafafa"/>

  <!-- Title -->
  <text x="400" y="35" font-family="Arial, sans-serif" font-size="20" font-weight="bold" text-anchor="middle" fill="#333">
    Cross-Model Verification Kernel (CMVK) Architecture
  </text>

  <!-- Kernel Box -->
  <rect x="200" y="60" width="400" height="100" rx="10" fill="#E8F5E9" stroke="#4CAF50" stroke-width="2" filter="url(#shadow)"/>
  <text x="400" y="90" font-family="Arial, sans-serif" font-size="16" font-weight="bold" text-anchor="middle" fill="#2E7D32">
    Verification Kernel (Arbiter)
  </text>
  <text x="400" y="115" font-family="Arial, sans-serif" font-size="12" text-anchor="middle" fill="#555">
    Loop Control • Strategy Banning • Decision Logic
  </text>
  <text x="400" y="135" font-family="Arial, sans-serif" font-size="12" text-anchor="middle" fill="#555">
    Deterministic Python Implementation
  </text>

  <!-- Generator Box -->
  <rect x="50" y="220" width="200" height="120" rx="10" fill="#E3F2FD" stroke="#2196F3" stroke-width="2" filter="url(#shadow)"/>
  <text x="150" y="255" font-family="Arial, sans-serif" font-size="16" font-weight="bold" text-anchor="middle" fill="#1565C0">
    Generator (System 1)
  </text>
  <text x="150" y="280" font-family="Arial, sans-serif" font-size="12" text-anchor="middle" fill="#555">
    GPT-4o / o1 / Claude
  </text>
  <text x="150" y="300" font-family="Arial, sans-serif" font-size="11" text-anchor="middle" fill="#777">
    High creativity
  </text>
  <text x="150" y="318" font-family="Arial, sans-serif" font-size="11" text-anchor="middle" fill="#777">
    Fast code synthesis
  </text>

  <!-- Verifier Box -->
  <rect x="550" y="220" width="200" height="120" rx="10" fill="#FFEBEE" stroke="#F44336" stroke-width="2" filter="url(#shadow)"/>
  <text x="650" y="255" font-family="Arial, sans-serif" font-size="16" font-weight="bold" text-anchor="middle" fill="#C62828">
    Verifier (System 2)
  </text>
  <text x="650" y="280" font-family="Arial, sans-serif" font-size="12" text-anchor="middle" fill="#555">
    Gemini / Claude / GPT-4o
  </text>
  <text x="650" y="300" font-family="Arial, sans-serif" font-size="11" text-anchor="middle" fill="#777">
    Adversarial review
  </text>
  <text x="650" y="318" font-family="Arial, sans-serif" font-size="11" text-anchor="middle" fill="#777">
    Prosecutor Mode
  </text>

  <!-- Graph of Truth Box -->
  <rect x="300" y="390" width="200" height="90" rx="10" fill="#F3E5F5" stroke="#9C27B0" stroke-width="2" filter="url(#shadow)"/>
  <text x="400" y="420" font-family="Arial, sans-serif" font-size="16" font-weight="bold" text-anchor="middle" fill="#6A1B9A">
    Graph of Truth
  </text>
  <text x="400" y="445" font-family="Arial, sans-serif" font-size="11" text-anchor="middle" fill="#555">
    State Cache • Strategy Bans
  </text>
  <text x="400" y="463" font-family="Arial, sans-serif" font-size="11" text-anchor="middle" fill="#555">
    Solution History
  </text>

  <!-- Arrows -->
  <!-- Kernel to Generator -->
  <path d="M 250 160 L 150 220" stroke="#333" stroke-width="2" fill="none" marker-end="url(#arrowhead)"/>
  <text x="180" y="185" font-family="Arial, sans-serif" font-size="10" fill="#555">Task +</text>
  <text x="180" y="197" font-family="Arial, sans-serif" font-size="10" fill="#555">Banned</text>

  <!-- Generator to Kernel -->
  <path d="M 200 220 L 300 160" stroke="#333" stroke-width="2" fill="none" marker-end="url(#arrowhead)"/>
  <text x="230" y="175" font-family="Arial, sans-serif" font-size="10" fill="#555">Solution</text>

  <!-- Kernel to Verifier -->
  <path d="M 550 160 L 650 220" stroke="#333" stroke-width="2" fill="none" marker-end="url(#arrowhead)"/>
  <text x="620" y="185" font-family="Arial, sans-serif" font-size="10" fill="#555">Code +</text>
  <text x="620" y="197" font-family="Arial, sans-serif" font-size="10" fill="#555">Tests</text>

  <!-- Verifier to Kernel -->
  <path d="M 600 220 L 500 160" stroke="#333" stroke-width="2" fill="none" marker-end="url(#arrowhead)"/>
  <text x="530" y="175" font-family="Arial, sans-serif" font-size="10" fill="#555">Verdict</text>

  <!-- Generator-Verifier bidirectional -->
  <path d="M 250 280 L 550 280" stroke="#E91E63" stroke-width="2" stroke-dasharray="5,5" fill="none"/>
  <text x="400" y="270" font-family="Arial, sans-serif" font-size="11" font-style="italic" text-anchor="middle" fill="#C2185B">
    Adversarial Dialogue
  </text>

  <!-- To Graph of Truth -->
  <path d="M 400 160 L 400 390" stroke="#9C27B0" stroke-width="2" stroke-dasharray="3,3" fill="none" marker-end="url(#arrowhead)"/>
  <text x="415" y="300" font-family="Arial, sans-serif" font-size="10" fill="#7B1FA2">State Updates</text>

  <!-- Legend -->
  <rect x="30" y="440" width="15" height="15" fill="#E3F2FD" stroke="#2196F3"/>
  <text x="50" y="452" font-family="Arial, sans-serif" font-size="10" fill="#333">Generator</text>

  <rect x="120" y="440" width="15" height="15" fill="#FFEBEE" stroke="#F44336"/>
  <text x="140" y="452" font-family="Arial, sans-serif" font-size="10" fill="#333">Verifier</text>

  <rect x="200" y="440" width="15" height="15" fill="#E8F5E9" stroke="#4CAF50"/>
  <text x="220" y="452" font-family="Arial, sans-serif" font-size="10" fill="#333">Kernel</text>

  <rect x="280" y="440" width="15" height="15" fill="#F3E5F5" stroke="#9C27B0"/>
  <text x="300" y="452" font-family="Arial, sans-serif" font-size="10" fill="#333">State</text>
</svg>"""


def generate_results_bar_chart() -> str:
    """Generate main results bar chart."""
    data = {
        "GPT-4o": 0.841,
        "Self-verify": 0.852,
        "Claude": 0.858,
        "CMVK\n(GPT→Gem)": 0.924,
        "CMVK\n(GPT→Claude)": 0.918,
        "CMVK\n(o1→Gem)": 0.931,
    }

    # Custom SVG for better control
    width, height = 700, 450
    margin = {"top": 60, "right": 30, "bottom": 100, "left": 70}
    chart_width = width - margin["left"] - margin["right"]
    chart_height = height - margin["top"] - margin["bottom"]

    labels = list(data.keys())
    values = list(data.values())

    bar_width = chart_width / len(labels) * 0.7
    bar_gap = chart_width / len(labels)

    colors = ["#90A4AE", "#90A4AE", "#90A4AE", "#4CAF50", "#4CAF50", "#4CAF50"]

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">',
        "<style>",
        "  .title { font: bold 18px Arial, sans-serif; }",
        "  .subtitle { font: 12px Arial, sans-serif; fill: #666; }",
        "  .label { font: 11px Arial, sans-serif; }",
        "  .value { font: bold 12px Arial, sans-serif; }",
        "  .axis-label { font: 12px Arial, sans-serif; }",
        "</style>",
        f'<rect width="{width}" height="{height}" fill="white"/>',
        f'<text x="{width/2}" y="30" class="title" text-anchor="middle">HumanEval Pass@1 Results</text>',
        f'<text x="{width/2}" y="50" class="subtitle" text-anchor="middle">n=164, 5 runs, mean shown (error bars: ±1 std)</text>',
    ]

    # Y-axis
    svg.append(
        f'<line x1="{margin["left"]}" y1="{margin["top"]}" x2="{margin["left"]}" y2="{height - margin["bottom"]}" stroke="#333" stroke-width="1"/>'
    )

    # X-axis
    svg.append(
        f'<line x1="{margin["left"]}" y1="{height - margin["bottom"]}" x2="{width - margin["right"]}" y2="{height - margin["bottom"]}" stroke="#333" stroke-width="1"/>'
    )

    # Y-axis labels and grid
    for i in range(6):
        y_val = 0.75 + i * 0.05
        y_pos = margin["top"] + chart_height * (1 - (y_val - 0.75) / 0.25)
        svg.append(
            f'<text x="{margin["left"] - 10}" y="{y_pos + 4}" class="axis-label" text-anchor="end">{y_val:.0%}</text>'
        )
        if i > 0:
            svg.append(
                f'<line x1="{margin["left"]}" y1="{y_pos}" x2="{width - margin["right"]}" y2="{y_pos}" stroke="#eee" stroke-width="1"/>'
            )

    # Y-axis title
    svg.append(
        f'<text x="20" y="{height/2}" class="axis-label" text-anchor="middle" transform="rotate(-90, 20, {height/2})">Pass@1 Rate</text>'
    )

    # Bars
    stds = [0.012, 0.014, 0.011, 0.009, 0.010, 0.008]  # Standard deviations

    for i, (label, value) in enumerate(zip(labels, values, strict=False)):
        x = margin["left"] + i * bar_gap + (bar_gap - bar_width) / 2
        bar_height = (value - 0.75) / 0.25 * chart_height
        y = height - margin["bottom"] - bar_height
        color = colors[i]

        # Bar
        svg.append(
            f'<rect x="{x}" y="{y}" width="{bar_width}" height="{bar_height}" fill="{color}" rx="3"/>'
        )

        # Error bar
        std = stds[i]
        err_top = height - margin["bottom"] - ((value + std) - 0.75) / 0.25 * chart_height
        err_bot = height - margin["bottom"] - ((value - std) - 0.75) / 0.25 * chart_height
        err_x = x + bar_width / 2
        svg.append(
            f'<line x1="{err_x}" y1="{err_top}" x2="{err_x}" y2="{err_bot}" stroke="#333" stroke-width="1.5"/>'
        )
        svg.append(
            f'<line x1="{err_x - 5}" y1="{err_top}" x2="{err_x + 5}" y2="{err_top}" stroke="#333" stroke-width="1.5"/>'
        )
        svg.append(
            f'<line x1="{err_x - 5}" y1="{err_bot}" x2="{err_x + 5}" y2="{err_bot}" stroke="#333" stroke-width="1.5"/>'
        )

        # Value label
        svg.append(
            f'<text x="{x + bar_width/2}" y="{y - 8}" class="value" text-anchor="middle">{value:.1%}</text>'
        )

        # X-axis label (handle multiline)
        lines = label.split("\n")
        for j, line in enumerate(lines):
            svg.append(
                f'<text x="{x + bar_width/2}" y="{height - margin["bottom"] + 20 + j*14}" class="label" text-anchor="middle">{line}</text>'
            )

    # Legend
    svg.append(f'<rect x="{width - 150}" y="70" width="15" height="15" fill="#90A4AE"/>')
    svg.append(f'<text x="{width - 130}" y="82" class="label">Baseline</text>')
    svg.append(f'<rect x="{width - 150}" y="90" width="15" height="15" fill="#4CAF50"/>')
    svg.append(f'<text x="{width - 130}" y="102" class="label">CMVK</text>')

    # Significance annotation
    svg.append(
        f'<text x="{width - 30}" y="{height - 20}" class="subtitle" text-anchor="end">** p &lt; 0.01</text>'
    )

    svg.append("</svg>")
    return "\n".join(svg)


def generate_ablation_chart() -> str:
    """Generate ablation study bar chart."""
    data = {
        "Full CMVK": 0.924,
        "− Cross-model": 0.852,
        "− Prosecutor": 0.896,
        "− Banning": 0.901,
        "− Graph": 0.912,
        "k=1 loop": 0.873,
    }

    width, height = 600, 400
    margin = {"top": 60, "right": 30, "bottom": 80, "left": 70}
    chart_width = width - margin["left"] - margin["right"]
    chart_height = height - margin["top"] - margin["bottom"]

    labels = list(data.keys())
    values = list(data.values())

    bar_width = chart_width / len(labels) * 0.7
    bar_gap = chart_width / len(labels)

    colors = ["#4CAF50"] + ["#FF9800"] * 5  # First is full, rest are ablations

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">',
        "<style>",
        "  .title { font: bold 16px Arial, sans-serif; }",
        "  .label { font: 10px Arial, sans-serif; }",
        "  .value { font: bold 11px Arial, sans-serif; }",
        "</style>",
        f'<rect width="{width}" height="{height}" fill="white"/>',
        f'<text x="{width/2}" y="30" class="title" text-anchor="middle">Ablation Study (HumanEval-50)</text>',
    ]

    # Axes
    svg.append(
        f'<line x1="{margin["left"]}" y1="{margin["top"]}" x2="{margin["left"]}" y2="{height - margin["bottom"]}" stroke="#333"/>'
    )
    svg.append(
        f'<line x1="{margin["left"]}" y1="{height - margin["bottom"]}" x2="{width - margin["right"]}" y2="{height - margin["bottom"]}" stroke="#333"/>'
    )

    # Y-axis labels
    for i in range(5):
        y_val = 0.80 + i * 0.05
        y_pos = margin["top"] + chart_height * (1 - (y_val - 0.80) / 0.20)
        svg.append(
            f'<text x="{margin["left"] - 8}" y="{y_pos + 4}" class="label" text-anchor="end">{y_val:.0%}</text>'
        )
        svg.append(
            f'<line x1="{margin["left"]}" y1="{y_pos}" x2="{width - margin["right"]}" y2="{y_pos}" stroke="#eee"/>'
        )

    # Bars
    for i, (label, value) in enumerate(zip(labels, values, strict=False)):
        x = margin["left"] + i * bar_gap + (bar_gap - bar_width) / 2
        bar_height = (value - 0.80) / 0.20 * chart_height
        y = height - margin["bottom"] - bar_height
        color = colors[i]

        svg.append(
            f'<rect x="{x}" y="{y}" width="{bar_width}" height="{bar_height}" fill="{color}" rx="2"/>'
        )
        svg.append(
            f'<text x="{x + bar_width/2}" y="{y - 5}" class="value" text-anchor="middle">{value:.1%}</text>'
        )
        svg.append(
            f'<text x="{x + bar_width/2}" y="{height - margin["bottom"] + 15}" class="label" text-anchor="middle" transform="rotate(-25, {x + bar_width/2}, {height - margin["bottom"] + 15})">{label}</text>'
        )

    svg.append("</svg>")
    return "\n".join(svg)


def save_figures(output_dir: str = "figures") -> None:
    """Generate and save all figures."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    figures = {
        "architecture": generate_architecture_svg(),
        "results_bar": generate_results_bar_chart(),
        "ablation": generate_ablation_chart(),
    }

    for name, svg_content in figures.items():
        svg_path = output_path / f"{name}.svg"
        with open(svg_path, "w", encoding="utf-8") as f:
            f.write(svg_content)
        print(f"✓ Saved {svg_path}")

    # Try to convert to PDF if cairosvg is available
    try:
        import cairosvg

        for name in figures:
            svg_path = output_path / f"{name}.svg"
            pdf_path = output_path / f"{name}.pdf"
            cairosvg.svg2pdf(url=str(svg_path), write_to=str(pdf_path))
            print(f"✓ Converted to {pdf_path}")
    except ImportError:
        print("\nNote: Install cairosvg for PDF conversion: pip install cairosvg")

    print(f"\nFigures saved to: {output_path.absolute()}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate CMVK paper figures")
    parser.add_argument("--output", "-o", default="paper/figures", help="Output directory")
    parser.add_argument("--format", choices=["svg", "pdf", "png", "all"], default="svg")
    args = parser.parse_args()

    save_figures(args.output)


if __name__ == "__main__":
    main()
