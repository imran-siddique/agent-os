"""
HuggingFace Hub Integration for CMVK

Upload datasets, experiment results, and execution traces to HuggingFace Hub
for reproducibility and community sharing.

Usage:
    python -m src.tools.huggingface_upload --dataset humaneval_50
    python -m src.tools.huggingface_upload --traces
    python -m src.tools.huggingface_upload --results
"""
import os
import json
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

# HuggingFace dataset repository configuration
DEFAULT_REPO_ID = "imran-siddique/cmvk-benchmark-data"
DEFAULT_REPO_TYPE = "dataset"


def check_huggingface_auth() -> bool:
    """Check if HuggingFace authentication is configured."""
    try:
        from huggingface_hub import HfApi
        api = HfApi()
        # Try to get user info - will fail if not authenticated
        api.whoami()
        return True
    except Exception as e:
        logger.warning(f"HuggingFace authentication not configured: {e}")
        return False


def upload_dataset(
    dataset_name: str,
    repo_id: str = DEFAULT_REPO_ID,
    private: bool = False
) -> str:
    """
    Upload a dataset file to HuggingFace Hub.
    
    Args:
        dataset_name: Name of the dataset (e.g., 'humaneval_50', 'sabotage')
        repo_id: HuggingFace repository ID
        private: Whether to make the upload private
        
    Returns:
        URL of the uploaded file
    """
    from huggingface_hub import HfApi, create_repo
    
    # Find the dataset file
    dataset_path = Path(f"experiments/datasets/{dataset_name}.json")
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")
    
    api = HfApi()
    
    # Create repo if it doesn't exist
    try:
        create_repo(repo_id, repo_type="dataset", private=private, exist_ok=True)
    except Exception as e:
        logger.info(f"Repository exists or creation skipped: {e}")
    
    # Upload the file
    url = api.upload_file(
        path_or_fileobj=str(dataset_path),
        path_in_repo=f"datasets/{dataset_name}.json",
        repo_id=repo_id,
        repo_type="dataset",
        commit_message=f"Upload {dataset_name} dataset"
    )
    
    logger.info(f"Uploaded {dataset_name} to {url}")
    return url


def upload_traces(
    trace_dir: str = "logs/traces",
    repo_id: str = DEFAULT_REPO_ID,
    max_files: int = 100
) -> List[str]:
    """
    Upload execution traces to HuggingFace Hub.
    
    Args:
        trace_dir: Directory containing trace JSON files
        repo_id: HuggingFace repository ID
        max_files: Maximum number of trace files to upload
        
    Returns:
        List of uploaded file URLs
    """
    from huggingface_hub import HfApi, create_repo
    
    trace_path = Path(trace_dir)
    if not trace_path.exists():
        raise FileNotFoundError(f"Trace directory not found: {trace_path}")
    
    trace_files = list(trace_path.glob("*.json"))[:max_files]
    if not trace_files:
        logger.warning("No trace files found")
        return []
    
    api = HfApi()
    
    # Create repo if it doesn't exist
    try:
        create_repo(repo_id, repo_type="dataset", exist_ok=True)
    except Exception:
        pass
    
    urls = []
    for trace_file in trace_files:
        try:
            url = api.upload_file(
                path_or_fileobj=str(trace_file),
                path_in_repo=f"traces/{trace_file.name}",
                repo_id=repo_id,
                repo_type="dataset",
                commit_message=f"Upload trace {trace_file.name}"
            )
            urls.append(url)
            logger.info(f"Uploaded {trace_file.name}")
        except Exception as e:
            logger.error(f"Failed to upload {trace_file.name}: {e}")
    
    return urls


def upload_experiment_results(
    results_dir: str = "experiments/results",
    repo_id: str = DEFAULT_REPO_ID
) -> List[str]:
    """
    Upload experiment results to HuggingFace Hub.
    
    Args:
        results_dir: Directory containing result JSON files
        repo_id: HuggingFace repository ID
        
    Returns:
        List of uploaded file URLs
    """
    from huggingface_hub import HfApi, create_repo
    
    results_path = Path(results_dir)
    if not results_path.exists():
        raise FileNotFoundError(f"Results directory not found: {results_path}")
    
    result_files = list(results_path.glob("*.json")) + list(results_path.glob("*.txt"))
    if not result_files:
        logger.warning("No result files found")
        return []
    
    api = HfApi()
    
    # Create repo if it doesn't exist
    try:
        create_repo(repo_id, repo_type="dataset", exist_ok=True)
    except Exception:
        pass
    
    urls = []
    for result_file in result_files:
        try:
            url = api.upload_file(
                path_or_fileobj=str(result_file),
                path_in_repo=f"results/{result_file.name}",
                repo_id=repo_id,
                repo_type="dataset",
                commit_message=f"Upload results {result_file.name}"
            )
            urls.append(url)
            logger.info(f"Uploaded {result_file.name}")
        except Exception as e:
            logger.error(f"Failed to upload {result_file.name}: {e}")
    
    return urls


