#!/bin/bash
#
# Build PDF from paper draft
# Requires: pandoc, xelatex (or pdflatex)
#

set -e

echo "Building paper PDFs..."

# Check for pandoc
if ! command -v pandoc &> /dev/null; then
    echo "Error: pandoc not found. Install with:"
    echo "  Windows: choco install pandoc"
    echo "  Mac: brew install pandoc"
    echo "  Linux: apt install pandoc"
    exit 1
fi

# Build main paper (with author info - for arXiv)
echo "Converting main.md to PDF..."
pandoc main.md \
    -o paper.pdf \
    --pdf-engine=xelatex \
    -V geometry:margin=1in \
    -V fontsize=11pt \
    --toc \
    --number-sections \
    --bibliography=references.bib \
    --citeproc \
    2>/dev/null || pandoc main.md -o paper.pdf --pdf-engine=pdflatex -V geometry:margin=1in

echo "✓ Created paper.pdf"

# Build anonymized paper (for double-blind review)
if [ -f "main_anonymous.md" ]; then
    echo "Converting main_anonymous.md to PDF..."
    pandoc main_anonymous.md \
        -o paper_anonymous.pdf \
        --pdf-engine=xelatex \
        -V geometry:margin=1in \
        -V fontsize=11pt \
        --toc \
        --number-sections \
        --bibliography=references.bib \
        --citeproc \
        2>/dev/null || pandoc main_anonymous.md -o paper_anonymous.pdf --pdf-engine=pdflatex -V geometry:margin=1in
    echo "✓ Created paper_anonymous.pdf"
fi

# Build appendix if exists
if [ -f "appendix.md" ]; then
    echo "Converting appendix.md to PDF..."
    pandoc appendix.md \
        -o appendix.pdf \
        --pdf-engine=xelatex \
        -V geometry:margin=1in \
        -V fontsize=10pt \
        --bibliography=references.bib \
        --citeproc \
        2>/dev/null || pandoc appendix.md -o appendix.pdf --pdf-engine=pdflatex -V geometry:margin=1in
    echo "✓ Created appendix.pdf"
fi

echo ""
echo "Build complete!"
echo "Files created:"
ls -la *.pdf 2>/dev/null || echo "  (no PDFs found - check for errors)"
