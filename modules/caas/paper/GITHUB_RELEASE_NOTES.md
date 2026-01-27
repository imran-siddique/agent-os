# GitHub Release v0.1.0 — Release Notes

Copy and paste this content when creating the GitHub release.

---

## Release Title
```
v0.1.0 — First Public Release 🎉
```

## Release Body (Markdown)

```markdown
# Context-as-a-Service v0.1.0

**🎉 First public release!** A principled framework for enterprise RAG systems that addresses seven critical fallacies in production deployments.

## 🚀 Highlights

- **28.1% improvement** in Precision@5 over flat-chunk baselines
- **0.003ms routing latency** — 150,000× faster than LLM-based routing
- **Five novel components**: Structure-Aware Indexing, Context Triad, Pragmatic Truth, Heuristic Router, Trust Gateway
- **Enterprise-ready**: Docker support, comprehensive tests, security features

## 📦 Installation

```bash
pip install context-as-a-service
```

Or with Docker:
```bash
docker pull ghcr.io/imran-siddique/context-as-a-service:latest
```

## 📊 Benchmark Results

| Metric | Baseline | CaaS | Improvement |
|--------|----------|------|-------------|
| Precision@5 | 0.640 ± 0.057 | 0.820 ± 0.045 | **+28.1%** |
| NDCG@10 | 0.610 ± 0.048 | 0.780 ± 0.042 | **+27.9%** |
| Routing Latency | N/A | 0.003ms | ⚡ |

*Statistical significance: p < 0.001, Cohen's d = 3.36 (large effect)*

## 📚 Resources

- **PyPI**: https://pypi.org/project/context-as-a-service/
- **Hugging Face Dataset**: https://huggingface.co/datasets/imran-siddique/context-as-a-service
- **Documentation**: See `/docs` folder
- **Paper Draft**: See `/paper` folder

## 🔧 Key Features

### Structure-Aware Indexing
Three-tier value hierarchy (High/Medium/Low) based on document structure.

### Context Triad
Hot/Warm/Cold prioritization with configurable token budgets:
- Hot: 2,000 tokens (current conversation)
- Warm: 1,000 tokens (user context)
- Cold: 5,000 tokens (retrieved knowledge)

### Pragmatic Truth
Surfaces practical knowledge from informal sources alongside official documentation.

### Heuristic Router
Deterministic, zero-latency query routing without ML inference.

### Trust Gateway
Enterprise security layer with input validation, audit logging, and rate limiting.

## 📝 What's Changed

See [CHANGELOG.md](CHANGELOG.md) for full details.

## 🙏 Acknowledgments

Built with support from the open-source community. Special thanks to all contributors!

---

**Full Changelog**: https://github.com/imran-siddique/context-as-a-service/commits/v0.1.0
```

---

## Instructions to Publish

1. Go to: https://github.com/imran-siddique/context-as-a-service/releases/new
2. **Choose a tag**: Select existing `v0.1.0`
3. **Release title**: `v0.1.0 — First Public Release 🎉`
4. **Description**: Paste the markdown content above
5. **Attachments** (optional): 
   - `paper/caas_paper_draft.pdf` (if compiled)
6. Click **Publish release**

## Verification Checklist

- [ ] Tag v0.1.0 selected
- [ ] Title includes version and emoji
- [ ] Links to PyPI, HF, docs all work
- [ ] CHANGELOG.md referenced
- [ ] Release is NOT marked as pre-release
