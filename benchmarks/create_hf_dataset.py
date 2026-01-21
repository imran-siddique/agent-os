#!/usr/bin/env python3
"""
Script to create a Hugging Face dataset from the CaaS sample corpus.

This converts the local benchmark corpus into a format suitable for upload
to the Hugging Face Hub.

Usage:
    python benchmarks/create_hf_dataset.py
    python benchmarks/create_hf_dataset.py --push-to-hub
"""

import json
import os
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import argparse

# Domain classification for each file
FILE_METADATA = {
    "auth_module.py": {
        "domain": "Engineering",
        "category": "Code",
        "description": "Authentication module with security features",
        "tags": ["python", "authentication", "security", "jwt", "oauth"],
    },
    "data_processor.py": {
        "domain": "Engineering", 
        "category": "Code",
        "description": "Data processing pipeline with validation",
        "tags": ["python", "data-processing", "etl", "validation"],
    },
    "api_reference.md": {
        "domain": "Documentation",
        "category": "Docs",
        "description": "REST API reference with examples",
        "tags": ["api", "rest", "documentation", "endpoints"],
    },
    "contribution_guide.md": {
        "domain": "Documentation",
        "category": "Docs", 
        "description": "Developer contribution guidelines",
        "tags": ["contributing", "development", "git", "workflow"],
    },
    "troubleshooting_guide.md": {
        "domain": "Documentation",
        "category": "Docs",
        "description": "Common issues and solutions",
        "tags": ["troubleshooting", "debugging", "faq", "support"],
    },
    "employee_handbook.md": {
        "domain": "HR",
        "category": "HR",
        "description": "Employee policies and benefits",
        "tags": ["hr", "policy", "benefits", "employment"],
    },
    "privacy_policy.md": {
        "domain": "Legal",
        "category": "Legal",
        "description": "Data privacy and compliance",
        "tags": ["privacy", "gdpr", "compliance", "legal"],
    },
    "software_license_agreement.md": {
        "domain": "Legal",
        "category": "Legal",
        "description": "Software licensing terms",
        "tags": ["license", "legal", "terms", "agreement"],
    },
    "incident_report.md": {
        "domain": "Security",
        "category": "Business",
        "description": "Security incident documentation",
        "tags": ["security", "incident", "report", "postmortem"],
    },
    "meeting_notes.md": {
        "domain": "Business",
        "category": "Business",
        "description": "Engineering team meeting notes",
        "tags": ["meeting", "notes", "planning", "team"],
    },
    "onboarding_checklist.md": {
        "domain": "HR",
        "category": "HR",
        "description": "New employee onboarding tasks",
        "tags": ["onboarding", "checklist", "hr", "new-hire"],
    },
    "release_notes.md": {
        "domain": "Engineering",
        "category": "Engineering",
        "description": "Software release documentation",
        "tags": ["release", "changelog", "version", "updates"],
    },
    "config_example.yaml": {
        "domain": "Engineering",
        "category": "Engineering",
        "description": "Configuration file example",
        "tags": ["config", "yaml", "settings", "configuration"],
    },
    "database_schema.sql": {
        "domain": "Engineering",
        "category": "Engineering",
        "description": "Database schema definitions",
        "tags": ["database", "sql", "schema", "tables"],
    },
    "remote_work_policy.html": {
        "domain": "HR",
        "category": "HR",
        "description": "Remote work guidelines",
        "tags": ["remote-work", "policy", "wfh", "hybrid"],
    },
    "README.md": {
        "domain": "Documentation",
        "category": "Docs",
        "description": "Sample corpus overview",
        "tags": ["readme", "documentation", "overview"],
    },
    "DATASET_CARD.md": {
        "domain": "Documentation",
        "category": "Docs",
        "description": "Hugging Face dataset card",
        "tags": ["dataset", "metadata", "huggingface"],
    },
}

# File extension to format mapping
FORMAT_MAPPING = {
    ".py": "python",
    ".md": "markdown",
    ".html": "html",
    ".sql": "sql",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".json": "json",
}


