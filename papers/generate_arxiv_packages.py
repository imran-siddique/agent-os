#!/usr/bin/env python3
"""
Generate arXiv submission packages for Agent OS papers.
Following https://trevorcampbell.me/html/arxiv.html guidelines.
"""

import os
import re
import shutil
import tarfile
from pathlib import Path
from datetime import datetime

PAPERS_DIR = Path(__file__).parent

# Paper configurations
PAPERS = {
    "02-cmvk": {
        "main_tex": "cmvk_neurips.tex",
        "bbl_file": "cmvk_neurips.bbl",
        "style_files": ["neurips_2024.sty"],
        "figures_dir": "figures",
        "title": "Cross-Model Verification Kernel: Adversarial Multi-Model Code Generation with Blind Spot Reduction",
        "authors": "Imran Siddique",
        "abstract": "Large Language Models exhibit systematic blind spots in code generation that persist across model families and prompt engineering techniques. We present the Cross-Model Verification Kernel (CMVK), an adversarial multi-model architecture that reduces blind spot occurrence from 23.7% to 8.2% through structured model disagreement. CMVK introduces three key innovations: (1) Blind Spot Detection via Cross-Entropy Divergence, where statistically significant output disagreement between models signals potential errors; (2) Adversarial Refinement Cycles, where models critique and improve each other's outputs; (3) Confidence-Weighted Aggregation that combines outputs based on per-model reliability scores. Evaluated on HumanEval, MBPP, and a novel BlindSpotBench dataset, CMVK achieves 91.2% pass rate compared to 76.8% for single-model baselines while reducing hallucinated API calls by 67%. The kernel integrates as a drop-in replacement for existing LLM code generation pipelines.",
        "categories": ["cs.SE", "cs.AI", "cs.LG"],
        "primary_category": "cs.SE"
    },
    "03-caas": {
        "main_tex": "latex/main.tex",
        "bbl_file": None,  # Need to generate
        "style_files": [],
        "figures_dir": "latex/figures",
        "title": "Context-as-a-Service: A Principled Architecture for Enterprise RAG Systems",
        "authors": "Imran Siddique",
        "abstract": "Enterprise Retrieval-Augmented Generation (RAG) systems suffer from context fragmentation, where relevant information is scattered across retrieval results without coherent organization. We present Context-as-a-Service (CaaS), an architecture that treats context management as a first-class system service rather than an ad-hoc retrieval step. CaaS introduces the Context Triad: Hot (immediate conversation), Warm (session-relevant retrieved chunks), and Cold (background knowledge graphs). A principled routing layer determines context placement based on recency, relevance, and retrieval cost. Evaluated on enterprise QA benchmarks, CaaS reduces hallucination rates by 34% while improving response relevance by 28% compared to standard RAG pipelines. The system handles 100K+ token contexts with sub-200ms routing latency.",
        "categories": ["cs.CL", "cs.IR", "cs.AI"],
        "primary_category": "cs.CL"
    },
    "05-control-plane": {
        "main_tex": "main.tex",
        "bbl_file": "main_arxiv.bbl" if Path(PAPERS_DIR / "05-control-plane/main_arxiv.bbl").exists() else None,
        "style_files": [],
        "figures_dir": "figures",
        "title": "Agent Control Plane: A Deterministic Kernel for Zero-Violation Governance in Agentic AI",
        "authors": "Imran Siddique",
        "abstract": "Current AI agent frameworks lack deterministic safety guarantees, relying on probabilistic prompt-based approaches that fail under adversarial conditions. We present the Agent Control Plane, a kernel architecture that provides POSIX-style governance primitives for autonomous agents. The system introduces three key abstractions: (1) Agent Signals (SIGSTOP, SIGKILL, SIGINT) for deterministic control flow; (2) Agent Virtual File System (VFS) for structured memory management; and (3) Kernel/User Space separation isolating policy enforcement from LLM execution. Evaluated against 60+ adversarial jailbreak attempts, the Control Plane achieves 0% policy violations compared to 26.67% for prompt-based baselines. The architecture enables enterprise deployment of autonomous agents in regulated industries including finance, healthcare, and energy.",
        "categories": ["cs.AI", "cs.SE", "cs.OS"],
        "primary_category": "cs.AI"
    },
    "06-scak": {
        "main_tex": "main.tex",
        "bbl_file": "main.bbl",
        "style_files": [],
        "figures_dir": "figures",
        "title": "Self-Correcting Agent Kernel: Automated Alignment via Differential Auditing and Semantic Memory Hygiene",
        "authors": "Imran Siddique",
        "abstract": "Production AI agents face a Reliability Wall defined by two invisible pathologies: laziness (premature give-ups on achievable tasks) and context rot (performance degradation due to accumulated prompt instructions). Existing architectures often exacerbate these issues by treating more context as the solution to every failure. We present the Self-Correcting Agent Kernel (SCAK), a dual-loop OODA architecture grounded in the principle of Scale by Subtraction. SCAK's Runtime Loop ensures deterministic safety, while the Alignment Loop implements Differential Auditing: a probabilistic mechanism that compares a weak agent against a stronger teacher only on give-up signals (5-10% of interactions). To combat context rot, we introduce Semantic Purge: a formal decay taxonomy where Type-A (syntax) patches are actively deleted on model upgrades, while Type-B (business) knowledge persists. Evaluations on GAIA benchmark extensions demonstrate 100% laziness detection and a 72% correction rate at 90% lower cost than full verification.",
        "categories": ["cs.AI", "cs.LG", "cs.SE"],
        "primary_category": "cs.AI"
    }
}


