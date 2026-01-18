# Publishing Instructions for SCAK v1.1.0

This document provides step-by-step instructions for publishing SCAK to PyPI, Hugging Face, and creating releases.

## Prerequisites

Before publishing, ensure:
- [x] All tests pass: `pytest tests/ -v`
- [x] Package builds successfully: `python -m build`
- [x] Twine check passes: `twine check dist/*`
- [x] CHANGELOG.md is up to date
- [x] README.md is accurate
- [x] Version numbers are consistent

## 1. Publishing to PyPI

### Step 1: Test on TestPyPI (Recommended)

```bash
# Build the package
python -m build

# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ scak

# Verify it works
python -c "from src.kernel.auditor import CompletenessAuditor; print('Success!')"
```

### Step 2: Publish to Production PyPI

```bash
# Build fresh (if not already done)
python -m build

# Upload to PyPI (requires credentials)
twine upload dist/*

# Verify on PyPI
# Visit: https://pypi.org/project/scak/

# Test installation
pip install scak
```

### Step 3: Update Badges

After successful publication, update README.md badges:
```markdown
[![PyPI version](https://img.shields.io/pypi/v/scak.svg)](https://pypi.org/project/scak/)
[![Python](https://img.shields.io/pypi/pyversions/scak.svg)](https://pypi.org/project/scak/)
[![Downloads](https://img.shields.io/pypi/dm/scak.svg)](https://pypi.org/project/scak/)
```

## 2. Creating Git Tags and Releases

### Step 1: Create Annotated Tags

```bash
# Create tags for version history
git tag -a v0.1.0 -m "Release v0.1.0 - Initial prototype (2025-12-01)"
git tag -a v1.0.0 -m "Release v1.0.0 - Dual-loop architecture complete (2026-01-15)"
git tag -a v1.1.0 -m "Release v1.1.0 - Production features (2026-01-18)"

# Push tags to GitHub
git push origin --tags

# Verify tags
git tag -l -n1
```

### Step 2: Create GitHub Releases

For each tag, create a release on GitHub:

1. Go to: https://github.com/imran-siddique/self-correcting-agent-kernel/releases/new
2. Select the tag (e.g., v1.1.0)
3. Title: "SCAK v1.1.0 - Production Features"
4. Description: Copy relevant section from CHANGELOG.md
5. Attach dist files: `scak-1.1.0-py3-none-any.whl` and `scak-1.1.0.tar.gz`
6. Click "Publish release"

**Release Description Template for v1.1.0:**

```markdown
# Self-Correcting Agent Kernel v1.1.0

Production-ready release with LLM integrations, multi-agent orchestration, and advanced security.

## 🚀 Major Features

- Real LLM integrations (OpenAI GPT-4o, o1-preview, Anthropic Claude 3.5 Sonnet)
- Multi-agent orchestration framework
- Dynamic tool registry with multi-modal support
- Advanced security and governance layer
- Streamlit dashboard for monitoring
- CLI tool for agent management

## 📊 New Experiments

- Multi-Agent RAG Chain: +30% workflow success rate
- Long-Horizon Tasks: 30% context reduction over 15 steps

## 🔧 Installation

```bash
pip install scak

# Or with extras
pip install scak[llm]  # LLM integrations
pip install scak[dev]  # Development tools
pip install scak[all]  # Everything
```

## 📚 Documentation

- [README](https://github.com/imran-siddique/self-correcting-agent-kernel/blob/main/README.md)
- [Wiki](https://github.com/imran-siddique/self-correcting-agent-kernel/wiki)
- [Examples](https://github.com/imran-siddique/self-correcting-agent-kernel/tree/main/examples)
- [CHANGELOG](https://github.com/imran-siddique/self-correcting-agent-kernel/blob/main/CHANGELOG.md)

## 🔗 Links

- **PyPI:** https://pypi.org/project/scak/
- **Datasets:** https://huggingface.co/datasets/imran-siddique/scak-gaia-laziness
- **Paper:** arXiv (coming soon)

## ⚠️ Breaking Changes

None - fully backward compatible with v1.0.0

## 📈 Stats

- 183+ tests
- Zero security vulnerabilities
- Production-ready
- MIT License
```

## 3. Publishing Datasets to Hugging Face

### Step 1: Install Hugging Face CLI

```bash
pip install huggingface_hub
```

### Step 2: Login

```bash
huggingface-cli login
# Enter your access token from https://huggingface.co/settings/tokens
```

### Step 3: Create Dataset Repository

```bash
# Create new dataset repository
huggingface-cli repo create scak-gaia-laziness --type dataset --organization imran-siddique

# Or use web interface at: https://huggingface.co/new-dataset
```

### Step 4: Upload Dataset Files

