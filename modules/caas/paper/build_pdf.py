#!/usr/bin/env python3
"""
Build paper PDF from Markdown sources.

Requirements:
    pip install markdown weasyprint

Usage:
    python paper/build_pdf.py              # Build full paper
    python paper/build_pdf.py --section abstract  # Build single section
"""

import argparse
import subprocess
import sys
from pathlib import Path
from datetime import datetime

PAPER_DIR = Path(__file__).parent
SECTIONS = [
    "abstract.md",
    "intro.md",
    "related_work.md",
    "method.md",
    "experiments.md",
    # "discussion.md",  # TODO
    # "conclusion.md",  # TODO
]

HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Context-as-a-Service: A Principled Architecture for Enterprise RAG Systems</title>
    <style>
        @page {{
            size: letter;
            margin: 1in;
        }}
        body {{
            font-family: 'Times New Roman', Times, serif;
            font-size: 11pt;
            line-height: 1.4;
            max-width: 6.5in;
            margin: 0 auto;
            padding: 20px;
        }}
        h1 {{
            font-size: 16pt;
            text-align: center;
            margin-bottom: 0.5em;
        }}
        h2 {{
            font-size: 12pt;
            margin-top: 1.5em;
            margin-bottom: 0.5em;
        }}
        h3 {{
            font-size: 11pt;
            font-style: italic;
            margin-top: 1em;
            margin-bottom: 0.3em;
        }}
        p {{
            text-align: justify;
            margin-bottom: 0.8em;
        }}
        code {{
            font-family: 'Courier New', monospace;
            font-size: 9pt;
            background-color: #f5f5f5;
            padding: 1px 3px;
        }}
        pre {{
            font-family: 'Courier New', monospace;
            font-size: 9pt;
            background-color: #f5f5f5;
            padding: 10px;
            overflow-x: auto;
        }}
        blockquote {{
            border-left: 3px solid #ccc;
            margin-left: 0;
            padding-left: 1em;
            color: #555;
        }}
        strong {{
            font-weight: bold;
        }}
        em {{
            font-style: italic;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 1em 0;
            font-size: 10pt;
        }}
        th, td {{
            border: 1px solid #ccc;
            padding: 6px 10px;
            text-align: left;
        }}
        th {{
            background-color: #f0f0f0;
        }}
        .title {{
            text-align: center;
            margin-bottom: 2em;
        }}
        .author {{
            text-align: center;
            font-size: 11pt;
            margin-bottom: 0.5em;
        }}
        .affiliation {{
            text-align: center;
            font-size: 10pt;
            color: #666;
            margin-bottom: 2em;
        }}
        .abstract {{
            margin: 2em 0;
            padding: 1em;
            background-color: #fafafa;
            border: 1px solid #eee;
        }}
        .abstract h2 {{
            margin-top: 0;
        }}
        hr {{
            border: none;
            border-top: 1px solid #ccc;
            margin: 2em 0;
        }}
        .page-break {{
            page-break-after: always;
        }}
        .footer {{
            font-size: 9pt;
            color: #999;
            text-align: center;
            margin-top: 3em;
        }}
    </style>
</head>
<body>
    <div class="title">
        <h1>Context-as-a-Service:<br>A Principled Architecture for Enterprise RAG Systems</h1>
    </div>
    <div class="author">
        Anonymous Author(s)
    </div>
    <div class="affiliation">
        Anonymous Institution
    </div>
    
    {content}
    
    <div class="footer">
        <p>Draft generated {date} | Code: <a href="https://github.com/imran-siddique/context-as-a-service">GitHub</a> | Data: <a href="https://huggingface.co/datasets/imran-siddique/context-as-a-service">Hugging Face</a></p>
    </div>
