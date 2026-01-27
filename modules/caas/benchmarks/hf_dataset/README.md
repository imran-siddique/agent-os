---
annotations_creators:
- expert-generated
language:
- en
language_creators:
- expert-generated
license:
- mit
multilinguality:
- monolingual
pretty_name: CaaS Benchmark Corpus
size_categories:
- n<1K
source_datasets:
- original
tags:
- context-extraction
- rag
- document-processing
- enterprise-ai
- benchmarking
task_categories:
- text-retrieval
- question-answering
task_ids:
- document-retrieval
---

# CaaS Benchmark Corpus v1

A diverse collection of synthetic enterprise documents for benchmarking context extraction and RAG systems.

## Dataset Description

This dataset contains **16 representative enterprise documents** spanning multiple formats and domains, designed to evaluate:

- **Structure-aware indexing** - Can the system identify high-value vs. low-value content?
- **Time decay relevance** - Does the system properly weight recent vs. old information?
- **Pragmatic truth detection** - Can the system identify conflicts between official and informal sources?
- **Cross-document reasoning** - Can the system synthesize information across documents?

### Supported Tasks

- Document retrieval and ranking
- Question answering over enterprise documents
- Context extraction for LLM augmentation
- Information extraction benchmarking

### Languages

English (en)

## Dataset Structure

### Data Files

| File | Type | Domain | Description |
|------|------|--------|-------------|
| `auth_module.py` | Python | Engineering | Authentication module with security features |
| `data_processor.py` | Python | Engineering | Data processing pipeline with validation |
| `api_reference.md` | Markdown | Documentation | REST API reference with examples |
| `contribution_guide.md` | Markdown | Documentation | Developer contribution guidelines |
| `troubleshooting_guide.md` | Markdown | Documentation | Common issues and solutions |
| `employee_handbook.md` | Markdown | HR/Policy | Employee policies and benefits |
| `privacy_policy.md` | Markdown | Legal | Data privacy and compliance |
| `software_license_agreement.md` | Markdown | Legal | Software licensing terms |
| `incident_report.md` | Markdown | Security | Security incident documentation |
| `meeting_notes.md` | Markdown | Business | Engineering team meeting notes |
| `onboarding_checklist.md` | Markdown | HR | New employee onboarding tasks |
| `release_notes.md` | Markdown | Engineering | Software release documentation |
| `config_example.yaml` | YAML | Engineering | Configuration file example |
| `database_schema.sql` | SQL | Engineering | Database schema definitions |
| `remote_work_policy.html` | HTML | HR/Policy | Remote work guidelines |
| `README.md` | Markdown | Documentation | Sample corpus overview |

### Document Characteristics

| Characteristic | Range |
|---------------|-------|
| Document length | 50 - 500 lines |
| Token count | 500 - 5,000 tokens |
| Formats | Python, Markdown, HTML, SQL, YAML |
| Domains | Engineering, Legal, HR, Security, Business |

### Data Fields

Each document contains:

- **Content**: The full text of the document
- **Filename**: Original filename with extension
- **File type**: Document format (py, md, html, sql, yaml)
- **Domain**: Business domain classification
- **Structure**: Hierarchical sections (where applicable)
- **Timestamps**: Simulated creation/update dates

## Dataset Creation

### Curation Rationale

Enterprise AI systems must handle diverse document types with varying structures, importance levels, and freshness requirements. This corpus was designed to:

1. **Represent real enterprise diversity** - Mix of technical, legal, HR, and operational documents
2. **Include temporal signals** - Documents have explicit dates for time-decay testing
3. **Provide ground truth** - Known structure and content for evaluation
4. **Enable ablation studies** - Test individual CaaS features in isolation

### Source Data

All documents are **synthetic**, created specifically for this benchmark. They are realistic representations of enterprise documents but contain no real company data, PII, or copyrighted content.

### Annotations

Documents include:

- **Section hierarchy** - Explicit heading structure
- **Content classification** - Domain and document type labels
- **Temporal metadata** - Creation and update timestamps
- **Cross-references** - Links between related documents (e.g., incident report references meeting notes)

## Considerations for Using the Data

### Social Impact

This dataset is designed for benchmarking AI systems. The synthetic documents represent common enterprise scenarios but do not reflect any real organization's data.

### Biases

- Documents reflect Western/US business practices
- English language only
- Tech company context (software, SaaS)

### Limitations

- Small corpus size (16 documents)
- Limited to text content (no images, tables as images)
- Synthetic content may not capture all real-world complexity

## Additional Information

### Dataset Curators

Context-as-a-Service Team

### Licensing Information

MIT License

### Citation Information

```bibtex
@dataset{caas_benchmark_corpus_2026,
  author = {Context-as-a-Service Team},
  title = {CaaS Benchmark Corpus: A Diverse Enterprise Document Collection for RAG Evaluation},
  year = {2026},
  publisher = {Hugging Face},
  url = {https://huggingface.co/datasets/mosiddi/caas-benchmark-corpus-v1}
}
```

### Contributions

To contribute additional documents or improvements:

1. Fork the [CaaS repository](https://github.com/imran-siddique/context-as-a-service)
2. Add documents to `benchmarks/data/sample_corpus/`
3. Submit a pull request

## Usage

### Loading the Dataset

```python
from datasets import load_dataset

# Load from Hugging Face
dataset = load_dataset("mosiddi/caas-benchmark-corpus-v1")

# Or load locally
from pathlib import Path
corpus_path = Path("benchmarks/data/sample_corpus")
documents = list(corpus_path.glob("*"))
```

### Running Benchmarks

```bash
# Clone the CaaS repository
git clone https://github.com/imran-siddique/context-as-a-service.git
cd context-as-a-service

# Install dependencies
pip install -e ".[dev]"

# Run benchmarks
python benchmarks/run_evaluation.py --corpus benchmarks/data/sample_corpus/
```

### Example: Evaluate Structure-Aware Indexing

```python
from caas import DocumentProcessor
from benchmarks.metrics import evaluate_structure_detection

processor = DocumentProcessor()
results = []

for doc_path in corpus_path.glob("*.md"):
    doc = processor.process(doc_path)
    accuracy = evaluate_structure_detection(doc, ground_truth[doc_path.name])
    results.append(accuracy)

print(f"Structure detection accuracy: {sum(results)/len(results):.2%}")
```
