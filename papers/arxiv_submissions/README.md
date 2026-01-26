# arXiv Submission Packages

Ready-to-upload packages for Agent OS research papers.

## Quick Reference

| Paper | Tarball | Category | Status |
|-------|---------|----------|--------|
| [02-cmvk](./02-cmvk/) | `submission.tar` (133 KB) | cs.SE | Ready |
| [03-caas](./03-caas/) | `submission.tar` (410 KB) | cs.CL | Ready |
| [05-control-plane](./05-control-plane/) | `submission.tar` (922 KB) | cs.AI | Ready |
| [06-scak](./06-scak/) | `submission.tar` (1.4 MB) | cs.AI | Ready |

## Submission Steps (per paper)

1. **Go to** https://arxiv.org/submit
2. **Upload** the `submission.tar` file from the paper's directory
3. **Verify** the file list shows only necessary files
4. **Check** the compiled PDF has no errors
5. **Enter metadata** from `ARXIV_METADATA.txt`:
   - Title (exact text, initial caps)
   - Authors (comma-separated)
   - Abstract (single line, no LaTeX)
   - Primary category
   - Cross-list categories
6. **Add comment**: "Part of the Agent OS project: https://github.com/imran-siddique/agent-os"
7. **Select license**: CC BY 4.0
8. **Preview and submit**

## Package Contents

Each package follows arXiv best practices:
- ✅ Comments removed from .tex files
- ✅ Figures flattened to root directory
- ✅ Pre-compiled .bbl bibliography included
- ✅ Style files included where needed
- ✅ No .aux, .log, .pdf, or other generated files
- ✅ arXiv recompilation hint added

## Regenerating Packages

```bash
cd papers/
python generate_arxiv_packages.py
```

## Paper Dependencies

```
02-cmvk ──────────┐
03-caas ──────────┼──→ 05-control-plane ──→ 06-scak
04-iatp (not LaTeX)
```

Consider submitting in dependency order to enable proper citations.

## Author

**Imran Siddique**  
Microsoft  
imran.siddique@microsoft.com
