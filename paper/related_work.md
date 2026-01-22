# Related Work

*Adapted from [docs/RELATED_WORK.md](../docs/RELATED_WORK.md)*

## Retrieval-Augmented Generation

The foundation of modern RAG systems traces to Lewis et al. [1], who introduced the paradigm of combining retrieval with generation for knowledge-intensive NLP tasks. Subsequent work by Guu et al. [2] demonstrated the benefits of retrieval-augmented pre-training, while Izacard & Grave [3] developed the Fusion-in-Decoder architecture for open-domain QA.

CaaS differs from these foundational approaches by focusing on the **serving-time context management** problem rather than the retrieval mechanism itself. We assume any retriever (dense, sparse, or hybrid) and instead optimize how retrieved context is organized, prioritized, and presented to the LLM.

## Document Structure and Hierarchical Indexing

Hierarchical document understanding has been explored in summarization [4, 5] and document-level NLP [6]. These works demonstrate that respecting document structure improves downstream performance. CaaS applies this insight to RAG through our **three-tier value hierarchy** (High/Medium/Low), which explicitly encodes structural importance into the retrieval ranking.

Unlike learned hierarchical representations, CaaS uses **deterministic heuristics** based on document type detection (code, legal, policy, etc.), enabling zero-latency decisions without model inference.

## Temporal Information Retrieval

The importance of time in retrieval has been studied extensively in web search [7] and more recently in LLM contexts [8, 9]. Kasai et al. [10] introduced RealTime QA, demonstrating that time-sensitive questions require time-aware retrieval. Lazaridou et al. [11] showed that language models struggle with temporal knowledge degradation.

CaaS implements **explicit time-based decay** with configurable half-life parameters, inspired by radioactive decay models. Unlike implicit temporal signals in embeddings, our approach provides transparent, explainable temporal weighting.

## Source Attribution and Provenance

Recent work on attribution [12, 13, 14] addresses the challenge of tracing generated content to sources. Menick et al. [12] trained models to support answers with verified quotes, while Rashkin et al. [14] developed metrics for attribution quality.

CaaS's **Pragmatic Truth** module extends attribution by explicitly tracking **conflicts between sources**—surfacing when official documentation disagrees with informal sources (Slack, tickets, incident reports). This addresses a gap in current attribution systems that assume source consistency.

## The Accumulation Paradox and Long-Context Degradation

A growing body of work reveals a counterintuitive phenomenon we term the **Accumulation Paradox**: adding more context to LLMs can paradoxically *degrade* rather than improve performance. Liu et al. [21] demonstrated this empirically in their landmark "Lost in the Middle" study, showing that model performance follows a U-shaped curve where information in the middle of long contexts is systematically ignored. They found that "performance can degrade significantly when changing the position of relevant information, indicating that current language models do not robustly make use of information in long input contexts."

This degradation extends to streaming and agentic settings. Xiao et al. [22] showed that window attention mechanisms fail entirely when context length exceeds cache size, introducing the "attention sink" phenomenon where initial tokens receive disproportionate attention regardless of semantic relevance. Li et al. [23] further demonstrated that even purpose-built long-context LLMs struggle with accumulated context, revealing biases toward later-presented information and degraded reasoning over multiple context pieces.

For agentic AI systems with extended interactions, Packer et al. [24] (MemGPT) showed that raw context accumulation cannot sustain long-running agents, proposing virtual context management inspired by operating system memory hierarchies. This work directly motivates CaaS's approach: rather than assuming more context is better, we implement **intelligent context decay and prioritization** that acknowledges the Accumulation Paradox.

CaaS addresses these challenges through: (1) **time-based decay** that naturally deprioritizes older context before it causes degradation, (2) **the Context Triad** (Hot/Warm/Cold) that ensures the most relevant context occupies attention-friendly positions, and (3) **structure-aware indexing** that prevents low-value content from diluting the context window.

## Context Window Management

Managing long conversations and context windows is a growing challenge as LLMs are deployed in production [15, 16]. Common approaches include summarization [17] and compression [18], but these introduce lossy transformations that can discard critical details.

CaaS takes a different approach with **FIFO sliding window management**: rather than summarizing poorly, we truncate precisely. Our philosophy—"Chopping > Summarizing"—preserves recent turns losslessly while accepting that older context is simply dropped. This design choice reflects the empirical observation that users rarely reference content from many turns ago, but frequently reference the exact code or error message from seconds ago.

## Enterprise AI Deployment

The enterprise deployment of LLMs introduces unique challenges around security, compliance, and data sovereignty [19, 20]. While cloud-based routing services offer cost optimization through model selection, they create unacceptable data leakage risks for sensitive enterprise data.

