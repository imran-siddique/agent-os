# New Features: From Engineering to Science

This document describes the three major features added to transform CMVK from an engineering prototype to a research-ready system.

## Feature 1: The Visualizer Tool 🎭

### Overview
The visualizer replays JSON traces as human-readable adversarial debates, making it easy to understand how the Builder (GPT-4o) and Prosecutor (Gemini) interact.

### Usage

```bash
# Replay a specific trace
python -m src.tools.visualizer logs/traces/cmvk_prob_001_*.json

# Replay the latest trace
python -m src.tools.visualizer --latest

# List all available traces
python -m src.tools.visualizer --list

# Control playback speed (0 = instant, 1 = 1 second per message)
python -m src.tools.visualizer --latest --speed 0.5

# Hide code blocks
python -m src.tools.visualizer --latest --no-code
```

### Output Example

```
>>> GPT-4o (The Builder): I'll solve this using Built In Sort...
    [Generated Code]

>>> Gemini (The Prosecutor): OBJECTION! The solution violates 
    the constraint 'WITHOUT using sorted()'.

>>> Kernel (The Arbiter): ⚖️ Objection Sustained. Solution REJECTED.
>>> Kernel (The Arbiter): 🚫 Strategy 'Built In Sort' is now BANNED.
```

### Features
- Color-coded output for different speakers
- Step-by-step replay of the verification loop
- Shows strategy bans in real-time
- Displays final statistics and results

---

## Feature 2: HumanEval Dataset Loader 📊

### Overview
The HumanEval loader provides seamless integration with the industry-standard benchmark for code generation models.

### Basic Usage

```python
from src.datasets.humaneval_loader import HumanEvalLoader

# Load the sample dataset (5 problems)
loader = HumanEvalLoader()

# Get all problems
problems = loader.get_all_problems()

# Get a specific problem
problem = loader.get_problem("HumanEval/0")

# Format for kernel
formatted = loader.format_for_kernel(problem)

# Get a subset
subset = loader.format_all_for_kernel(start=0, count=10)
```

### Command Line Usage

```bash
# Run the demo
python -m src.datasets.humaneval_loader

# Get statistics
python -c "from src.datasets.humaneval_loader import HumanEvalLoader; loader = HumanEvalLoader(); print(f'{len(loader)} problems loaded')"
```

### Dataset Format

The loader converts HumanEval problems to the format expected by the kernel:

```python
{
    'id': 'HumanEval_0',  # Filesystem-safe ID
    'query': 'Complete the following Python function:\n\n...',
    'metadata': {
        'task_id': 'HumanEval/0',
        'entry_point': 'has_close_elements',
        'test_code': 'def check(candidate): ...',
        'original_prompt': 'from typing import List...'
    }
}
```

### Downloading the Full Dataset

The sample dataset contains 5 problems. To download all 164 problems:

```python
from src.datasets.humaneval_loader import download_full_humaneval
download_full_humaneval('experiments/datasets/humaneval_full.json')
```

---

## Feature 3: Enhanced Paper Data Generator 📈

### Overview
The paper data generator now supports scalable experiments with HumanEval, allowing you to go from 2 problems to 50+ for statistical significance.

### Usage

```bash
# Legacy mode (original 2 problems)
python experiments/paper_data_generator.py --legacy

# Small scale (5 problems)
python experiments/paper_data_generator.py --humaneval --count 5

# Medium scale (50 problems - recommended for papers)
python experiments/paper_data_generator.py --humaneval --count 50

# Full dataset (all available problems)
python experiments/paper_data_generator.py --humaneval

# Custom range
python experiments/paper_data_generator.py --humaneval --start 10 --count 20

# Custom dataset path
python experiments/paper_data_generator.py --humaneval --dataset-path /path/to/dataset.json
```

### Output