def get_file_format(filename: str) -> str:
    """Get the format type based on file extension."""
    ext = Path(filename).suffix.lower()
    return FORMAT_MAPPING.get(ext, "text")


def count_lines(content: str) -> int:
    """Count non-empty lines in content."""
    return len([line for line in content.split("\n") if line.strip()])


def estimate_tokens(content: str) -> int:
    """Rough estimate of token count (words * 1.3 for code/docs)."""
    words = len(content.split())
    return int(words * 1.3)


def generate_doc_id(filename: str, content: str) -> str:
    """Generate a unique document ID."""
    hash_input = f"{filename}:{content[:100]}"
    return hashlib.sha256(hash_input.encode()).hexdigest()[:12]


def extract_sections(content: str, file_format: str) -> List[Dict[str, str]]:
    """Extract section headers from document."""
    sections = []
    
    if file_format == "markdown":
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if line.startswith("#"):
                level = len(line) - len(line.lstrip("#"))
                title = line.lstrip("#").strip()
                sections.append({"level": level, "title": title, "line": i + 1})
    
    elif file_format == "python":
        lines = content.split("\n")
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("class "):
                name = stripped.split("(")[0].replace("class ", "").strip(":")
                sections.append({"level": 1, "title": f"class {name}", "line": i + 1})
            elif stripped.startswith("def ") and not line.startswith("    "):
                name = stripped.split("(")[0].replace("def ", "")
                sections.append({"level": 1, "title": f"def {name}", "line": i + 1})
    
    elif file_format == "html":
        import re
        for match in re.finditer(r"<h([1-6])[^>]*>([^<]+)</h\1>", content, re.IGNORECASE):
            level = int(match.group(1))
            title = match.group(2).strip()
            sections.append({"level": level, "title": title, "line": 0})
    
    elif file_format == "sql":
        lines = content.split("\n")
        for i, line in enumerate(lines):
            upper = line.upper().strip()
            if upper.startswith("CREATE TABLE"):
                name = line.split()[2].strip("(").strip("`").strip('"')
                sections.append({"level": 1, "title": f"TABLE {name}", "line": i + 1})
            elif upper.startswith("CREATE INDEX"):
                name = line.split()[2]
                sections.append({"level": 2, "title": f"INDEX {name}", "line": i + 1})
    
    return sections


def process_corpus(corpus_dir: Path) -> List[Dict[str, Any]]:
    """Process all files in the corpus directory."""
    documents = []
    
    # Files to exclude from the dataset
    exclude_files = {"DATASET_CARD.md"}  # The dataset card itself shouldn't be data
    
    for filepath in sorted(corpus_dir.iterdir()):
        if not filepath.is_file():
            continue
        
        filename = filepath.name
        
        if filename in exclude_files:
            continue
            
        if filename.startswith("."):
            continue
        
        try:
            content = filepath.read_text(encoding="utf-8")
        except Exception as e:
            print(f"Warning: Could not read {filename}: {e}")
            continue
        
        file_format = get_file_format(filename)
        metadata = FILE_METADATA.get(filename, {
            "domain": "Other",
            "category": "Other",
            "description": f"Document: {filename}",
            "tags": [],
        })
        
        sections = extract_sections(content, file_format)
        
        doc = {
            "id": generate_doc_id(filename, content),
            "filename": filename,
            "content": content,
            "format": file_format,
            "domain": metadata["domain"],
            "category": metadata["category"],
            "description": metadata["description"],
            "tags": metadata["tags"],
            "num_lines": count_lines(content),
            "num_chars": len(content),
            "estimated_tokens": estimate_tokens(content),
            "sections": sections,
            "num_sections": len(sections),
            "created_at": datetime.now().isoformat(),
        }
        
        documents.append(doc)
        print(f"✓ Processed: {filename} ({file_format}, {doc['num_lines']} lines)")
    
    return documents