CaaS's **Trust Gateway** addresses this through an on-premises deployment model. Rather than competing on routing intelligence, we compete on trust: enterprises deploy the gateway behind their firewall, maintaining complete data sovereignty while still benefiting from intelligent context serving.

---

## References

[1] Lewis, P., et al. (2020). "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks." *NeurIPS 2020*. https://arxiv.org/abs/2005.11401

[2] Guu, K., et al. (2020). "REALM: Retrieval-Augmented Language Model Pre-Training." *ICML 2020*. https://arxiv.org/abs/2002.08909

[3] Izacard, G., & Grave, E. (2021). "Leveraging Passage Retrieval with Generative Models for Open Domain Question Answering." *EACL 2021*. https://arxiv.org/abs/2007.01282

[4] Cohan, A., et al. (2018). "A Discourse-Aware Attention Model for Abstractive Summarization of Long Documents." *NAACL 2018*. https://arxiv.org/abs/1804.05685

[5] Liu, Y., & Lapata, M. (2019). "Hierarchical Transformers for Multi-Document Summarization." *ACL 2019*. https://arxiv.org/abs/1905.13164

[6] Xiao, W., & Carenini, G. (2019). "Extractive Summarization of Long Documents by Combining Global and Local Context." *EMNLP 2019*. https://arxiv.org/abs/1909.08089

[7] Campos, R., et al. (2014). "Survey of Temporal Information Retrieval and Scoping Methods." *WWW Journal*. DOI: 10.1007/s11280-013-0230-y

[8] Dai, Z., & Callan, J. (2019). "Deeper Text Understanding for IR with Contextual Neural Language Modeling." *SIGIR 2019*. https://arxiv.org/abs/1905.09217

[9] Nguyen, T., et al. (2016). "A Neural Network Approach to Context-Sensitive Generation of Conversational Responses." *NAACL 2016*. https://arxiv.org/abs/1506.06714

[10] Kasai, J., et al. (2022). "RealTime QA: What's the Answer Right Now?" *NeurIPS 2022*. https://arxiv.org/abs/2207.13332

[11] Lazaridou, A., et al. (2021). "Mind the Gap: Assessing Temporal Generalization in Neural Language Models." *NeurIPS 2021*. https://arxiv.org/abs/2102.01951

[12] Menick, J., et al. (2022). "Teaching Language Models to Support Answers with Verified Quotes." *NeurIPS 2022*. https://arxiv.org/abs/2203.11147

[13] Gao, L., et al. (2022). "Rarr: Researching and Revising What Language Models Say, Using Language Models." *ACL 2023*. https://arxiv.org/abs/2210.08726

[14] Rashkin, H., et al. (2021). "Measuring Attribution in Natural Language Generation Models." *Computational Linguistics 2021*. https://arxiv.org/abs/2112.12870

[15] Dinan, E., et al. (2019). "Wizard of Wikipedia: Knowledge-Powered Conversational Agents." *ICLR 2019*. https://arxiv.org/abs/1811.01241

[16] Zhang, S., et al. (2020). "DialoGPT: Large-Scale Generative Pre-training for Conversational Response Generation." *ACL 2020*. https://arxiv.org/abs/1911.00536

[17] Chevalier, A., et al. (2023). "Adapting Language Models to Compress Contexts." *EMNLP 2023*. https://arxiv.org/abs/2305.14788

[18] Gekhman, Z., et al. (2023). "Does Fine-Tuning LLMs on New Knowledge Encourage Hallucinations?" *arXiv*. https://arxiv.org/abs/2405.05904

[19] Wang, L., et al. (2023). "Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection." *arXiv*. https://arxiv.org/abs/2310.11511

[20] Khattab, O., et al. (2021). "Baleen: Robust Multi-Hop Reasoning at Scale via Condensed Retrieval." *NeurIPS 2021*. https://arxiv.org/abs/2101.00436

[21] Liu, N. F., Lin, K., Hewitt, J., Paranjape, A., Bevilacqua, M., Petroni, F., & Liang, P. (2023). "Lost in the Middle: How Language Models Use Long Contexts." *Transactions of the Association for Computational Linguistics (TACL)*. https://arxiv.org/abs/2307.03172

[22] Xiao, G., Tian, Y., Chen, B., Han, S., & Lewis, M. (2024). "Efficient Streaming Language Models with Attention Sinks." *ICLR 2024*. https://arxiv.org/abs/2309.17453

[23] Li, T., Zhang, G., Do, Q. D., Yue, X., & Chen, W. (2024). "Long-context LLMs Struggle with Long In-context Learning." *arXiv*. https://arxiv.org/abs/2404.02060

[24] Packer, C., Wooders, S., Lin, K., Fang, V., Patil, S. G., Stoica, I., & Gonzalez, J. E. (2023). "MemGPT: Towards LLMs as Operating Systems." *arXiv*. https://arxiv.org/abs/2310.08560
