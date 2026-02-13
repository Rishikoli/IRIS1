
import sys
import os
import shutil
import argparse
from datetime import datetime
import chromadb
from pprint import pprint

# Ensure we can import from src
sys.path.append(os.getcwd())

from src.config import settings

def get_client():
    if not os.path.exists(settings.chroma_persist_directory):
        print(f"Directory {settings.chroma_persist_directory} does not exist.")
        return None
    return chromadb.PersistentClient(path=settings.chroma_persist_directory)

def list_documents(args):
    client = get_client()
    if not client: return

    try:
        collection = client.get_collection("financial_documents")
        count = collection.count()
        print(f"Collection: financial_documents")
        print(f"Total Documents: {count}")
        
        if count > 0:
            # Get unique sources
            results = collection.get(include=['metadatas'])
            sources = set()
            for m in results['metadatas']:
                if m and 'source' in m:
                    sources.add(m['source'])
                elif m and 'company' in m:
                    sources.add(f"Analysis: {m['company']}")
            
            print("\nSources found:")
            for s in sorted(sources):
                print(f"- {s}")
    except Exception as e:
        print(f"Error: {e}")

def peek_documents(args):
    client = get_client()
    if not client: return

    try:
        collection = client.get_collection("financial_documents")
        results = collection.peek(limit=args.limit)
        
        for i in range(len(results['ids'])):
            print(f"\n[ID: {results['ids'][i]}]")
            print(f"Metadata: {results['metadatas'][i]}")
            print(f"Content: {results['documents'][i][:200]}...")
    except Exception as e:
        print(f"Error: {e}")

def reset_db(args):
    if input("Are you sure you want to WIPE all vector data? (y/n): ").lower() != 'y':
        print("Cancelled.")
        return

    path = settings.chroma_persist_directory
    if os.path.exists(path):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{path}_backup_{timestamp}"
        print(f"Backing up to {backup_path}...")
        shutil.move(path, backup_path)
        print("Reset complete. ChromaDB will re-initialize on next run.")
    else:
        print("Database directory not found.")

def main():
    parser = argparse.ArgumentParser(description="I.R.I.S. ChromaDB Manager")
    subparsers = parser.add_subparsers()

    # List
    parser_list = subparsers.add_parser('list', help='List summary of indexed documents')
    parser_list.set_defaults(func=list_documents)

    # Peek
    parser_peek = subparsers.add_parser('peek', help='View last N documents')
    parser_peek.add_argument('--limit', type=int, default=5)
    parser_peek.set_defaults(func=peek_documents)

    # Reset
    parser_reset = subparsers.add_parser('reset', help='Wipe the database (with backup)')
    parser_reset.set_defaults(func=reset_db)

    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