def save_jsonl(documents: List[Dict[str, Any]], output_path: Path) -> None:
    """Save documents as JSONL file."""
    with open(output_path, "w", encoding="utf-8") as f:
        for doc in documents:
            f.write(json.dumps(doc, ensure_ascii=False) + "\n")
    print(f"\n✓ Saved {len(documents)} documents to {output_path}")


def save_json(documents: List[Dict[str, Any]], output_path: Path) -> None:
    """Save documents as JSON file (for preview)."""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(documents, f, indent=2, ensure_ascii=False)
    print(f"✓ Saved preview to {output_path}")


def create_dataset_loading_script(output_dir: Path) -> None:
    """Create a dataset loading script for Hugging Face."""
    script = '''"""CaaS Benchmark Corpus dataset loader for Hugging Face."""

import json
import datasets


_CITATION = """
@misc{caas2026,
  author = {Imran Siddique},
  title = {Context-as-a-Service: Intelligent Context Extraction Pipeline},
  year = {2026},
  publisher = {GitHub},
  url = {https://github.com/imran-siddique/context-as-a-service}
}
"""

_DESCRIPTION = """
CaaS Benchmark Corpus v1 - A diverse collection of synthetic enterprise documents 
for benchmarking context extraction and RAG systems.
"""

_HOMEPAGE = "https://github.com/imran-siddique/context-as-a-service"
_LICENSE = "MIT"


class CaasBenchmarkCorpus(datasets.GeneratorBasedBuilder):
    """CaaS Benchmark Corpus dataset."""

    VERSION = datasets.Version("1.0.0")

    def _info(self):
        return datasets.DatasetInfo(
            description=_DESCRIPTION,
            features=datasets.Features({
                "id": datasets.Value("string"),
                "filename": datasets.Value("string"),
                "content": datasets.Value("string"),
                "format": datasets.Value("string"),
                "domain": datasets.Value("string"),
                "category": datasets.Value("string"),
                "description": datasets.Value("string"),
                "tags": datasets.Sequence(datasets.Value("string")),
                "num_lines": datasets.Value("int32"),
                "num_chars": datasets.Value("int32"),
                "estimated_tokens": datasets.Value("int32"),
                "sections": datasets.Sequence({
                    "level": datasets.Value("int32"),
                    "title": datasets.Value("string"),
                    "line": datasets.Value("int32"),
                }),
                "num_sections": datasets.Value("int32"),
                "created_at": datasets.Value("string"),
            }),
            supervised_keys=None,
            homepage=_HOMEPAGE,
            license=_LICENSE,
            citation=_CITATION,
        )

    def _split_generators(self, dl_manager):
        data_file = dl_manager.download_and_extract("data/corpus.jsonl")
        return [
            datasets.SplitGenerator(
                name=datasets.Split.TRAIN,
                gen_kwargs={"filepath": data_file},
            ),
        ]

    def _generate_examples(self, filepath):
        with open(filepath, encoding="utf-8") as f:
            for idx, line in enumerate(f):
                doc = json.loads(line)
                yield idx, doc
'''
    
    script_path = output_dir / "caas_benchmark_corpus.py"
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(script)
    print(f"✓ Created dataset loading script: {script_path}")


def push_to_hub(output_dir: Path, repo_id: str) -> None:
    """Push dataset to Hugging Face Hub."""
    try:
        from huggingface_hub import HfApi, login
        from datasets import load_dataset
        
        print("\n🔐 Logging in to Hugging Face Hub...")
        login()
        
        print(f"\n📤 Pushing dataset to {repo_id}...")
        
        # Load the local dataset
        dataset = load_dataset("json", data_files=str(output_dir / "data" / "corpus.jsonl"))
        
        # Push to hub
        dataset.push_to_hub(repo_id, private=False)
        
        # Upload the README (dataset card)
        api = HfApi()
        readme_path = output_dir / "README.md"
        if readme_path.exists():
            api.upload_file(
                path_or_fileobj=str(readme_path),
                path_in_repo="README.md",
                repo_id=repo_id,
                repo_type="dataset",
            )
        
        print(f"\n✅ Dataset pushed to: https://huggingface.co/datasets/{repo_id}")
        
    except ImportError:
        print("\n❌ Error: Install huggingface_hub: pip install huggingface_hub")
    except Exception as e:
        print(f"\n❌ Error pushing to hub: {e}")