def create_dataset_card(repo_id: str = DEFAULT_REPO_ID) -> str:
    """
    Create and upload a dataset card (README.md) for the HuggingFace repo.
    
    Args:
        repo_id: HuggingFace repository ID
        
    Returns:
        URL of the uploaded README
    """
    from huggingface_hub import HfApi
    
    readme_content = """---
license: mit
task_categories:
  - text-generation
  - text2text-generation
language:
  - en
tags:
  - code-generation
  - verification
  - multi-agent
  - llm-evaluation
  - adversarial
size_categories:
  - n<1K
---

# CMVK Benchmark Data

Datasets, execution traces, and experiment results for the **Cross-Model Verification Kernel (CMVK)** research project.

## Overview

CMVK is a framework for adversarial multi-model verification of AI-generated code. This repository contains:

- **Datasets**: HumanEval subsets and custom test cases
- **Traces**: Execution traces showing Generator-Verifier interactions
- **Results**: Benchmark results and ablation studies

## Datasets

| Dataset | Description | Size |
|---------|-------------|------|
| `humaneval_sample.json` | Quick test set | 5 problems |
| `humaneval_50.json` | Balanced benchmark | 50 problems |
| `humaneval_full.json` | Complete HumanEval | 164 problems |
| `sabotage.json` | Adversarial test cases | 20 problems |

## Usage

```python
from datasets import load_dataset

# Load a specific dataset
dataset = load_dataset("imran-siddique/cmvk-benchmark-data", data_files="datasets/humaneval_50.json")

# Or load traces
traces = load_dataset("imran-siddique/cmvk-benchmark-data", data_files="traces/*.json")
```

## Citation

```bibtex
@software{cmvk2024,
  author = {Siddique, Imran},
  title = {Cross-Model Verification Kernel: Adversarial Multi-Model Verification},
  year = {2024},
  url = {https://github.com/imran-siddique/cross-model-verification-kernel}
}
```

## Links

- [GitHub Repository](https://github.com/imran-siddique/cross-model-verification-kernel)
- [Research Paper](https://github.com/imran-siddique/cross-model-verification-kernel/blob/main/PAPER.md)
"""
    
    api = HfApi()
    
    # Write README to temp file and upload
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(readme_content)
        temp_path = f.name
    
    try:
        url = api.upload_file(
            path_or_fileobj=temp_path,
            path_in_repo="README.md",
            repo_id=repo_id,
            repo_type="dataset",
            commit_message="Update dataset card"
        )
        return url
    finally:
        os.unlink(temp_path)


def upload_all(repo_id: str = DEFAULT_REPO_ID, private: bool = False) -> Dict[str, Any]:
    """
    Upload all datasets, traces, and results to HuggingFace Hub.
    
    Args:
        repo_id: HuggingFace repository ID
        private: Whether to make the repository private
        
    Returns:
        Summary of uploaded files
    """
    summary = {
        "datasets": [],
        "traces": [],
        "results": [],
        "errors": []
    }
    
    # Upload datasets
    for dataset in ["humaneval_sample", "humaneval_50", "humaneval_full", "sabotage"]:
        try:
            url = upload_dataset(dataset, repo_id, private)
            summary["datasets"].append({"name": dataset, "url": url})
        except Exception as e:
            summary["errors"].append({"type": "dataset", "name": dataset, "error": str(e)})
    
    # Upload traces
    try:
        urls = upload_traces(repo_id=repo_id)
        summary["traces"] = urls
    except Exception as e:
        summary["errors"].append({"type": "traces", "error": str(e)})
    
    # Upload results
    try:
        urls = upload_experiment_results(repo_id=repo_id)
        summary["results"] = urls
    except Exception as e:
        summary["errors"].append({"type": "results", "error": str(e)})
    
    # Create dataset card
    try:
        create_dataset_card(repo_id)
    except Exception as e:
        summary["errors"].append({"type": "readme", "error": str(e)})
    
    return summary


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Upload CMVK data to HuggingFace Hub"
    )
    parser.add_argument(
        "--dataset",
        type=str,
        help="Upload a specific dataset (e.g., humaneval_50, sabotage)"
    )
    parser.add_argument(
        "--traces",
        action="store_true",
        help="Upload execution traces"
    )
    parser.add_argument(
        "--results",
        action="store_true",
        help="Upload experiment results"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Upload everything (datasets, traces, results)"
    )
    parser.add_argument(
        "--repo-id",
        type=str,
        default=DEFAULT_REPO_ID,
        help=f"HuggingFace repository ID (default: {DEFAULT_REPO_ID})"
    )
    parser.add_argument(
        "--private",
        action="store_true",
        help="Make the repository private"
    )
    parser.add_argument(
        "--check-auth",
        action="store_true",
        help="Check HuggingFace authentication status"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    
    if args.check_auth:
        if check_huggingface_auth():
            print("✓ HuggingFace authentication configured")
        else:
            print("✗ HuggingFace authentication not configured")
            print("  Run: huggingface-cli login")
        return
    
    if not check_huggingface_auth():
        print("Error: HuggingFace authentication required")
        print("Run: huggingface-cli login")
        return
    
    if args.all:
        summary = upload_all(args.repo_id, args.private)
        print("\n=== Upload Summary ===")
        print(f"Datasets: {len(summary['datasets'])} uploaded")
        print(f"Traces: {len(summary['traces'])} uploaded")
        print(f"Results: {len(summary['results'])} uploaded")
        if summary['errors']:
            print(f"Errors: {len(summary['errors'])}")
            for err in summary['errors']:
                print(f"  - {err}")
    
    elif args.dataset:
        url = upload_dataset(args.dataset, args.repo_id, args.private)
        print(f"Uploaded: {url}")
    
    elif args.traces:
        urls = upload_traces(repo_id=args.repo_id)
        print(f"Uploaded {len(urls)} trace files")
    
    elif args.results:
        urls = upload_experiment_results(repo_id=args.repo_id)
        print(f"Uploaded {len(urls)} result files")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