</body>
</html>
"""


def check_dependencies():
    """Check if required tools are available."""
    # Try pandoc first (preferred)
    try:
        result = subprocess.run(
            ["pandoc", "--version"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return "pandoc"
    except FileNotFoundError:
        pass
    
    # Try weasyprint as fallback
    try:
        import weasyprint
        return "weasyprint"
    except ImportError:
        pass
    
    # Try markdown + pdfkit
    try:
        import markdown
        import pdfkit
        return "pdfkit"
    except ImportError:
        pass
    
    return None


def read_markdown(filepath: Path) -> str:
    """Read and preprocess markdown file."""
    content = filepath.read_text(encoding="utf-8")
    
    # Remove YAML frontmatter if present
    if content.startswith("---"):
        end = content.find("---", 3)
        if end != -1:
            content = content[end + 3:].strip()
    
    # Remove markdown comments
    lines = []
    for line in content.split("\n"):
        if not line.strip().startswith("<!--"):
            lines.append(line)
    
    return "\n".join(lines)


def build_with_pandoc(md_files: list, output: Path):
    """Build PDF using pandoc."""
    cmd = [
        "pandoc",
        "-f", "markdown",
        "-t", "pdf",
        "--pdf-engine=xelatex",
        "-V", "geometry:margin=1in",
        "-V", "fontsize=11pt",
        "-o", str(output),
    ] + [str(f) for f in md_files]
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Pandoc error: {result.stderr}")
        return False
    return True


def build_with_weasyprint(md_files: list, output: Path):
    """Build PDF using weasyprint."""
    import markdown
    from weasyprint import HTML
    
    # Combine all markdown
    combined_md = ""
    for f in md_files:
        combined_md += read_markdown(f) + "\n\n---\n\n"
    
    # Convert to HTML
    md_converter = markdown.Markdown(extensions=['tables', 'fenced_code'])
    html_content = md_converter.convert(combined_md)
    
    # Wrap in template
    full_html = HTML_TEMPLATE.format(
        content=html_content,
        date=datetime.now().strftime("%Y-%m-%d")
    )
    
    # Generate PDF
    html = HTML(string=full_html)
    html.write_pdf(output)
    return True


def build_html(md_files: list, output: Path):
    """Build HTML (always works, no dependencies)."""
    import re
    
    combined_md = ""
    for f in md_files:
        combined_md += read_markdown(f) + "\n\n<hr>\n\n"
    
    # Simple markdown to HTML conversion
    html = combined_md
    
    # Headers
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)  # Demote h1 to h2
    
    # Bold and italic
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
    
    # Code
    html = re.sub(r'`(.+?)`', r'<code>\1</code>', html)
    
    # Paragraphs (simple)
    html = re.sub(r'\n\n', '</p><p>', html)
    html = f'<p>{html}</p>'
    
    # Wrap in template
    full_html = HTML_TEMPLATE.format(
        content=html,
        date=datetime.now().strftime("%Y-%m-%d")
    )
    
    output.write_text(full_html, encoding="utf-8")
    return True


def main():
    parser = argparse.ArgumentParser(description="Build paper PDF from Markdown")
    parser.add_argument("--section", help="Build single section only")
    parser.add_argument("--output", "-o", help="Output filename")
    parser.add_argument("--format", choices=["pdf", "html"], default="html",
                       help="Output format (default: html)")
    args = parser.parse_args()
    
    # Determine which files to build
    if args.section:
        md_files = [PAPER_DIR / f"{args.section}.md"]
        if not md_files[0].exists():
            md_files = [PAPER_DIR / args.section]
        if not md_files[0].exists():
            print(f"Section not found: {args.section}")
            return 1
    else:
        md_files = [PAPER_DIR / s for s in SECTIONS if (PAPER_DIR / s).exists()]
    
    print(f"Building from: {[f.name for f in md_files]}")
    
    # Determine output path
    if args.output:
        output = Path(args.output)
    else:
        output = PAPER_DIR / f"caas_paper_draft.{args.format}"
    
    # Build
    if args.format == "pdf":
        tool = check_dependencies()
        if tool == "pandoc":
            success = build_with_pandoc(md_files, output)
        elif tool == "weasyprint":
            success = build_with_weasyprint(md_files, output)
        else:
            print("No PDF tools available. Install pandoc or: pip install weasyprint")
            print("Falling back to HTML...")
            output = output.with_suffix(".html")
            success = build_html(md_files, output)
    else:
        success = build_html(md_files, output)
    
    if success:
        print(f"✓ Built: {output}")
        print(f"  Size: {output.stat().st_size / 1024:.1f} KB")
        return 0
    else:
        print("✗ Build failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
