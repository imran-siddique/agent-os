# arXiv / NeurIPS / ICLR Submission Checklist

This checklist ensures the CMVK paper meets venue requirements for top ML conferences.

## Pre-Submission Checklist

### 1. Paper Format & Structure

- [ ] **Page Limit**: ≤8 pages (NeurIPS/ICLR main), ≤9 pages (ICML)
- [ ] **Anonymous Submission**: No author names, affiliations, or identifying info
- [ ] **Template**: Using official venue LaTeX template
- [ ] **Font Size**: 10pt minimum (no squeezing)
- [ ] **Margins**: Per template (do not modify)
- [ ] **References**: Unlimited pages (not counted)
- [ ] **Appendix**: Unlimited pages (after references)

### 2. LLM Usage Disclosure ⚠️ IMPORTANT

**Required by most venues starting 2024:**

- [ ] Disclosed use of LLMs in research methodology
- [ ] Specified which LLMs used (GPT-4o, Gemini 1.5 Pro, Claude 3.5 Sonnet)
- [ ] Described prompts used (or stated they're in appendix/supplement)
- [ ] Noted any LLM assistance in writing (if applicable)
- [ ] API versions/dates documented

**Sample disclosure text:**
```
This work studies cross-model verification using large language models.
Specifically, we use GPT-4o (gpt-4o-2024-05-13) as Generator, and 
Gemini 1.5 Pro (gemini-1.5-pro-latest) or Claude 3.5 Sonnet as Verifier.
All prompts are provided in Appendix A. The code is MIT-licensed and
available at [anonymized for review].
```

### 3. Reproducibility Checklist

**Code & Data:**
- [ ] Code will be released (state license)
- [ ] Provide anonymized code link for review (e.g., anonymous GitHub)
- [ ] All hyperparameters documented
- [ ] Random seeds specified and fixed
- [ ] Dataset versions specified

**Environment:**
- [ ] Python version: 3.11
- [ ] All dependencies in `requirements.txt` with exact versions
- [ ] Hardware requirements documented (GPU optional, API keys required)
- [ ] Estimated compute cost documented

**Experiments:**
- [ ] Number of runs per experiment: ≥3 (recommend 5)
- [ ] Error bars / confidence intervals on all results
- [ ] Statistical significance tests (p < 0.05)
- [ ] Baseline comparisons are fair (same compute budget)

### 4. Ethics Statement

- [ ] Dual-use considerations discussed
- [ ] No personally identifiable information in datasets
- [ ] Safety considerations for code execution documented
- [ ] Prompt injection risks acknowledged
- [ ] No deceptive content generation

**Sample ethics text:**
```
This work presents a verification system that improves code reliability.
We acknowledge potential dual-use concerns: adversarial prompts in our
"prosecutor mode" could theoretically be adapted for malicious purposes.
We mitigate this by: (1) sandboxing all code execution, (2) rate-limiting
API calls, (3) releasing code under MIT license for transparency.
See Appendix B for detailed safety considerations.
```

### 5. Broader Impact Statement

- [ ] Positive impacts listed
- [ ] Potential negative impacts acknowledged
- [ ] Mitigation strategies described
- [ ] Environmental impact considered (API calls ≈ carbon cost)

### 6. Anonymization for Blind Review

**Remove from paper:**
- [ ] Author names and affiliations
- [ ] Acknowledgments (can add after acceptance)
- [ ] Personal URLs (use anonymous links)
- [ ] "Our previous work [Author et al.]" → "Prior work [XX]"
- [ ] Company/lab-specific references

**Code anonymization:**
- [ ] GitHub → Anonymous GitHub or OpenReview link
- [ ] Remove author names from code comments
- [ ] Remove personal API keys (obviously)
- [ ] Provide environment setup instructions

### 7. Figures & Tables

**Quality:**
- [ ] All figures ≥300 DPI for print
- [ ] Legible when printed in grayscale
- [ ] Colorblind-friendly palette used
- [ ] Axis labels and legends readable at printed size

**Content:**
- [ ] Figure 1: Architecture diagram
- [ ] Figure 2: Verification loop flow
- [ ] Figure 3: Main results (bar chart)
- [ ] Figure 4: Ablation study
- [ ] Table 1: Comparison with baselines
- [ ] Table 2: Model pair analysis

### 8. Related Work

- [ ] Self-consistency / self-verification methods cited
- [ ] Multi-agent debate papers cited
- [ ] Constitutional AI cited (if relevant)
- [ ] LLM-as-judge papers cited
- [ ] Code generation benchmarks cited (HumanEval, MBPP)
- [ ] No missing obvious citations

### 9. Claims & Evidence

- [ ] All claims supported by experiments or citations
- [ ] Limitations clearly stated
- [ ] No overclaiming ("solves" → "improves")
- [ ] Failure cases discussed

### 10. Final Checks

- [ ] Spell check completed
- [ ] Grammar check completed  
- [ ] All figures referenced in text
- [ ] All tables referenced in text
- [ ] All citations in bibliography
- [ ] Page numbers correct (if required)
- [ ] PDF renders correctly
- [ ] Supplementary material uploaded (if any)

---

## Venue-Specific Requirements

### NeurIPS 2024/2025

- Main paper: 8 pages
- References: unlimited
- Appendix: unlimited
- **Paper checklist**: REQUIRED (in LaTeX template)
- **Code**: Encouraged via OpenReview
- **Ethics review**: May be flagged for additional review

### ICLR 2024/2025

- Main paper: 8 pages
- References: unlimited
- Appendix: unlimited
- **Reproducibility checklist**: Required
- **OpenReview**: Comments visible during review

### ICML 2024/2025

- Main paper: 9 pages
- References: unlimited
- Appendix: unlimited
- **Impact statement**: Required
- **Code**: Submission via CMT

### arXiv (Preprint)

- No page limit
- Include author names (not anonymous)
- Use `cs.LG` (Machine Learning) as primary category
- Secondary: `cs.CL` (Computation and Language), `cs.SE` (Software Engineering)
- License: CC BY 4.0 recommended

---

## Quick Reference: Key Dates

Update these for your target venue:

| Venue | Abstract Due | Paper Due | Notification |
|-------|--------------|-----------|--------------|
| NeurIPS 2025 | TBD | TBD | TBD |
| ICLR 2025 | TBD | TBD | TBD |
| ICML 2025 | TBD | TBD | TBD |
| arXiv | Anytime | Anytime | Instant |

---

## Common Rejection Reasons to Avoid

1. **Novelty concerns**: Clearly state contribution vs. prior work
2. **Evaluation gaps**: Include multiple baselines, metrics, datasets
3. **Reproducibility**: Provide code, seeds, exact prompts
4. **Overclaiming**: Use measured language
5. **Missing related work**: Cite recent 2023-2024 papers
6. **Statistical rigor**: Include confidence intervals and p-values

---

## CMVK-Specific Items

### Unique Contributions to Highlight

1. **Cross-model verification** (not just self-verification)
2. **Graph of Truth** as explicit state representation
3. **Prosecutor Mode** for adversarial robustness
4. **Strategy banning** to avoid repetition
5. **Empirical validation** on HumanEval with significant improvement

### Key Results to Report

| Metric | Value | Notes |
|--------|-------|-------|
| HumanEval Pass@1 (baseline) | 84.1% | GPT-4o alone |
| HumanEval Pass@1 (CMVK) | 92.4% | GPT-4o + Gemini |
| Improvement | +8.3pp | Statistically significant |
| Sabotage Detection | 89% | Prosecutor mode |
| Avg Verification Loops | 1.8 | Efficiency |

### Code Release Plan

- [ ] Clean up code comments
- [ ] Add docstrings to all public functions
- [ ] Ensure all tests pass
- [ ] Create reproducibility script (`experiments/reproducible_runner.py`)
- [ ] Upload to HuggingFace (datasets)
- [ ] Create Colab notebook for easy replication
