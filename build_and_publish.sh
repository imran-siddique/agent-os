#!/bin/bash
# Build and publish script for SCAK PyPI package
# This script helps prepare the package for PyPI publication

set -e  # Exit on error

echo "======================================"
echo "SCAK Package Build & Publish Script"
echo "======================================"
echo ""

# Check if we're in the right directory
if [ ! -f "setup.py" ]; then
    echo "Error: setup.py not found. Run this script from the repository root."
    exit 1
fi

# Clean previous builds
echo "1. Cleaning previous builds..."
rm -rf build/ dist/ *.egg-info
echo "   ✓ Cleaned"
echo ""

# Install build dependencies
echo "2. Installing build dependencies..."
pip install --upgrade build twine
echo "   ✓ Dependencies installed"
echo ""

# Build the package
echo "3. Building package..."
python -m build
echo "   ✓ Package built successfully"
echo ""

# Check the distribution
echo "4. Checking package with twine..."
twine check dist/*
echo "   ✓ Package check passed"
echo ""

# Display package info
echo "5. Package information:"
echo "   Contents of dist/:"
ls -lh dist/
echo ""

# Instructions for publishing
echo "======================================"
echo "Package is ready for publication!"
echo "======================================"
echo ""
echo "To test on TestPyPI:"
echo "  twine upload --repository testpypi dist/*"
echo ""
echo "To publish to PyPI:"
echo "  twine upload dist/*"
echo ""
echo "To install locally and test:"
echo "  pip install dist/*.whl"
echo ""
echo "To create git tags:"
echo "  git tag -a v0.1.0 -m 'Release v0.1.0 - Initial prototype'"
echo "  git tag -a v1.0.0 -m 'Release v1.0.0 - Dual-loop architecture complete'"
echo "  git tag -a v1.1.0 -m 'Release v1.1.0 - Production features'"
echo "  git push origin --tags"
echo ""
