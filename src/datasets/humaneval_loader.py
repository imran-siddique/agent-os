"""
HumanEval Dataset Loader

This module provides utilities for loading and processing the HumanEval dataset,
the industry standard benchmark for code generation models.

The HumanEval dataset contains 164 hand-written programming problems with function
signatures, docstrings, and unit tests. It's widely used to evaluate code generation
capabilities of language models.

Reference: "Evaluating Large Language Models Trained on Code" (Chen et al., 2021)
"""
import json
import os
from typing import List, Dict, Any, Optional
from pathlib import Path


class HumanEvalLoader:
    """
    Loader for the HumanEval dataset.
    
    This class handles loading and formatting HumanEval problems for use
    with the Cross-Model Verification Kernel.
    """
    
    def __init__(self, dataset_path: Optional[str] = None):
        """
        Initialize the HumanEval loader.
        
        Args:
            dataset_path: Path to the HumanEval JSON file. If None, uses the
                         sample dataset in experiments/datasets/humaneval_sample.json
        """
        if dataset_path is None:
            # Use default sample dataset
            base_dir = Path(__file__).parent.parent.parent
            dataset_path = base_dir / "experiments" / "datasets" / "humaneval_sample.json"
        
        self.dataset_path = Path(dataset_path)
        self.problems = []
        self._load_dataset()
    
    def _load_dataset(self):
        """Load the dataset from JSON file."""
        if not self.dataset_path.exists():
            raise FileNotFoundError(
                f"HumanEval dataset not found at {self.dataset_path}. "
                "Please provide a valid path or ensure the sample dataset exists."
            )
        
        with open(self.dataset_path, 'r', encoding='utf-8') as f:
            self.problems = json.load(f)
        
        print(f"✅ Loaded {len(self.problems)} problems from HumanEval dataset")
    
    def get_all_problems(self) -> List[Dict[str, Any]]:
        """
        Get all problems from the dataset.
        
        Returns:
            List of problem dictionaries
        """
        return self.problems
    
    def get_problem(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific problem by task ID.
        
        Args:
            task_id: The task ID (e.g., "HumanEval/0")
            
        Returns:
            Problem dictionary or None if not found
        """
        for problem in self.problems:
            if problem.get('task_id') == task_id:
                return problem
        return None
    
    def get_problem_by_index(self, index: int) -> Optional[Dict[str, Any]]:
        """
        Get a problem by its index in the dataset.
        
        Args:
            index: Zero-based index
            
        Returns:
            Problem dictionary or None if index out of range
        """
        if 0 <= index < len(self.problems):
            return self.problems[index]
        return None
    
    def format_for_kernel(self, problem: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format a HumanEval problem for use with the Verification Kernel.
        
        The kernel expects problems in a specific format with 'id' and 'query' keys.
        
        Args:
            problem: Raw HumanEval problem dictionary
            
        Returns:
            Formatted problem dictionary with 'id', 'query', and metadata
        """
        task_id = problem.get('task_id', 'unknown')
        prompt = problem.get('prompt', '')
        test = problem.get('test', '')
        entry_point = problem.get('entry_point', '')
        
        # Create a detailed query that includes the function signature and docstring
        query = (
            f"Complete the following Python function:\n\n"
            f"{prompt}\n\n"
            f"Requirements:\n"
            f"- The function must pass all provided test cases\n"
            f"- Follow the exact function signature provided\n"
            f"- Entry point: {entry_point}"
        )
        
        return {
            'id': task_id.replace('/', '_'),  # Make filesystem-safe
            'query': query,
            'metadata': {
                'task_id': task_id,
                'entry_point': entry_point,
                'test_code': test,
                'original_prompt': prompt
            }
        }
    
    def get_problem_subset(self, start: int = 0, count: int = 10) -> List[Dict[str, Any]]:
        """
        Get a subset of problems from the dataset.
        
        This is useful for running experiments on a smaller scale before
        scaling up to the full dataset.
        
        Args:
            start: Starting index (default: 0)
            count: Number of problems to return (default: 10)
            
        Returns:
            List of problem dictionaries
        """
        end = min(start + count, len(self.problems))
        return self.problems[start:end]
    
    def format_all_for_kernel(self, start: int = 0, count: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Format multiple problems for the kernel.
        
        Args:
            start: Starting index (default: 0)
            count: Number of problems to format (default: all remaining)
            
        Returns:
            List of formatted problem dictionaries
        """
        if count is None:
            count = len(self.problems) - start
        
        subset = self.get_problem_subset(start, count)
        return [self.format_for_kernel(p) for p in subset]
    
    def __len__(self) -> int:
        """Return the number of problems in the dataset."""
        return len(self.problems)
    
    def __iter__(self):
        """Iterate over all problems."""
        return iter(self.problems)


def download_full_humaneval(output_path: str = "experiments/datasets/humaneval_full.jsonl"):
    """
    Download the full HumanEval dataset from the official source.
    
    Note: This requires internet access and the 'requests' library.
    The full dataset is available at:
    https://github.com/openai/human-eval
    
    Args:
        output_path: Where to save the downloaded dataset
    """
    try:
        import requests
    except ImportError:
        print("❌ Error: 'requests' library is required to download the dataset.")
        print("Install it with: pip install requests")
        return None
    
    url = "https://github.com/openai/human-eval/raw/master/data/HumanEval.jsonl.gz"
    
    print(f"Downloading HumanEval dataset from {url}...")
    
    try:
        import gzip
        
        response = requests.get(url)
        response.raise_for_status()
        
        # Decompress and save
        import io
        compressed_file = io.BytesIO(response.content)
        
        problems = []
        with gzip.open(compressed_file, 'rt', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    problems.append(json.loads(line))
        
        # Save as regular JSON for easier handling
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path.with_suffix('.json'), 'w', encoding='utf-8') as f:
            json.dump(problems, f, indent=2)
        
        print(f"✅ Downloaded {len(problems)} problems to {output_path.with_suffix('.json')}")
        return str(output_path.with_suffix('.json'))
        
    except Exception as e:
        print(f"❌ Failed to download HumanEval dataset: {e}")
        print("You can manually download it from: https://github.com/openai/human-eval")
        return None


if __name__ == "__main__":
    # Example usage
    print("="*80)
    print("HumanEval Dataset Loader - Demo")
    print("="*80)
    
    # Load the sample dataset
    loader = HumanEvalLoader()
    
    print(f"\n📊 Dataset Statistics:")
    print(f"   Total problems: {len(loader)}")
    
    # Get first problem
    print(f"\n📝 Example Problem:")
    problem = loader.get_problem_by_index(0)
    if problem:
        print(f"   Task ID: {problem['task_id']}")
        print(f"   Entry Point: {problem['entry_point']}")
        print(f"   Prompt Preview: {problem['prompt'][:100]}...")
    
    # Format for kernel
    print(f"\n🔧 Formatted for Kernel:")
    formatted = loader.format_for_kernel(problem)
    print(f"   ID: {formatted['id']}")
    print(f"   Query (first 150 chars): {formatted['query'][:150]}...")
    
    # Get a subset
    print(f"\n📦 Getting subset (5 problems):")
    subset = loader.format_all_for_kernel(start=0, count=5)
    for i, p in enumerate(subset, 1):
        print(f"   {i}. {p['id']}")
    
    print("\n" + "="*80)
    print("To download the full HumanEval dataset:")
    print("  python -c 'from src.datasets.humaneval_loader import download_full_humaneval; download_full_humaneval()'")
    print("="*80)
