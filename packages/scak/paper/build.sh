#!/bin/bash
# Build SCAK paper PDF from markdown
# Prerequisites: pandoc, xelatex (or pdflatex)

set -e

echo "========================================"
echo "Building SCAK Paper PDF"
echo "========================================"

# Check for pandoc
if ! command -v pandoc &> /dev/null; then
    echo "Error: pandoc not found. Install from https://pandoc.org/installing.html"
    exit 1
fi

# Build PDF with bibliography
echo "Generating PDF..."
pandoc paper_draft.md \
    -o scak_paper.pdf \
    --pdf-engine=xelatex \
    --bibliography=bibliography.bib \
    --citeproc \
    -V geometry:margin=1in \
    -V fontsize=11pt \
    -V documentclass=article \
    --highlight-style=tango \
    --toc=false

echo "✓ Generated: scak_paper.pdf"

# Optional: Generate LaTeX source
echo "Generating LaTeX source..."
pandoc paper_draft.md \
    -o scak_paper.tex \
    --bibliography=bibliography.bib \
    --citeproc \
    -V geometry:margin=1in \
    -V fontsize=11pt \
    -V documentclass=article \
    --standalone

echo "✓ Generated: scak_paper.tex"

echo ""
echo "========================================"
echo "Build complete!"
echo "========================================"
echo ""
echo "Output files:"
echo "  - scak_paper.pdf (main PDF)"
echo "  - scak_paper.tex (LaTeX source)"
echo ""
echo "For NeurIPS submission, use the official template:"
echo "  https://neurips.cc/Conferences/2026/PaperInformation/StyleFiles"
