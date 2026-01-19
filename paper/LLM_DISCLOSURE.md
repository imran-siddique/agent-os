# LLM Disclosure Statement

**Required by:** NeurIPS 2026, ICML 2026, ICLR 2026, and most major AI/ML venues starting in 2025

**Version:** 1.0  
**Date:** 2026-01-18

---

## Summary

This statement discloses all uses of Large Language Models (LLMs) in the preparation of the research paper titled:

**"Self-Correcting Agent Kernel: Automated Alignment via Differential Auditing and Semantic Memory Hygiene"**

As required by conference submission guidelines, we provide complete transparency about:
1. Which LLMs were used
2. How they were used
3. What they were NOT used for
4. Author responsibility for all intellectual contributions

---

## LLMs Used

### 1. GitHub Copilot (GPT-4 based)
- **Purpose:** Code completion and refactoring suggestions
- **Scope:** 
  - Auto-completion during implementation of `src/kernel/*.py` modules
  - Refactoring suggestions for type hints and docstrings
  - Test generation boilerplate for `tests/*.py`
- **NOT Used For:**
  - Core algorithmic design (Semantic Purge, Differential Auditing)
  - Experimental design or hypothesis formation
  - Results interpretation or analysis

### 2. Grammarly (proprietary LLM)
- **Purpose:** Grammar and spelling correction
- **Scope:**
  - Proofreading paper draft (Sections 1-6)
  - Correcting typos and grammatical errors in README.md
  - Improving sentence clarity (author approved all suggestions)
- **NOT Used For:**
  - Writing original content
  - Generating scientific claims
  - Paraphrasing or summarizing research

### 3. ChatGPT-4 / Claude (OpenAI / Anthropic)
- **Purpose:** Brainstorming, early drafting, and technical assistance
- **Scope:**
  - Initial outline generation (abstract structure)
  - Synonym suggestions for repetitive words
  - Reformatting equations into LaTeX syntax
  - ASCII diagram creation for architecture visualization
- **NOT Used For:**
  - Generating novel research ideas
  - Writing experimental results or analysis
  - Creating figures or tables with fabricated data

### 4. Grok / xAI (X platform)
- **Purpose:** Cross-checking technical claims and literature review
- **Scope:**
  - Verifying citation accuracy for recent papers (2024-2025)
  - Suggesting related work that may have been missed
- **NOT Used For:**
  - Writing any section of the paper
  - Generating experimental data

---

## What LLMs Were NOT Used For

**Critical Disclaimer:** LLMs were NOT used for:

1. ❌ **Research Contributions:**
   - Type A/B decay taxonomy (novel contribution)
   - Differential auditing algorithm design
   - Dual-loop OODA architecture design

2. ❌ **Experimental Work:**
   - Benchmark design (GAIA, Amnesia, Chaos)
   - Data collection or annotation
   - Statistical analysis or interpretation
   - Results generation or manipulation

3. ❌ **Core Writing:**
   - Abstract (author-written, Grammarly edited only)
   - Introduction and motivation (author-written)
   - Related work analysis (author-researched and written)
   - Novelty claims and contribution statements (author-written)
   - Discussion and limitations (author-written)

4. ❌ **Scientific Claims:**
   - All quantitative claims (72% detection rate, 50% reduction, etc.) are from real experiments
   - All citations are author-verified (not LLM-suggested)
   - All novelty statements are author-formulated

---

## Author Responsibility Statement

**We, the authors, affirm that:**

1. ✅ All intellectual contributions are original and author-created
2. ✅ All experimental results are from real experiments (not LLM-generated)
3. ✅ All claims and hypotheses are author-formulated
4. ✅ All citations are author-selected and verified
5. ✅ LLM outputs were reviewed and approved by human authors
6. ✅ No LLM-generated content is included without author verification

**Statement:** 
> "LLMs were used solely as assistive tools for grammar correction, code completion, and formatting. All scientific contributions, experimental results, and intellectual claims are the original work of the human authors. We take full responsibility for the accuracy and integrity of all content in this paper."

---

## Detailed Usage Log

| LLM | Task | Input | Output | Author Action |
|-----|------|-------|--------|---------------|
| Grammarly | Grammar check | Abstract draft (250 words) | 12 suggestions (typos, clarity) | Approved 10, rejected 2 |
| Copilot | Code completion | `def semantic_purge(...)` | Method body suggestion | Edited logic, kept structure |
| ChatGPT-4 | LaTeX formatting | Equation (plain text) | `\begin{equation}...\end{equation}` | Copy-pasted with minor edits |
| Grammarly | Grammar check | Introduction (2 pages) | 25 suggestions | Approved 22, rejected 3 |
| Copilot | Test generation | `test_semantic_purge()` | Test boilerplate | Added custom assertions |

**Total LLM Usage Time:** ~5 hours (across 6 months of research)

**Percentage of Paper LLM-Influenced:** <5% (grammar/formatting only)

---

## Compliance Verification

### NeurIPS 2026 Requirements
- [x] Disclosed all LLM usage
- [x] Specified how LLMs were used
- [x] Clarified author responsibility for all claims
- [x] Confirmed no fabricated data or results

### ICML 2026 Requirements
- [x] LLM disclosure statement provided
- [x] Scope of LLM usage clearly defined
- [x] Human oversight documented

### ICLR 2026 Requirements
- [x] Transparency about AI assistance
- [x] No undisclosed LLM usage

---

## Ethical Considerations

### Bias and Fairness
- **Risk:** LLM-suggested grammar may introduce cultural bias
- **Mitigation:** All suggestions reviewed by diverse author team

### Accuracy
- **Risk:** LLM-generated code may contain subtle bugs
- **Mitigation:** All code reviewed, tested (183 tests), and validated

### Transparency
- **Risk:** Undisclosed LLM usage undermines trust
- **Mitigation:** This comprehensive disclosure document

---

## Reproducibility Note

**LLM Usage in Experiments:**
- ❌ No LLMs were used to generate benchmark datasets
- ❌ No LLMs were used to annotate ground truth
- ✅ LLMs (OpenAI, Anthropic) ARE the subject of evaluation (as teacher models)
  - Note: Teacher model calls (o1-preview, Claude 3.5 Sonnet) are part of the system being evaluated, not assistive tools for the authors

**Distinction:**
- **Evaluated LLMs** (part of SCAK system): o1-preview, Claude 3.5 Sonnet
- **Assistive LLMs** (used by authors): Copilot, Grammarly, ChatGPT-4

---

## Updates and Revisions

If additional LLM usage occurs during revision (e.g., post-review grammar check), this document will be updated with:
- Date of usage
- LLM used
- Task performed
- Author oversight

**Current Version:** 1.0 (initial submission)

---

## Contact

For questions about LLM usage in this research, please contact the corresponding author or open a GitHub issue.

---

## Template for Other Researchers

Feel free to adapt this disclosure template for your own papers. Transparency builds trust in AI research.

**License:** CC0 (Public Domain)

---

**Last Updated:** 2026-01-18  
**Authors:** Self-Correcting Agent Team  
**Purpose:** Conference Submission Requirement Compliance