def remove_comments(tex_content: str) -> str:
    """Remove LaTeX comments while preserving % in URLs and escaped %."""
    lines = tex_content.split('\n')
    cleaned_lines = []
    for line in lines:
        # Find first unescaped % that's not in a URL
        result = []
        i = 0
        while i < len(line):
            if line[i] == '%':
                # Check if escaped
                if i > 0 and line[i-1] == '\\':
                    result.append('%')
                # Check if in URL (rough heuristic)
                elif 'http' in line[:i] or 'url{' in line[:i].lower():
                    result.append('%')
                else:
                    # Start of comment, stop here
                    break
            else:
                result.append(line[i])
            i += 1
        cleaned_lines.append(''.join(result).rstrip())
    return '\n'.join(cleaned_lines)


def flatten_figures(tex_content: str, figures_subdir: str) -> str:
    """Update figure paths to be in root directory."""
    if not figures_subdir:
        return tex_content
    # Handle various includegraphics patterns
    patterns = [
        (rf'\\includegraphics(\[[^\]]*\])?{{{figures_subdir}/([^}}]+)}}',
         r'\\includegraphics\1{\2}'),
        (rf'\\input{{{figures_subdir}/([^}}]+)}}',
         r'\\input{\1}'),
    ]
    for pattern, replacement in patterns:
        tex_content = re.sub(pattern, replacement, tex_content)
    return tex_content


