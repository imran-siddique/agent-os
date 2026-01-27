# Paper Directory

This directory contains the research paper and related materials for AMB (Agent Message Bus).

## Files

- `whitepaper.md` - Full whitepaper in Markdown format (easy to read/share)
- `paper.tex` - LaTeX template for academic submission
- `figures/` - Directory for diagrams and charts (to be added)

## Building the LaTeX Paper

```bash
cd paper
pdflatex paper.tex
bibtex paper
pdflatex paper.tex
pdflatex paper.tex
```

Or use a LaTeX editor like Overleaf, TeXstudio, or VS Code with LaTeX Workshop.

## Updating Results

After running experiments, update the tables in both documents:

1. Run experiments: `python experiments/reproduce_results.py`
2. Copy results from `experiments/results.json` to the paper tables

## Citation

```bibtex
@software{amb2026,
  author = {Siddique, Imran},
  title = {AMB: A Broker-Agnostic Message Bus for AI Agents},
  year = {2026},
  url = {https://github.com/imran-siddique/amb},
  version = {0.1.0}
}
```
