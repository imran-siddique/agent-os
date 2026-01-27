# Paper Outline

**Working Title:** Context-as-a-Service: A Principled Architecture for Enterprise RAG Systems

---

## 1. Abstract (~250 words)
- Problem: Seven fallacies in production RAG
- Solution: CaaS framework with 5 novel components
- Results: +28% Precision@5, sub-ms routing, enterprise-ready
- See [abstract.md](abstract.md) for current draft

## 2. Introduction (1.5 pages)
- Motivation: RAG is ubiquitous but broken at scale
- The Seven Fallacies (brief enumeration)
- Contributions (numbered list):
  1. Taxonomy of RAG pitfalls
  2. Structure-aware indexing
  3. Context Triad (Hot/Warm/Cold)
  4. Pragmatic Truth tracking
  5. Trust Gateway architecture
  6. Heuristic Router
  7. Open benchmark corpus

## 3. Related Work (1 page)
- See [../docs/RELATED_WORK.md](../docs/RELATED_WORK.md)
- RAG frameworks (LlamaIndex, LangChain, Haystack)
- Context management (MemGPT, Reflexion)
- Enterprise AI deployment challenges
- Temporal/decay-based retrieval

## 4. The Seven Fallacies (1 page)
- 4.1 Flat Chunk Fallacy (Structure)
- 4.2 Context Amnesia (Metadata)
- 4.3 Time-Blind Retrieval (Temporal)
- 4.4 Flat Context Fallacy (Priority)
- 4.5 Official Truth Fallacy (Source)
- 4.6 Brutal Squeeze (Summarization)
- 4.7 Middleware Gap (Trust)

## 5. Method: CaaS Architecture (2 pages)
- 5.1 System Overview (Figure 1: Architecture diagram)
- 5.2 Structure-Aware Indexing
  - Three-tier value hierarchy (High/Medium/Low)
  - Algorithm 1: Structure detection
- 5.3 Context Triad
  - Hot: Current conversation
  - Warm: User preferences, recent docs
  - Cold: Historical archives
  - Figure 2: Triad visualization
- 5.4 Pragmatic Truth
  - Official vs. practical knowledge
  - Conflict detection algorithm
- 5.5 Heuristic Router
  - Deterministic routing rules
  - Zero-latency design
- 5.6 Trust Gateway
  - On-premises deployment
  - Security properties

## 6. Experiments (2 pages)
- 6.1 Benchmark Corpus
  - 16 enterprise documents
  - Domain distribution (Table 1)
  - Available on Hugging Face
- 6.2 Baselines
  - Naive chunking (500 tokens)
  - LlamaIndex default
  - LangChain default
- 6.3 Metrics
  - Precision@K, NDCG@K
  - Routing latency
  - Token efficiency
- 6.4 Results
  - Table 2: Main results (+28.1% P@5)
  - Table 3: Ablation study
  - Table 4: Latency comparison (0.003ms routing)
- 6.5 Statistical Significance
  - Paired t-tests (p < 0.001)
  - Cohen's d = 3.36 (large effect)

## 7. Discussion (0.5 pages)
- Limitations
  - Small benchmark corpus (16 docs)
  - Synthetic documents
  - No end-to-end LLM evaluation
- Broader Impact
  - Enterprise adoption considerations
  - Privacy implications of Trust Gateway
- Future Work
  - Larger evaluation corpora
  - Integration with more LLM providers
  - Learned routing (optional hybrid)

## 8. Conclusion (0.5 pages)
- Summary of contributions
- Call to action: open-source, reproducible

## 9. References
- ~30-40 citations
- RAG papers, enterprise AI, context management

---

## Appendices (Supplementary)
- A. Full hyperparameter tables
- B. Additional qualitative examples
- C. Pseudocode for all algorithms
- D. Dataset card

---

## Figures Needed
- [ ] Fig 1: System architecture
- [ ] Fig 2: Context Triad diagram
- [ ] Fig 3: Structure-aware indexing example
- [ ] Fig 4: Results bar chart

## Tables Needed
- [x] Table 1: Corpus statistics (in dataset card)
- [x] Table 2: Main results (from run_evaluation.py)
- [x] Table 3: Ablation study (from run_evaluation.py)
- [x] Table 4: Statistical tests (from statistical_tests.py)
