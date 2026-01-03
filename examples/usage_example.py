"""
Example usage of Context-as-a-Service API.

This script demonstrates how to use the API to ingest documents,
extract context, and analyze the corpus.
"""

import requests
import json
from pathlib import Path


API_BASE = "http://localhost:8000"


def ingest_document(file_path: str, format: str, title: str = None):
    """Ingest a document into the service."""
    print(f"\n📤 Ingesting {file_path}...")
    
    with open(file_path, 'rb') as f:
        files = {'file': f}
        data = {
            'format': format,
            'title': title or Path(file_path).stem
        }
        
        response = requests.post(f"{API_BASE}/ingest", files=files, data=data)
        response.raise_for_status()
        
        result = response.json()
        print(f"✅ Document ingested!")
        print(f"   ID: {result['document_id']}")
        print(f"   Type: {result['detected_type']}")
        print(f"   Sections: {result['sections_found']}")
        print(f"   Weights: {json.dumps(result['weights'], indent=2)}")
        
        return result['document_id']


def get_context(document_id: str, query: str = "", max_tokens: int = 1000):
    """Extract context from a document."""
    print(f"\n🔍 Extracting context for document {document_id}...")
    if query:
        print(f"   Query: {query}")
    
    response = requests.post(
        f"{API_BASE}/context/{document_id}",
        json={
            "query": query,
            "max_tokens": max_tokens,
            "include_metadata": True
        }
    )
    response.raise_for_status()
    
    result = response.json()
    print(f"✅ Context extracted!")
    print(f"   Document Type: {result['document_type']}")
    print(f"   Sections Used: {len(result['sections_used'])}")
    print(f"   Total Tokens: {result['total_tokens']}")
    print(f"\n--- Context Preview ---")
    print(result['context'][:500] + "..." if len(result['context']) > 500 else result['context'])
    
    return result


def analyze_document(document_id: str):
    """Analyze a document."""
    print(f"\n📊 Analyzing document {document_id}...")
    
    response = requests.get(f"{API_BASE}/analyze/{document_id}")
    response.raise_for_status()
    
    result = response.json()
    print(f"✅ Analysis complete!")
    print(json.dumps(result, indent=2))
    
    return result


def analyze_corpus():
    """Analyze the entire corpus."""
    print(f"\n📚 Analyzing corpus...")
    
    response = requests.get(f"{API_BASE}/corpus/analyze")
    response.raise_for_status()
    
    result = response.json()
    print(f"✅ Corpus analysis complete!")
    print(json.dumps(result, indent=2))
    
    return result


def list_documents():
    """List all documents."""
    print(f"\n📋 Listing documents...")
    
    response = requests.get(f"{API_BASE}/documents")
    response.raise_for_status()
    
    result = response.json()
    print(f"✅ Found {result['total']} documents")
    for doc in result['documents']:
        print(f"   - {doc['title']} ({doc['type']}) [{doc['id']}]")
    
    return result


def main():
    """Main demonstration."""
    print("=" * 60)
    print("Context-as-a-Service API Demo")
    print("=" * 60)
    
    # Check service health
    response = requests.get(f"{API_BASE}/health")
    if response.status_code == 200:
        print("✅ Service is healthy\n")
    else:
        print("❌ Service is not available")
        return
    
    # Example 1: Ingest HTML document
    try:
        doc_id_1 = ingest_document(
            "examples/api_documentation.html",
            "html",
            "User Management API"
        )
        
        # Extract context with a query
        get_context(doc_id_1, query="authentication", max_tokens=500)
        
    except Exception as e:
        print(f"❌ Error with HTML document: {e}")
    
    # Example 2: Ingest code file
    try:
        doc_id_2 = ingest_document(
            "examples/auth_module.py",
            "code",
            "Authentication Module"
        )
        
        # Extract context
        get_context(doc_id_2, query="register user", max_tokens=800)
        
        # Analyze the document
        analyze_document(doc_id_2)
        
    except Exception as e:
        print(f"❌ Error with code file: {e}")
    
    # List all documents
    try:
        list_documents()
    except Exception as e:
        print(f"❌ Error listing documents: {e}")
    
    # Analyze corpus
    try:
        analyze_corpus()
    except Exception as e:
        print(f"❌ Error analyzing corpus: {e}")
    
    print("\n" + "=" * 60)
    print("Demo complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
