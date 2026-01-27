# Sample Corpus for Benchmarks

This directory contains sample documents for testing and benchmarking Context-as-a-Service.

## Files

1. **remote_work_policy.html** - Company policy document (HTML format)
   - Tests: HTML parsing, policy extraction, time-based content (updated Jan 2026)
   - Use cases: HR documentation, policy retrieval

2. **contribution_guide.md** - Development contribution guidelines (Markdown format)
   - Tests: Code block extraction, technical documentation, structured content
   - Use cases: Developer onboarding, code contribution workflows

3. **auth_module.py** - Python authentication module (Code format)
   - Tests: Code structure detection, docstring extraction, class/function indexing
   - Use cases: Code search, API documentation generation

## Usage

### Ingest Documents

```bash
# Ingest all sample documents
for file in benchmarks/data/sample_corpus/*; do
    ext="${file##*.}"
    case $ext in
        html) format="html" ;;
        md) format="html" ;;  # Markdown treated as HTML
        py) format="code" ;;
        *) format="code" ;;
    esac
    caas ingest "$file" "$format" "$(basename $file)"
done
```

### Run Benchmark Tests

```bash
# Run statistical tests on sample corpus
python benchmarks/statistical_tests.py --corpus benchmarks/data/sample_corpus/

# Compare against baseline
python benchmarks/baseline_comparison.py --corpus benchmarks/data/sample_corpus/
```

## Characteristics

| File | Format | Size | Sections | Metadata |
|------|--------|------|----------|----------|
| remote_work_policy.html | HTML | 2.5 KB | 8 | Updated: Jan 2026 |
| contribution_guide.md | Markdown | 3.9 KB | 7 | Technical docs |
| auth_module.py | Python | 6.2 KB | 2 classes, 8 methods | Code documentation |

## Test Queries

Sample queries to test against this corpus:

1. "What are the remote work eligibility requirements?"
2. "How do I set up my development environment?"
3. "How does the authentication token validation work?"
4. "What is the minimum internet speed for remote work?"
5. "What is the PR review process?"

## Expected Results

These documents are designed to test:

- **Structure-Aware Indexing**: HTML headers vs. code classes vs. markdown sections
- **Time Decay**: Remote policy updated in 2026 (recent) vs. contribution guide (no timestamp)
- **Metadata Injection**: File type detection, section hierarchy
- **Context Triad**: Policy (Hot), Dev guide (Warm), Code (Cold) for different query types
- **Pragmatic Truth**: Official policy vs. actual practice (if Slack logs were added)

## Extending the Corpus

To add more sample documents:

1. Create files in appropriate formats (HTML, MD, PY, PDF, etc.)
2. Update this README with file characteristics
3. Add corresponding test queries
4. Run benchmarks to validate impact

## License

These sample documents are provided for testing purposes only and are released under the MIT License.