The generator produces:
- **Baseline solutions:** `logs/baseline_*.py` - Single GPT-4o generations
- **CMVK traces:** `logs/traces/cmvk_*.json` - Full adversarial verification logs

### Workflow

1. **Run experiments** at increasing scale
2. **Visualize traces** to understand system behavior
3. **Analyze results** for statistical significance
4. **Scale up** to 50+ problems for publication

---

## Feature 4: PAPER.md Research Draft 📄

### Overview
A complete research paper structure documenting the CMVK methodology and experimental design.

### Sections

1. **Abstract** - Overview and key results
2. **Introduction** - The "grading your own homework" problem
3. **Methodology** - Adversarial architecture
4. **Experiments** - HumanEval benchmark setup
5. **Tools** - Reproducibility (visualizer, loader)
6. **Discussion** - Why multi-model verification works
7. **Related Work** - Self-correction, multi-agent systems
8. **Conclusion** - Key insights

### Structure for Results

The paper includes placeholders for:
- Pass rate tables (Baseline vs CMVK)
- Attempt efficiency metrics
- Strategy diversity analysis
- Blind spot detection examples

### How to Use

1. Read `PAPER.md` to understand the research narrative
2. Run experiments to fill in Section 3.3 (Results)
3. Add system prompts to Appendix A
4. Include example traces in Appendix B
5. Perform statistical analysis for Appendix C

---

## Complete Workflow Example

### Step 1: Load Data
```python
from src.datasets.humaneval_loader import HumanEvalLoader
loader = HumanEvalLoader()
problems = loader.format_all_for_kernel(start=0, count=5)
```

### Step 2: Run Experiments
```bash
python experiments/paper_data_generator.py --humaneval --count 5
```

### Step 3: Visualize Results
```bash
python -m src.tools.visualizer --latest
```

### Step 4: Analyze Traces
```python
import json
import glob

# Find the latest trace file for HumanEval_0
trace_files = glob.glob('logs/traces/cmvk_HumanEval_0_*.json')
if trace_files:
    latest_trace = max(trace_files, key=os.path.getmtime)
    with open(latest_trace) as f:
        trace = json.load(f)
        
    print(f"Attempts: {trace['meta']['total_attempts']}")
    print(f"Status: {trace['meta']['final_status']}")
    print(f"Banned strategies: {trace['forbidden_strategies']}")
```

### Step 5: Scale Up
```bash
# Once you validate the approach works on 5 problems
python experiments/paper_data_generator.py --humaneval --count 50
```

---

## Testing

All features include comprehensive tests:

```bash
# Test the visualizer
python tests/test_visualizer.py

# Test the HumanEval loader
python tests/test_humaneval_loader.py

# Test trace logging
python tests/test_trace_logger.py

# Run all tests
python -m pytest tests/
```

---

## Quick Demo

Run the complete pipeline demo:

```bash
python demo_complete_pipeline.py
```

This demonstrates:
1. HumanEval data loading
2. Trace generation
3. Visualization
4. Scaling experiments
5. Paper structure

---

## Next Steps

### For Research
1. Set up API keys for OpenAI and Gemini
2. Run pilot experiments (n=5)
3. Validate traces with visualizer
4. Scale to 50+ problems
5. Fill in PAPER.md results section

### For Development
1. Add more datasets beyond HumanEval
2. Implement learned strategy detection
3. Add multi-verifier ensemble
4. Create web-based visualizer

---

## Citation

If you use these tools in your research, please cite:

```bibtex
@misc{cmvk2026,
  title={Cross-Model Verification Kernel: Adversarial Multi-Model Code Generation},
  author={[Authors]},
  year={2026},
  howpublished={\\url{https://github.com/imran-siddique/cross-model-verification-kernel}}
}
```

---

## Support

For questions or issues:
- GitHub Issues: https://github.com/imran-siddique/cross-model-verification-kernel/issues
- Documentation: See README.md and PAPER.md
- Examples: See demo_complete_pipeline.py