def main():
    parser = argparse.ArgumentParser(description="Create HF dataset from CaaS corpus")
    parser.add_argument(
        "--corpus-dir",
        type=Path,
        default=Path("benchmarks/data/sample_corpus"),
        help="Path to the sample corpus directory",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("benchmarks/hf_dataset"),
        help="Output directory for HF dataset files",
    )
    parser.add_argument(
        "--push-to-hub",
        action="store_true",
        help="Push dataset to Hugging Face Hub",
    )
    parser.add_argument(
        "--repo-id",
        type=str,
        default="mosiddi/caas-benchmark-corpus-v1",
        help="Hugging Face repository ID",
    )
    args = parser.parse_args()
    
    print("=" * 60)
    print("🤗 CaaS Benchmark Corpus - Hugging Face Dataset Creator")
    print("=" * 60)
    
    # Verify corpus exists
    if not args.corpus_dir.exists():
        print(f"❌ Corpus directory not found: {args.corpus_dir}")
        return 1
    
    # Create output directory
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "data").mkdir(exist_ok=True)
    
    # Process corpus
    print(f"\n📂 Processing corpus from: {args.corpus_dir}")
    documents = process_corpus(args.corpus_dir)
    
    if not documents:
        print("❌ No documents found!")
        return 1
    
    # Save as JSONL (main data file)
    jsonl_path = args.output_dir / "data" / "corpus.jsonl"
    save_jsonl(documents, jsonl_path)
    
    # Save as JSON (for preview/debugging)
    json_path = args.output_dir / "corpus_preview.json"
    save_json(documents[:3], json_path)  # Save first 3 for preview
    
    # Copy dataset card as README
    dataset_card = args.corpus_dir / "DATASET_CARD.md"
    if dataset_card.exists():
        readme_content = dataset_card.read_text(encoding="utf-8")
        (args.output_dir / "README.md").write_text(readme_content, encoding="utf-8")
        print(f"✓ Copied dataset card to README.md")
    
    # Create loading script
    create_dataset_loading_script(args.output_dir)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 Dataset Summary")
    print("=" * 60)
    print(f"Total documents: {len(documents)}")
    print(f"Total lines: {sum(d['num_lines'] for d in documents):,}")
    print(f"Total characters: {sum(d['num_chars'] for d in documents):,}")
    print(f"Estimated tokens: {sum(d['estimated_tokens'] for d in documents):,}")
    print("\nBy format:")
    formats = {}
    for doc in documents:
        formats[doc['format']] = formats.get(doc['format'], 0) + 1
    for fmt, count in sorted(formats.items()):
        print(f"  {fmt}: {count}")
    print("\nBy domain:")
    domains = {}
    for doc in documents:
        domains[doc['domain']] = domains.get(doc['domain'], 0) + 1
    for domain, count in sorted(domains.items()):
        print(f"  {domain}: {count}")
    
    print(f"\n📁 Output directory: {args.output_dir}")
    print(f"   - data/corpus.jsonl (main data)")
    print(f"   - README.md (dataset card)")
    print(f"   - corpus_preview.json (preview)")
    print(f"   - caas_benchmark_corpus.py (loading script)")
    
    # Push to hub if requested
    if args.push_to_hub:
        push_to_hub(args.output_dir, args.repo_id)
    else:
        print(f"\n💡 To push to Hugging Face Hub, run:")
        print(f"   python benchmarks/create_hf_dataset.py --push-to-hub --repo-id {args.repo_id}")
    
    return 0


if __name__ == "__main__":
    exit(main())
