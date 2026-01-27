#!/usr/bin/env python
"""
Quick verification script to test sample corpus ingestion.

This script verifies that the sample corpus files can be loaded and
basic functionality works as expected.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from caas.storage.document_store import DocumentStore
from caas.ingestion.html_processor import HTMLProcessor
from caas.ingestion.code_processor import CodeProcessor


def test_sample_corpus():
    """Test ingestion of sample corpus files."""
    print("Testing sample corpus ingestion...\n")
    
    corpus_path = Path(__file__).parent / "data" / "sample_corpus"
    
    if not corpus_path.exists():
        print(f"❌ Sample corpus not found at {corpus_path}")
        return False
    
    # Initialize storage
    store = DocumentStore()
    html_processor = HTMLProcessor()
    code_processor = CodeProcessor()
    
    # Test files
    test_files = [
        ("remote_work_policy.html", "html", "Remote Work Policy"),
        ("contribution_guide.md", "html", "Contribution Guide"),  # Treated as HTML
        ("auth_module.py", "code", "Authentication Module"),
    ]
    
    success_count = 0
    
    for filename, format_type, title in test_files:
        file_path = corpus_path / filename
        
        if not file_path.exists():
            print(f"❌ File not found: {filename}")
            continue
        
        try:
            # Process based on format
            if format_type == "html":
                doc = html_processor.process(str(file_path), title)
            elif format_type == "code":
                doc = code_processor.process(str(file_path), title)
            else:
                print(f"❌ Unknown format: {format_type}")
                continue
            
            # Verify document
            if doc and doc.title == title:
                print(f"✓ Successfully processed: {filename}")
                print(f"  - Title: {doc.title}")
                print(f"  - Chunks: {len(doc.chunks)}")
                print(f"  - Detected type: {doc.detected_type}")
                success_count += 1
            else:
                print(f"❌ Failed to process: {filename}")
        
        except Exception as e:
            print(f"❌ Error processing {filename}: {e}")
    
    print(f"\n{'=' * 50}")
    print(f"Results: {success_count}/{len(test_files)} files processed successfully")
    print(f"{'=' * 50}")
    
    return success_count == len(test_files)


if __name__ == "__main__":
    success = test_sample_corpus()
    sys.exit(0 if success else 1)
