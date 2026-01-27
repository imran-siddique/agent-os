# Release Guide

This guide provides step-by-step instructions for releasing Context-as-a-Service.

## Pre-Release Checklist

- [ ] All tests passing (`pytest tests/`)
- [ ] CHANGELOG.md updated with release notes
- [ ] Version bumped in `pyproject.toml`
- [ ] Documentation up to date
- [ ] No uncommitted changes

## 1. PyPI Release

### Prerequisites

```bash
# Install build tools
pip install build twine

# Verify you have PyPI credentials
# Option A: ~/.pypirc file
# Option B: TWINE_USERNAME and TWINE_PASSWORD environment variables
# Option C: Use API token (recommended)
```

### Build and Upload

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info/

# Build the package
python -m build

# Check the package
twine check dist/*

# Upload to TestPyPI first (recommended)
twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ context-as-a-service

# If everything works, upload to PyPI
twine upload dist/*
```

### Verify Installation

```bash
# Create a fresh virtual environment
python -m venv test-env
source test-env/bin/activate  # Windows: test-env\Scripts\activate

# Install from PyPI
pip install context-as-a-service

# Test import
python -c "import caas; print(caas.__version__)"

# Test CLI
caas --help

# Cleanup
deactivate
rm -rf test-env
```

## 2. GitHub Release

### Create and Push Tag

```bash
# Ensure you're on main branch with latest changes
git checkout main
git pull origin main

# Create annotated tag
git tag -a v0.1.0 -m "Release v0.1.0 - Initial public release"

# Push tag to GitHub
git push origin v0.1.0
```

### Create GitHub Release

1. Go to https://github.com/imran-siddique/context-as-a-service/releases
2. Click "Draft a new release"
3. Select the tag `v0.1.0`
4. Set release title: `v0.1.0 - Initial Release`
5. Copy release notes from CHANGELOG.md
6. Check "Set as the latest release"
7. Click "Publish release"

### Alternative: GitHub CLI

```bash
# Install GitHub CLI if needed: https://cli.github.com/
gh release create v0.1.0 \
  --title "v0.1.0 - Initial Release" \
  --notes-file CHANGELOG.md \
  dist/*
```

## 3. Hugging Face Dataset Upload

### Prerequisites

```bash
# Install Hugging Face Hub
pip install huggingface_hub datasets

# Login to Hugging Face
huggingface-cli login
# Enter your access token from https://huggingface.co/settings/tokens
```

### Upload Dataset

#### Option A: Using the Hub Library

```python
from huggingface_hub import HfApi, create_repo
from pathlib import Path

# Create the repository
api = HfApi()
repo_id = "mosiddi/caas-benchmark-corpus-v1"

try:
    create_repo(repo_id, repo_type="dataset", private=False)
except Exception as e:
    print(f"Repo may already exist: {e}")

# Upload the entire sample_corpus directory
api.upload_folder(
    folder_path="benchmarks/data/sample_corpus",
    repo_id=repo_id,
    repo_type="dataset",
)

print(f"Dataset uploaded to: https://huggingface.co/datasets/{repo_id}")
```

#### Option B: Using CLI

```bash
# Create dataset repository
huggingface-cli repo create caas-benchmark-corpus-v1 --type dataset

# Clone it locally
git clone https://huggingface.co/datasets/mosiddi/caas-benchmark-corpus-v1
cd caas-benchmark-corpus-v1

# Copy files
cp -r ../context-as-a-service/benchmarks/data/sample_corpus/* .

# Add, commit, push
git add .
git commit -m "Initial dataset upload"
git push
```

#### Option C: Web UI

1. Go to https://huggingface.co/new-dataset
2. Name: `caas-benchmark-corpus-v1`
3. License: MIT
4. Upload files from `benchmarks/data/sample_corpus/`
5. Ensure `DATASET_CARD.md` is renamed to `README.md` for HF

### Verify Dataset

```python
from datasets import load_dataset

# Test loading
dataset = load_dataset("mosiddi/caas-benchmark-corpus-v1")
print(dataset)
```

## 4. Post-Release Tasks

### Update README

Ensure badges point to live resources:

```markdown
[![PyPI version](https://badge.fury.io/py/context-as-a-service.svg)](https://pypi.org/project/context-as-a-service/)
[![Dataset on HF](https://img.shields.io/badge/🤗%20Dataset-CaaS%20Benchmark-yellow)](https://huggingface.co/datasets/mosiddi/caas-benchmark-corpus-v1)
```

### Announce Release

- [ ] Post on Twitter/X
- [ ] Post on LinkedIn
- [ ] Post on relevant subreddits (r/MachineLearning, r/LocalLLaMA)
- [ ] Post on Hacker News
- [ ] Update project documentation sites

### Monitor

- Watch PyPI download stats
- Monitor GitHub issues for bug reports
- Check Hugging Face dataset downloads

## Automated Release (CI/CD)

The repository includes a GitHub Action that automatically publishes to PyPI when a release is created:

`.github/workflows/publish-pypi.yml`

This workflow:
1. Triggers on GitHub release publication
2. Builds the package
3. Publishes to PyPI using trusted publishing

To enable:
1. Go to PyPI project settings
2. Add GitHub as a trusted publisher
3. Configure: owner=`imran-siddique`, repo=`context-as-a-service`, workflow=`publish-pypi.yml`

## Version Numbering

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

Examples:
- `0.1.0` → `0.1.1` (patch)
- `0.1.1` → `0.2.0` (minor)
- `0.2.0` → `1.0.0` (major)

## Rollback Procedure

If a release has critical issues:

### PyPI

```bash
# You cannot delete a release, but you can yank it
# This hides it from default installs but allows explicit version pins
pip install twine
twine yank context-as-a-service==0.1.0

# Then publish a fixed version
# Bump to 0.1.1 and release
```

### GitHub

```bash
# Delete the tag locally and remotely
git tag -d v0.1.0
git push origin :refs/tags/v0.1.0

# Delete the release via GitHub UI or CLI
gh release delete v0.1.0
```

## Quick Reference

```bash
# Full release sequence (after all checks pass)

# 1. Build and publish to PyPI
python -m build && twine upload dist/*

# 2. Tag and push
git tag -a v0.1.0 -m "Release v0.1.0"
git push origin v0.1.0

# 3. Create GitHub release
gh release create v0.1.0 --title "v0.1.0" --notes-file CHANGELOG.md

# 4. Upload to Hugging Face (run the Python script above)
python scripts/upload_to_hf.py
```

---

*Last updated: January 2026*
