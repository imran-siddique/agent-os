#!/usr/bin/env python3
"""
Results Visualization for CMVK Experiments

This script generates publication-ready figures and tables from experiment results.
Supports:
- Bar charts for pass@1 comparisons
- Ablation study visualizations
- Learning curves (loops vs. success)
- Statistical comparison tables
- LaTeX export

Usage:
    python experiments/visualize_results.py --input results.json --output figures/
    python experiments/visualize_results.py --demo  # Generate demo figures
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))


# ============================================================================
# ASCII Chart Rendering (No Dependencies)
# ============================================================================


class ASCIIChart:
    """Generate ASCII charts for terminal display."""

    @staticmethod
    def bar_chart(
        data: dict[str, float],
        title: str = "",
        width: int = 50,
        max_value: float | None = None,
    ) -> str:
        """Generate a horizontal bar chart."""
        lines = []

        if title:
            lines.append(f"╔{'═' * (width + 20)}╗")
            lines.append(f"║ {title.center(width + 18)} ║")
            lines.append(f"╠{'═' * (width + 20)}╣")

        max_val = max_value or max(data.values())
        max_label = max(len(str(k)) for k in data)

        for label, value in data.items():
            bar_width = int((value / max_val) * width) if max_val > 0 else 0
            bar = "█" * bar_width + "░" * (width - bar_width)
            pct = f"{value:.1%}" if value <= 1 else f"{value:.1f}"
            lines.append(f"║ {label.ljust(max_label)} │{bar}│ {pct.rjust(6)} ║")

        if title:
            lines.append(f"╚{'═' * (width + 20)}╝")

        return "\n".join(lines)

    @staticmethod
    def grouped_bar_chart(
        data: dict[str, dict[str, float]],
        title: str = "",
        width: int = 40,
    ) -> str:
        """Generate a grouped bar chart (multiple series)."""
        lines = []

        if title:
            lines.append(f"\n{'=' * 60}")
            lines.append(title.center(60))
            lines.append("=" * 60)

        # Get all series names
        series_names = set()
        for group_data in data.values():
            series_names.update(group_data.keys())
        series_names = sorted(series_names)

        # Characters for different series
        chars = ["█", "▓", "▒", "░"]

        max_val = max(v for group_data in data.values() for v in group_data.values())

        for group, group_data in data.items():
            lines.append(f"\n{group}:")
            for i, series in enumerate(series_names):
                value = group_data.get(series, 0)
                bar_width = int((value / max_val) * width) if max_val > 0 else 0
                char = chars[i % len(chars)]
                bar = char * bar_width
                pct = f"{value:.1%}" if value <= 1 else f"{value:.1f}"
                lines.append(f"  {series.ljust(15)} │{bar.ljust(width)}│ {pct}")

        # Legend
        lines.append("\nLegend:")
        for i, series in enumerate(series_names):
            char = chars[i % len(chars)]
            lines.append(f"  {char * 3} = {series}")

        return "\n".join(lines)

    @staticmethod
    def table(
        data: list[dict[str, Any]],
        columns: list[str],
        title: str = "",
    ) -> str:
        """Generate an ASCII table."""
        # Compute column widths
        widths = {col: len(col) for col in columns}
        for row in data:
            for col in columns:
                val = str(row.get(col, ""))
                widths[col] = max(widths[col], len(val))

        # Build table
        lines = []

        # Header
        sep = "+" + "+".join("-" * (widths[c] + 2) for c in columns) + "+"
        lines.append(sep)

        if title:
            total_width = sum(widths.values()) + len(columns) * 3 - 1
            lines.append(f"|{title.center(total_width)}|")
            lines.append(sep)

        header = "|" + "|".join(f" {c.center(widths[c])} " for c in columns) + "|"
        lines.append(header)
        lines.append(sep.replace("-", "="))

        # Data rows
        for row in data:
            row_str = (
                "|" + "|".join(f" {str(row.get(c, '')).ljust(widths[c])} " for c in columns) + "|"
            )
            lines.append(row_str)

        lines.append(sep)
        return "\n".join(lines)


# ============================================================================
# SVG Chart Generation (No Dependencies)
# ============================================================================


class SVGChart:
    """Generate SVG charts for publication."""

    @staticmethod
    def bar_chart(
        data: dict[str, float],
        title: str = "",
        width: int = 600,
        height: int = 400,
        colors: list[str] | None = None,
    ) -> str:
        """Generate an SVG bar chart."""
        default_colors = [
            "#4A90D9",  # Blue (Generator)
            "#E57373",  # Red (Verifier)
            "#81C784",  # Green (Success)
            "#9575CD",  # Purple (Graph)
            "#90A4AE",  # Gray
            "#FFB74D",  # Orange
        ]
        colors = colors or default_colors

        margin = {"top": 60, "right": 30, "bottom": 80, "left": 60}
        chart_width = width - margin["left"] - margin["right"]
        chart_height = height - margin["top"] - margin["bottom"]

        labels = list(data.keys())
        values = list(data.values())
        max_val = max(values) * 1.1  # 10% padding

        bar_width = chart_width / len(labels) * 0.7
        bar_gap = chart_width / len(labels) * 0.3

        svg_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">',
            "<style>",
            "  .title { font: bold 18px sans-serif; }",
            "  .label { font: 12px sans-serif; }",
            "  .value { font: bold 12px sans-serif; }",
            "  .axis { stroke: #333; stroke-width: 1; }",
            "</style>",
            f'<rect width="{width}" height="{height}" fill="white"/>',
        ]

        # Title
        if title:
            svg_parts.append(
                f'<text x="{width/2}" y="30" class="title" text-anchor="middle">{title}</text>'
            )

        # Y-axis
        svg_parts.append(
            f'<line x1="{margin["left"]}" y1="{margin["top"]}" '
            f'x2="{margin["left"]}" y2="{height - margin["bottom"]}" class="axis"/>'
        )

        # X-axis
        svg_parts.append(
            f'<line x1="{margin["left"]}" y1="{height - margin["bottom"]}" '
            f'x2="{width - margin["right"]}" y2="{height - margin["bottom"]}" class="axis"/>'
        )

        # Y-axis labels
        for i in range(5):
            y_val = max_val * (4 - i) / 4
            y_pos = margin["top"] + (chart_height * i / 4)
            svg_parts.append(
                f'<text x="{margin["left"] - 10}" y="{y_pos + 4}" '
                f'class="label" text-anchor="end">{y_val:.0%}</text>'
            )
            svg_parts.append(
                f'<line x1="{margin["left"]}" y1="{y_pos}" '
                f'x2="{width - margin["right"]}" y2="{y_pos}" '
                f'stroke="#eee" stroke-width="1"/>'
            )

        # Bars
        for i, (label, value) in enumerate(data.items()):
            x = margin["left"] + (bar_gap / 2) + i * (bar_width + bar_gap)
            bar_height = (value / max_val) * chart_height
            y = height - margin["bottom"] - bar_height
            color = colors[i % len(colors)]

            svg_parts.append(
                f'<rect x="{x}" y="{y}" width="{bar_width}" height="{bar_height}" '
                f'fill="{color}" rx="2"/>'
            )

            # Value label
            svg_parts.append(
                f'<text x="{x + bar_width/2}" y="{y - 5}" '
                f'class="value" text-anchor="middle">{value:.1%}</text>'
            )

            # X-axis label
            svg_parts.append(
                f'<text x="{x + bar_width/2}" y="{height - margin["bottom"] + 20}" '
                f'class="label" text-anchor="middle" transform="rotate(-30, {x + bar_width/2}, {height - margin["bottom"] + 20})">'
                f"{label}</text>"
            )

        svg_parts.append("</svg>")
        return "\n".join(svg_parts)

    @staticmethod
    def grouped_bar_chart(
        data: dict[str, dict[str, float]],
        title: str = "",
        width: int = 800,
        height: int = 500,
        series_colors: dict[str, str] | None = None,
    ) -> str:
        """Generate an SVG grouped bar chart."""
        default_colors = {
            "Baseline": "#90A4AE",
            "CMVK": "#4CAF50",
            "Self": "#FF9800",
            "Cross": "#2196F3",
        }
        series_colors = series_colors or default_colors

        margin = {"top": 80, "right": 150, "bottom": 100, "left": 70}
        chart_width = width - margin["left"] - margin["right"]
        chart_height = height - margin["top"] - margin["bottom"]

        groups = list(data.keys())
        all_series = set()
        for group_data in data.values():
            all_series.update(group_data.keys())
        series_list = sorted(all_series)

        max_val = max(v for gd in data.values() for v in gd.values()) * 1.1

        group_width = chart_width / len(groups)
        bar_width = group_width / (len(series_list) + 1) * 0.8

        svg_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">',
            "<style>",
            "  .title { font: bold 20px sans-serif; }",
            "  .label { font: 12px sans-serif; }",
            "  .value { font: 10px sans-serif; }",
            "  .legend { font: 12px sans-serif; }",
            "  .axis { stroke: #333; stroke-width: 1; }",
            "</style>",
            f'<rect width="{width}" height="{height}" fill="white"/>',
        ]

        # Title
        if title:
            svg_parts.append(
                f'<text x="{width/2}" y="35" class="title" text-anchor="middle">{title}</text>'
            )

        # Axes
        svg_parts.append(
            f'<line x1="{margin["left"]}" y1="{margin["top"]}" '
            f'x2="{margin["left"]}" y2="{height - margin["bottom"]}" class="axis"/>'
        )
        svg_parts.append(
            f'<line x1="{margin["left"]}" y1="{height - margin["bottom"]}" '
            f'x2="{width - margin["right"]}" y2="{height - margin["bottom"]}" class="axis"/>'
        )

        # Y-axis labels and grid
        for i in range(6):
            y_val = max_val * (5 - i) / 5
            y_pos = margin["top"] + (chart_height * i / 5)
            svg_parts.append(
                f'<text x="{margin["left"] - 10}" y="{y_pos + 4}" '
                f'class="label" text-anchor="end">{y_val:.0%}</text>'
            )
            if i > 0:
                svg_parts.append(
                    f'<line x1="{margin["left"]}" y1="{y_pos}" '
                    f'x2="{width - margin["right"]}" y2="{y_pos}" '
                    f'stroke="#eee" stroke-width="1"/>'
                )

        # Bars
        for gi, (group, group_data) in enumerate(data.items()):
            group_x = margin["left"] + gi * group_width

            for si, series in enumerate(series_list):
                value = group_data.get(series, 0)
                x = group_x + (si + 0.5) * bar_width + bar_width * 0.3
                bar_height = (value / max_val) * chart_height
                y = height - margin["bottom"] - bar_height

                color = series_colors.get(series, "#999")
                svg_parts.append(
                    f'<rect x="{x}" y="{y}" width="{bar_width * 0.9}" height="{bar_height}" '
                    f'fill="{color}" rx="2"/>'
                )

                # Value on top
                if value > 0:
                    svg_parts.append(
                        f'<text x="{x + bar_width * 0.45}" y="{y - 3}" '
                        f'class="value" text-anchor="middle">{value:.1%}</text>'
                    )

            # Group label
            svg_parts.append(
                f'<text x="{group_x + group_width/2}" y="{height - margin["bottom"] + 25}" '
                f'class="label" text-anchor="middle">{group}</text>'
            )

        # Legend
        legend_x = width - margin["right"] + 20
        legend_y = margin["top"] + 20
        for i, series in enumerate(series_list):
            color = series_colors.get(series, "#999")
            svg_parts.append(
                f'<rect x="{legend_x}" y="{legend_y + i * 25}" '
                f'width="18" height="18" fill="{color}" rx="2"/>'
            )
            svg_parts.append(
                f'<text x="{legend_x + 25}" y="{legend_y + i * 25 + 14}" '
                f'class="legend">{series}</text>'
            )

        svg_parts.append("</svg>")
        return "\n".join(svg_parts)


# ============================================================================
# LaTeX Table Generation
# ============================================================================


class LaTeXExporter:
    """Export results to LaTeX format."""

    @staticmethod
    def table(
        data: list[dict[str, Any]],
        columns: list[tuple[str, str]],  # [(key, header), ...]
        caption: str = "",
        label: str = "",
        highlight_best: str | None = None,
    ) -> str:
        """Generate a LaTeX table."""
        col_spec = "l" + "c" * (len(columns) - 1)
        headers = " & ".join(h for _, h in columns)

        lines = [
            "\\begin{table}[h]",
            "\\centering",
        ]

        if caption:
            lines.append(f"\\caption{{{caption}}}")
        if label:
            lines.append(f"\\label{{{label}}}")

        lines.extend(
            [
                f"\\begin{{tabular}}{{{col_spec}}}",
                "\\toprule",
                f"{headers} \\\\",
                "\\midrule",
            ]
        )

        # Find best value if highlighting
        best_val = None
        if highlight_best:
            values = [row.get(highlight_best, 0) for row in data]
            best_val = max(values)

        for row in data:
            cells = []
            for key, _ in columns:
                val = row.get(key, "")
                if isinstance(val, float):
                    cell = f"{val:.1%}" if val <= 1 else f"{val:.2f}"
                else:
                    cell = str(val)

                # Bold best value
                if highlight_best and key == highlight_best and row.get(key) == best_val:
                    cell = f"\\textbf{{{cell}}}"

                cells.append(cell)

            lines.append(" & ".join(cells) + " \\\\")

        lines.extend(
            [
                "\\bottomrule",
                "\\end{tabular}",
                "\\end{table}",
            ]
        )

        return "\n".join(lines)

    @staticmethod
    def significance_table(
        comparisons: list[dict[str, Any]],
    ) -> str:
        """Generate a table with statistical significance markers."""
        lines = [
            "\\begin{table}[h]",
            "\\centering",
            "\\caption{Statistical Significance of Improvements}",
            "\\label{tab:significance}",
            "\\begin{tabular}{lccccc}",
            "\\toprule",
            "Comparison & $\\Delta$ & t-stat & p-value & Significant \\\\",
            "\\midrule",
        ]

        for comp in comparisons:
            delta = comp.get("delta", 0)
            delta_str = f"+{delta:.1%}" if delta >= 0 else f"{delta:.1%}"
            t_stat = comp.get("t_statistic", 0)
            p_val = comp.get("p_value", 1)
            sig = "\\checkmark" if p_val < 0.05 else "-"
            if p_val < 0.01:
                sig = "\\checkmark\\checkmark"
            if p_val < 0.001:
                sig = "\\checkmark\\checkmark\\checkmark"

            lines.append(
                f"{comp.get('name', '')} & {delta_str} & {t_stat:.2f} & {p_val:.4f} & {sig} \\\\"
            )

        lines.extend(
            [
                "\\bottomrule",
                "\\multicolumn{5}{l}{\\footnotesize $^{***}$p<0.001, $^{**}$p<0.01, $^{*}$p<0.05} \\\\",
                "\\end{tabular}",
                "\\end{table}",
            ]
        )

        return "\n".join(lines)


# ============================================================================
# Results Processor
# ============================================================================


class ResultsVisualizer:
    """Process and visualize experiment results."""

    def __init__(self, output_dir: str = "figures"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def load_results(self, path: str) -> dict[str, Any]:
        """Load results from JSON file."""
        with open(path) as f:
            return json.load(f)

    def generate_main_comparison(
        self,
        results: dict[str, float],
        title: str = "HumanEval Pass@1 Results",
    ) -> dict[str, str]:
        """Generate main comparison figures in multiple formats."""
        outputs = {}

        # ASCII for terminal
        outputs["ascii"] = ASCIIChart.bar_chart(results, title)

        # SVG for web/papers
        outputs["svg"] = SVGChart.bar_chart(results, title)

        # Save files
        (self.output_dir / "main_comparison.txt").write_text(outputs["ascii"])
        (self.output_dir / "main_comparison.svg").write_text(outputs["svg"])

        return outputs

    def generate_ablation_figure(
        self,
        ablation_data: dict[str, dict[str, float]],
        title: str = "Ablation Study Results",
    ) -> dict[str, str]:
        """Generate ablation study figures."""
        outputs = {}

        # ASCII
        outputs["ascii"] = ASCIIChart.grouped_bar_chart(ablation_data, title)

        # SVG
        outputs["svg"] = SVGChart.grouped_bar_chart(
            ablation_data,
            title,
            series_colors={
                "Self-Verify": "#FF9800",
                "Cross-Verify": "#4CAF50",
                "No Prosecutor": "#FFC107",
                "Full CMVK": "#2196F3",
            },
        )

        # Save
        (self.output_dir / "ablation.txt").write_text(outputs["ascii"])
        (self.output_dir / "ablation.svg").write_text(outputs["svg"])

        return outputs

    def generate_latex_tables(
        self,
        results: list[dict[str, Any]],
    ) -> dict[str, str]:
        """Generate LaTeX tables for paper."""
        outputs = {}

        # Main results table
        outputs["main_table"] = LaTeXExporter.table(
            results,
            columns=[
                ("method", "Method"),
                ("pass_rate", "Pass@1"),
                ("delta", "$\\Delta$"),
                ("loops", "Avg Loops"),
                ("time", "Time (s)"),
            ],
            caption="Main Results on HumanEval",
            label="tab:main-results",
            highlight_best="pass_rate",
        )

        # Save
        (self.output_dir / "main_table.tex").write_text(outputs["main_table"])

        return outputs

    def generate_demo_figures(self):
        """Generate demo figures with sample data."""
        # Sample main comparison data
        main_data = {
            "GPT-4o Alone": 0.841,
            "Claude Alone": 0.852,
            "Gemini Alone": 0.823,
            "CMVK (GPT→Gem)": 0.924,
            "CMVK (GPT→Claude)": 0.918,
            "CMVK (o1→Gem)": 0.931,
        }

        print("=" * 60)
        print("MAIN COMPARISON CHART")
        print("=" * 60)
        ascii_chart = ASCIIChart.bar_chart(main_data, "HumanEval Pass@1 Results")
        print(ascii_chart)

        # Save
        self.generate_main_comparison(main_data)

        # Sample ablation data
        ablation_data = {
            "GPT-4o": {
                "Self-Verify": 0.841,
                "Cross-Verify": 0.924,
            },
            "Claude": {
                "Self-Verify": 0.852,
                "Cross-Verify": 0.918,
            },
            "Gemini": {
                "Self-Verify": 0.823,
                "Cross-Verify": 0.911,
            },
        }

        print("\n" + "=" * 60)
        print("ABLATION STUDY")
        print("=" * 60)
        ablation_chart = ASCIIChart.grouped_bar_chart(
            ablation_data, "Self-Verification vs Cross-Model"
        )
        print(ablation_chart)

        self.generate_ablation_figure(ablation_data)

        # Sample table data
        table_data = [
            {"method": "GPT-4o Alone", "pass_rate": 0.841, "delta": 0, "loops": 1.0, "time": 2.1},
            {
                "method": "Claude Alone",
                "pass_rate": 0.852,
                "delta": 0.011,
                "loops": 1.0,
                "time": 2.3,
            },
            {
                "method": "CMVK (GPT→Gem)",
                "pass_rate": 0.924,
                "delta": 0.083,
                "loops": 1.8,
                "time": 4.2,
            },
            {
                "method": "CMVK (o1→Gem)",
                "pass_rate": 0.931,
                "delta": 0.090,
                "loops": 1.5,
                "time": 8.1,
            },
        ]

        print("\n" + "=" * 60)
        print("ASCII TABLE")
        print("=" * 60)
        ascii_table = ASCIIChart.table(
            table_data, ["method", "pass_rate", "delta", "loops", "time"], "Main Results"
        )
        print(ascii_table)

        # LaTeX table
        print("\n" + "=" * 60)
        print("LATEX TABLE")
        print("=" * 60)
        tables = self.generate_latex_tables(table_data)
        print(tables["main_table"])

        print(f"\nFigures saved to: {self.output_dir}")


# ============================================================================
# CLI
# ============================================================================


def parse_args():
    parser = argparse.ArgumentParser(description="Visualize CMVK experiment results")
    parser.add_argument(
        "--input",
        "-i",
        help="Path to results JSON file",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="figures",
        help="Output directory for figures",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Generate demo figures with sample data",
    )
    parser.add_argument(
        "--format",
        choices=["ascii", "svg", "both"],
        default="both",
        help="Output format",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    visualizer = ResultsVisualizer(output_dir=args.output)

    if args.demo:
        visualizer.generate_demo_figures()
    elif args.input:
        results = visualizer.load_results(args.input)
        # Process based on results structure
        if "aggregates" in results:
            # Ablation results
            data = {k: v["pass_rate_mean"] for k, v in results["aggregates"].items()}
            visualizer.generate_main_comparison(data)
        else:
            print("Unknown results format. Use --demo for sample figures.")
    else:
        print("Use --demo for sample figures or --input to process results")
        print("\nExample:")
        print("  python visualize_results.py --demo")
        print("  python visualize_results.py --input ablation_results.json")


if __name__ == "__main__":
    main()