def create_arxiv_package(paper_id: str, config: dict, output_dir: Path):
    """Create a clean arXiv submission package."""
    paper_dir = PAPERS_DIR / paper_id
    pkg_dir = output_dir / paper_id
    
    # Clean start
    if pkg_dir.exists():
        shutil.rmtree(pkg_dir)
    pkg_dir.mkdir(parents=True)
    
    print(f"\n{'='*60}")
    print(f"Processing {paper_id}: {config['title'][:50]}...")
    print(f"{'='*60}")
    
    # Determine source paths
    main_tex_path = paper_dir / config['main_tex']
    if not main_tex_path.exists():
        print(f"  ERROR: Main tex file not found: {main_tex_path}")
        return
    
    # Read and process main.tex
    with open(main_tex_path, 'r', encoding='utf-8') as f:
        tex_content = f.read()
    
    # Remove comments
    tex_content = remove_comments(tex_content)
    
    # Flatten figure paths
    figures_subdir = config.get('figures_dir', '').split('/')[-1] if config.get('figures_dir') else None
    if figures_subdir:
        tex_content = flatten_figures(tex_content, figures_subdir)
    
    # Add arXiv compilation hint at end
    if 'typeout{get arXiv' not in tex_content:
        tex_content = tex_content.rstrip()
        if tex_content.endswith('\\end{document}'):
            tex_content += '\n\\typeout{get arXiv to do 4 passes: Label(s) may have changed. Rerun}\n'
    
    # Write processed main.tex
    with open(pkg_dir / 'main.tex', 'w', encoding='utf-8') as f:
        f.write(tex_content)
    print(f"  - Wrote main.tex (comments removed, figures flattened)")
    
    # Copy style files
    for sty in config.get('style_files', []):
        sty_path = paper_dir / sty
        if sty_path.exists():
            shutil.copy(sty_path, pkg_dir / sty)
            print(f"  - Copied {sty}")
    
    # Copy .bbl file (pre-compiled bibliography)
    bbl_file = config.get('bbl_file')
    if bbl_file:
        bbl_path = paper_dir / bbl_file
        if bbl_path.exists():
            shutil.copy(bbl_path, pkg_dir / 'main.bbl')
            print(f"  - Copied {bbl_file} -> main.bbl")
        else:
            print(f"  WARNING: BBL file not found: {bbl_path}")
    
    # Copy figures (flattened to root)
    figures_dir = config.get('figures_dir')
    if figures_dir:
        fig_path = paper_dir / figures_dir
        if fig_path.exists():
            fig_count = 0
            for fig in fig_path.iterdir():
                if fig.suffix.lower() in ['.png', '.pdf', '.jpg', '.jpeg', '.eps', '.svg']:
                    shutil.copy(fig, pkg_dir / fig.name)
                    fig_count += 1
            print(f"  - Copied {fig_count} figures to root")
    
    # Create tarball
    tar_path = pkg_dir / 'submission.tar'
    with tarfile.open(tar_path, 'w') as tar:
        for item in pkg_dir.iterdir():
            if item.name != 'submission.tar':
                tar.add(item, arcname=item.name)
    print(f"  - Created submission.tar")
    
    # List contents
    print(f"  Package contents:")
    for item in sorted(pkg_dir.iterdir()):
        if item.name != 'submission.tar':
            size = item.stat().st_size
            print(f"    - {item.name} ({size:,} bytes)")
    
    return pkg_dir


def create_metadata_file(paper_id: str, config: dict, output_dir: Path):
    """Create arXiv metadata file."""
    metadata_path = output_dir / paper_id / 'ARXIV_METADATA.txt'
    
    metadata = f"""arXiv Submission Metadata
========================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Paper: {paper_id}

TITLE (use initial caps, no LaTeX):
{config['title']}

AUTHORS (comma-separated, no "and"):
{config['authors']}

ABSTRACT (plain text, no LaTeX, no line breaks):
{config['abstract']}

PRIMARY CATEGORY:
{config['primary_category']}

CROSS-LIST CATEGORIES:
{', '.join(config['categories'][1:]) if len(config['categories']) > 1 else 'None'}

COMMENTS:
Part of the Agent OS project: https://github.com/imran-siddique/agent-os

LICENSE:
CC BY 4.0

---
Submission Checklist:
[ ] Upload submission.tar
[ ] Verify all files extracted correctly
[ ] Check compiled PDF for errors
[ ] Copy title exactly as above
[ ] Copy authors exactly as above  
[ ] Copy abstract (remove any remaining line breaks)
[ ] Select primary category: {config['primary_category']}
[ ] Add cross-list categories
[ ] Add comments field
"""
    
    with open(metadata_path, 'w', encoding='utf-8') as f:
        f.write(metadata)
    print(f"  - Created ARXIV_METADATA.txt")


def main():
    output_dir = PAPERS_DIR / 'arxiv_submissions'
    output_dir.mkdir(exist_ok=True)
    
    print("="*60)
    print("Generating arXiv Submission Packages")
    print("="*60)
    print(f"Output directory: {output_dir}")
    
    for paper_id, config in PAPERS.items():
        try:
            pkg_dir = create_arxiv_package(paper_id, config, output_dir)
            if pkg_dir:
                create_metadata_file(paper_id, config, output_dir)
        except Exception as e:
            print(f"  ERROR processing {paper_id}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    for paper_id in PAPERS:
        pkg_dir = output_dir / paper_id
        if pkg_dir.exists():
            tar_path = pkg_dir / 'submission.tar'
            if tar_path.exists():
                print(f"  {paper_id}: submission.tar ({tar_path.stat().st_size:,} bytes)")
            else:
                print(f"  {paper_id}: FAILED (no tarball)")
        else:
            print(f"  {paper_id}: FAILED (no directory)")
    
    print(f"\nPackages ready in: {output_dir}")


if __name__ == '__main__':
    main()
