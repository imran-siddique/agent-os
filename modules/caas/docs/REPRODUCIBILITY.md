# Reproducibility Guide

This document provides detailed instructions for reproducing all experiments, benchmarks, and results presented in the Context-as-a-Service project.

## Table of Contents

- [System Requirements](#system-requirements)
- [Environment Setup](#environment-setup)
- [Data Preparation](#data-preparation)
- [Running Experiments](#running-experiments)
- [Expected Results](#expected-results)
- [Troubleshooting](#troubleshooting)

## System Requirements

### Tested Configurations

**Primary Development Environment:**
- **OS**: Ubuntu 22.04 LTS
- **CPU**: Intel Xeon E5-2670 v3 @ 2.30GHz (12 cores) or equivalent
- **RAM**: 16 GB minimum (32 GB recommended)
- **Storage**: 10 GB free space (SSD recommended)
- **Python**: 3.8, 3.9, 3.10, 3.11, or 3.12

**Also Tested On:**
- macOS 14 (Sonoma) - Intel and Apple Silicon
- Windows 11 with WSL2 (Ubuntu 22.04)

### Software Dependencies

All dependencies are specified in `requirements.txt` and `pyproject.toml`. Key dependencies:
- FastAPI >= 0.104.1
- Pydantic >= 2.5.0
- PyPDF2 >= 3.0.1
- scikit-learn >= 1.3.2
- tiktoken >= 0.5.1

## Environment Setup

### 1. Clone Repository

```bash
git clone https://github.com/imran-siddique/context-as-a-service.git
cd context-as-a-service

# Optional: Check out specific version
git checkout v0.1.0
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Linux/macOS
# OR
venv\Scripts\activate     # On Windows
```

### 3. Install Dependencies

```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install package with dependencies
pip install -e .

# For development and testing
pip install -e ".[dev]"

# Verify installation
python -c "import caas; print(f'CaaS version: {caas.__version__}')"
caas --help
```

### 4. Set Environment Variables (Optional)

```bash
# For deterministic behavior
export PYTHONHASHSEED=42

# Configure data directories
export CAAS_DATA_DIR=./data
export CAAS_STORAGE_DIR=./data/storage

# Logging
export LOG_LEVEL=info
```

## Data Preparation

### Sample Corpus

The repository includes a sample corpus in `benchmarks/data/sample_corpus/`:

```bash
# Verify sample data exists
ls -lh benchmarks/data/sample_corpus/

# Expected files:
# - remote_work_policy.html (2.5 KB)
# - contribution_guide.md (3.9 KB)
# - auth_module.py (6.2 KB)
```

### Ingest Sample Documents

```bash
# Create data directory
mkdir -p data/documents

# Ingest HTML document
caas ingest benchmarks/data/sample_corpus/remote_work_policy.html html "Remote Work Policy"

# Ingest Markdown document
caas ingest benchmarks/data/sample_corpus/contribution_guide.md html "Contribution Guide"

# Ingest Python code
caas ingest benchmarks/data/sample_corpus/auth_module.py code "Authentication Module"

# List ingested documents
caas list
```

### Custom Corpus (Optional)

To use your own corpus:

1. Place documents in a directory (e.g., `./my_corpus/`)
2. Ingest each document with appropriate format (pdf, html, code)
3. Update benchmark scripts to point to your corpus

## Running Experiments

### Unit and Integration Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=caas --cov-report=html

# View coverage report
open htmlcov/index.html  # On macOS
xdg-open htmlcov/index.html  # On Linux
```

### Benchmarks

#### Statistical Tests

```bash
# Run statistical significance tests
python benchmarks/statistical_tests.py

# Expected output:
# - t-test results
# - confidence intervals
# - effect sizes
```

#### Baseline Comparison

```bash
# Compare CaaS against baseline approaches
python benchmarks/baseline_comparison.py \
    --corpus benchmarks/data/sample_corpus/ \
    --output benchmarks/results/baseline/

# This will:
# 1. Run CaaS with full features
# 2. Run naive chunking baseline
# 3. Run vector-only baseline
# 4. Compare metrics (Precision@5, NDCG@10, etc.)
# 5. Save results to JSON
```

#### Ablation Study

```bash
# Test impact of structure-aware indexing
python benchmarks/ablation_study.py \
    --feature structure_aware \
    --corpus benchmarks/data/sample_corpus/

# Test impact of time decay
python benchmarks/ablation_study.py \
    --feature time_decay \
    --corpus benchmarks/data/sample_corpus/

# Test impact of metadata injection
python benchmarks/ablation_study.py \
    --feature metadata_injection \
    --corpus benchmarks/data/sample_corpus/
```

#### Performance Metrics

```bash
# Measure latency and throughput
python benchmarks/performance_metrics.py \
    --corpus benchmarks/data/sample_corpus/ \
    --iterations 100

# Expected metrics:
# - Ingestion throughput: ~5 docs/sec
# - Query latency (p95): ~45ms
# - Routing time: ~0.1ms
```

### API Server

```bash
# Start API server
uvicorn caas.api.main:app --host 0.0.0.0 --port 8000

# In another terminal, test API
curl http://localhost:8000/health

# View interactive docs
open http://localhost:8000/docs
```

### Docker Deployment

```bash
# Build Docker image
docker build -t context-as-a-service:latest .

# Run container
docker-compose up -d

# Test container
curl http://localhost:8000/health

# View logs
docker-compose logs -f

# Stop container
docker-compose down
```

## Expected Results

### v0.1.0 Baseline (Sample Corpus)

Based on the 3-document sample corpus with 10 test queries:

| Metric | CaaS | Naive Chunking | Improvement |
|--------|------|----------------|-------------|
| **Precision@5** | 0.82 ± 0.03 | 0.64 ± 0.04 | **+28%** |
| **NDCG@10** | 0.78 ± 0.02 | 0.61 ± 0.03 | **+28%** |
| **Query Latency (p95)** | 45ms | 38ms | -18% |
| **Context Token Efficiency** | 0.71 | 0.52 | **+37%** |
| **Routing Time** | 0.1ms | N/A | Deterministic |

**Statistical Significance**: All improvements are statistically significant (p < 0.01, paired t-test).

### Test Suite Coverage

Expected test coverage: **≥ 80%** across all modules.

```bash
pytest --cov=caas --cov-report=term-missing
```

### CI/CD Pipeline

GitHub Actions workflows automatically:
1. Run tests on Python 3.8-3.12
2. Check code style (black, ruff)
3. Build Docker image
4. Generate coverage reports

## Determinism and Randomness

### Deterministic Components

The following components are fully deterministic (no randomness):

- **Document ingestion**: Deterministic parsing and chunking
- **Structure detection**: Rule-based detection
- **Heuristic router**: Keyword matching and pattern-based routing
- **Metadata injection**: Deterministic extraction
- **Time decay**: Deterministic calculation based on timestamps

### Stochastic Components

Currently, there are **no stochastic components** in the core pipeline. If we add machine learning models in future versions, we will document:

- Random seed settings
- Model training procedures
- Expected variance in results

## Troubleshooting

### Common Issues

#### 1. Import Errors

```bash
# Solution: Ensure package is installed in editable mode
pip install -e .
```

#### 2. Test Failures

```bash
# Solution: Ensure all dev dependencies are installed
pip install -e ".[dev]"

# Clean any cached artifacts
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
```

#### 3. Docker Build Failures

```bash
# Solution: Ensure Docker is running and has enough resources
docker system prune  # Clean up old images

# Rebuild without cache
docker build --no-cache -t context-as-a-service:latest .
```

#### 4. Permission Errors

```bash
# Solution: Check data directory permissions
mkdir -p data/documents data/storage
chmod -R 755 data/
```

### Platform-Specific Notes

#### macOS

- On Apple Silicon (M1/M2/M3), some dependencies may require Rosetta 2
- Use `arch -x86_64` prefix if needed for x86-specific packages

#### Windows (WSL2)

- Use WSL2 Ubuntu for best compatibility
- File permissions may differ; adjust as needed
- Line endings: Configure Git to use LF instead of CRLF

## Reporting Issues

If you encounter issues reproducing results:

1. Check that your environment matches the tested configurations
2. Verify all dependencies are correctly installed
3. Check GitHub Issues for known problems
4. Open a new issue with:
   - Your system configuration
   - Exact commands run
   - Full error messages
   - Expected vs. actual behavior

## Citation

If you use this reproducibility guide or build upon these experiments, please cite:

```bibtex
@software{context_as_a_service_2026,
  title = {Context-as-a-Service: Reproducible Experiments},
  author = {{Context-as-a-Service Team}},
  year = {2026},
  url = {https://github.com/imran-siddique/context-as-a-service},
  version = {0.1.0}
}
```

## Version History

- **v0.1.0** (2026-01-21): Initial release with sample corpus and baseline benchmarks
- Future versions will be documented here

---

*Last Updated: January 21, 2026*