```bash
# Upload dataset files
cd datasets/hf_upload
huggingface-cli upload imran-siddique/scak-gaia-laziness . --repo-type dataset

# Or use Python API
python -c "
from huggingface_hub import HfApi
api = HfApi()
api.upload_folder(
    folder_path='datasets/hf_upload',
    repo_id='imran-siddique/scak-gaia-laziness',
    repo_type='dataset'
)
"
```

### Step 5: Verify Dataset

1. Visit: https://huggingface.co/datasets/imran-siddique/scak-gaia-laziness
2. Check README renders correctly
3. Test dataset loading:

```python
from datasets import load_dataset

dataset = load_dataset("imran-siddique/scak-gaia-laziness")
print(f"Loaded {len(dataset['train'])} examples")
```

### Step 6: Update README

After successful upload, update main README.md:

```markdown
## Datasets

SCAK datasets are available on Hugging Face:

- **GAIA Laziness Benchmark**: [imran-siddique/scak-gaia-laziness](https://huggingface.co/datasets/imran-siddique/scak-gaia-laziness)
  - 50 vague queries for agent laziness detection
  - Categories: archived resources, renamed entities, time-based confusion, synonym issues

```python
from datasets import load_dataset
dataset = load_dataset("imran-siddique/scak-gaia-laziness")
```
```

## 4. Announcement Distribution

### Step 1: Twitter/X Threads

Post threads from `ANNOUNCEMENT_MATERIALS.md`:
1. Main announcement thread (7 tweets)
2. Technical deep dive thread (5 tweets)
3. For practitioners thread (4 tweets)

Schedule across 3 days for maximum reach.

### Step 2: Reddit

Post to r/MachineLearning:
- Use the detailed post from `ANNOUNCEMENT_MATERIALS.md`
- Tag as `[R]` (Research) or `[P]` (Project)
- Engage with comments promptly
- Cross-post to r/LanguageTechnology, r/OpenSource

### Step 3: Hacker News

Submit to Show HN:
- Title: "Show HN: Self-Correcting Agent Kernel – AI agents that learn from failures"
- URL: GitHub repo
- Include brief description in comments

### Step 4: LinkedIn

Post professional announcement:
- Use the LinkedIn post from `ANNOUNCEMENT_MATERIALS.md`
- Tag relevant hashtags
- Share in relevant groups

### Step 5: Discord Communities

Post in:
- LangChain Discord (#show-and-tell)
- AutoGPT Discord (#research)
- AI Agent Dev Discord (#projects)
- OpenAI Discord (#api-discussion)
- Hugging Face Discord (#datasets)

Use the message template from `ANNOUNCEMENT_MATERIALS.md`.

### Step 6: Email Newsletter (Optional)

If you have a newsletter:
- Announce the release
- Include key features and results
- Link to blog post (if created)

## 5. Demo Video

### Record and Upload

1. Follow `DEMO_VIDEO_SCRIPT.md` for recording
2. Edit video (add subtitles, music, graphics)
3. Upload to YouTube:
   - Title: "Self-Correcting Agent Kernel (SCAK) - AI Agents That Learn From Failures"
   - Description: Include links to GitHub, PyPI, docs
   - Tags: ai, agents, machine-learning, llm, production-ml, open-source

4. Embed in README:

```markdown
## 🎥 Demo Video

[![SCAK Demo](https://img.youtube.com/vi/YOUR_VIDEO_ID/0.jpg)](https://www.youtube.com/watch?v=YOUR_VIDEO_ID)

Watch a 2-minute overview of SCAK's key features and capabilities.
```

## 6. Paper Submission

### Prepare for arXiv

1. Compile paper from research notes
2. Include all experiment results
3. Add LIMITATIONS.md content
4. Format according to arXiv guidelines
5. Submit to relevant category (cs.AI, cs.LG, cs.SE)

### Update Links

After arXiv publication, update:
- README.md badges
- CITATION.cff
- setup.py metadata
- All announcement materials

## Checklist

Before declaring "published":

- [ ] PyPI package published and verified
- [ ] Git tags created and pushed
- [ ] GitHub releases created with dist files
- [ ] Datasets uploaded to Hugging Face
- [ ] README updated with dataset links
- [ ] Twitter threads posted
- [ ] Reddit post submitted
- [ ] Hacker News submission made
- [ ] LinkedIn post published
- [ ] Discord communities notified
- [ ] Demo video recorded and uploaded
- [ ] Demo video embedded in README
- [ ] Paper submitted to arXiv (if ready)
- [ ] All links verified working

## Post-Publication Monitoring

### Week 1
- Respond to comments on Reddit, HN
- Engage on Twitter
- Monitor GitHub issues
- Track PyPI download stats
- Collect feedback

### Week 2-4
- Write blog post with detailed walkthrough
- Create tutorial videos
- Engage with early adopters
- Address bug reports
- Plan next features based on feedback

---

**Last Updated:** 2026-01-18  
**Version:** 1.0
