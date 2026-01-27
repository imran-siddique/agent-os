# arXiv Submission Package

## Contents

```
arxiv_submission.zip
├── main.tex           # Main LaTeX source file
├── references.bib     # BibTeX bibliography
└── figures/
    ├── fig1_system_architecture.png  # System architecture diagram
    ├── fig2_context_triad.png        # Context Triad visualization
    ├── fig3_ablation_results.png     # Ablation study bar chart
    └── fig4_routing_latency.png      # Routing latency comparison
```

## Compilation

```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

## arXiv Submission Steps

1. Go to: https://arxiv.org/submit
2. Sign in (or create account)
3. Start new submission
4. Fill in metadata:
   - **Primary Category**: `cs.AI` (Artificial Intelligence)
   - **Cross-list**: `cs.CL` (Computation and Language), `cs.IR` (Information Retrieval)
   - **Title**: Context-as-a-Service: A Principled Architecture for Enterprise RAG Systems
   - **License**: CC BY 4.0
5. Upload `arxiv_submission.zip`
6. In **Comments** field, add:
   ```
   Code: https://github.com/imran-siddique/context-as-a-service
   PyPI: https://pypi.org/project/context-as-a-service/
   Dataset: https://huggingface.co/datasets/imran-siddique/context-as-a-service
   ```
7. Preview and submit

## Package Size

- Total: ~363 KB
- Within arXiv's 10MB limit ✓
