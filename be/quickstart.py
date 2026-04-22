#!/usr/bin/env python3
"""
CampGPT Quick Start Script
Interactive setup and testing tool for CampGPT RAG system
"""

import os
import sys
import json
from pathlib import Path
from typing import Optional


def print_header(text: str):
    """Print formatted header."""
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80 + "\n")


def print_step(number: int, text: str):
    """Print formatted step."""
    print(f"  [{number}] {text}")


def check_installation():
    """Check if required packages are installed."""
    print_header("CHECKING INSTALLATION")
    
    required_packages = [
        'langchain',
        'langchain_community',
        'langchain_google_genai',
        'chromadb',
        'streamlit',
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} (MISSING)")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("\nInstall with:")
        print(f"  pip install -r requirements.txt")
        return False
    
    print("\n✓ All packages installed!")
    return True


def check_api_key():
    """Check and configure Google API key."""
    print_header("GOOGLE API KEY SETUP")
    
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if api_key:
        print(f"✓ Found API key in environment: {api_key[:10]}...")
        return api_key
    
    print("No API key found in GOOGLE_API_KEY environment variable.\n")
    print("Get a free API key:")
    print("  1. Visit https://ai.google.dev/")
    print("  2. Click 'Get API Key'")
    print("  3. Create a new API key")
    print("  4. Copy the key\n")
    
    api_key = input("Paste your API key here (or press Enter to skip): ").strip()
    
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key
        print(f"\n✓ API key set: {api_key[:10]}...")
        return api_key
    
    print("\n⚠️  No API key provided. You won't be able to run the system.")
    return None


def check_data_file():
    """Check and select data file."""
    print_header("DATA FILE SETUP")
    
    sample_file = Path("sample_campsites.json")
    
    if sample_file.exists():
        print(f"✓ Found sample data: {sample_file}")
        print(f"  ({os.path.getsize(sample_file)} bytes)")
        
        use_sample = input("\nUse sample data? (y/n): ").strip().lower()
        if use_sample == 'y':
            return str(sample_file)
    
    print("\nSpecify a JSON file with campsite data:")
    print("  Format: {'name': '...', 'facilities': {...}, ...}")
    
    file_path = input("Path to JSON file (or press Enter to use sample): ").strip()
    
    if file_path:
        if Path(file_path).exists():
            print(f"✓ Found file: {file_path}")
            return file_path
        else:
            print(f"✗ File not found: {file_path}")
            return None
    
    # Create sample if it doesn't exist
    print("\nCreating sample data file...")
    from campgpt_rag import create_sample_campsite_json
    sample_file = create_sample_campsite_json()
    print(f"✓ Created: {sample_file}")
    return sample_file


def test_rag_system(api_key: str, data_file: str) -> bool:
    """Test RAG system with sample query."""
    print_header("TESTING RAG SYSTEM")
    
    try:
        print("  Importing CampGPT...")
        from campgpt_rag import CampGPTRAG
        
        print("  Initializing RAG system...")
        rag = CampGPTRAG(google_api_key=api_key)
        
        print("  Ingesting data...")
        rag.ingest_json_data(data_file)
        
        print("  Running test query...")
        response = rag.query("What facilities are available?")
        
        print("\n  Test Query Response:")
        print(f"  ✓ Answer received ({len(response['answer'])} chars)")
        print(f"  ✓ Sources: {len(response.get('sources', []))} documents")
        
        if response.get('answer'):
            print(f"\n  Preview:")
            preview = response['answer'][:150]
            print(f"  \"{preview}...\"")
        
        print("\n✓ RAG System is working!")
        return True
        
    except Exception as e:
        print(f"\n✗ Error testing RAG system:")
        print(f"  {type(e).__name__}: {e}")
        return False


def show_usage_options():
    """Show available usage options."""
    print_header("USAGE OPTIONS")
    
    options = {
        "1": {
            "name": "Run Streamlit Web App",
            "command": "streamlit run streamlit_app.py",
            "description": "Interactive web interface for CampGPT"
        },
        "2": {
            "name": "Run Example Scripts",
            "command": "python examples.py",
            "description": "Run comprehensive examples"
        },
        "3": {
            "name": "Interactive Python Shell",
            "command": "python3 -c \"from campgpt_rag import CampGPTRAG; rag = CampGPTRAG(); rag.ingest_json_data('sample_campsites.json')\"",
            "description": "Start Python REPL with RAG system"
        },
        "4": {
            "name": "Run a Custom Query",
            "command": None,
            "description": "Ask a specific question"
        },
    }
    
    for key, option in options.items():
        print(f"  {key}. {option['name']}")
        print(f"     {option['description']}\n")
    
    return options


def run_custom_query(api_key: str, data_file: str):
    """Run a custom query."""
    print_header("CUSTOM QUERY")
    
    from campgpt_rag import CampGPTRAG
    
    rag = CampGPTRAG(google_api_key=api_key)
    rag.ingest_json_data(data_file)
    
    queries = [
        "Is this site safe for my 70-year-old father who uses a walker?",
        "Can we bring our electric car and charge it here?",
        "Are dogs allowed? What are the rules?",
        "What do guests say about extra costs?",
        "How many wheelchair-accessible pitches do you have?"
    ]
    
    print("Example questions:")
    for i, q in enumerate(queries, 1):
        print(f"  {i}. {q}")
    
    print("\nOr type your own question.")
    
    user_query = input("\nYour question: ").strip()
    
    if not user_query:
        user_query = queries[0]
        print(f"Using first example: {user_query}")
    
    print("\n  Processing query...\n")
    response = rag.query(user_query)
    
    print(f"Answer:\n{response['answer']}\n")
    
    if response.get('sources'):
        print(f"Sources ({len(response['sources'])} documents):")
        for i, source in enumerate(response['sources'], 1):
            print(f"  {i}. {source['metadata']['campsite_name']} - {source['metadata']['section']}")


def show_next_steps():
    """Show next steps."""
    print_header("NEXT STEPS")
    
    print("""
  1. WEB INTERFACE:
     Run: streamlit run streamlit_app.py
     Then open: http://localhost:8501

  2. LEARN MORE:
     - Read: README.md
     - Run: python examples.py
     - View: sample_campsites.json

  3. CUSTOMIZE:
     - Edit sample_campsites.json with your data
     - Modify chunk_size in ingest_json_data()
     - Adjust temperature in CampGPTRAG initialization

  4. DEPLOY:
     - Docker: See README.md
     - Streamlit Cloud: git push to GitHub
     - FastAPI: See integration examples in README.md

  5. EXTEND:
     - Add more campsites to JSON
     - Implement caching
     - Connect to booking system
     - Add analytics

Documentation: https://github.com/your-repo/campgpt
API Docs: https://ai.google.dev/
    """)


def main():
    """Main setup flow."""
    print("\n")
    print("█" * 80)
    print("█" + " " * 78 + "█")
    print("█" + "  🏕️  CampGPT - Intelligent Campsite Concierge".center(78) + "█")
    print("█" + "  RAG-Based Chatbot for Hyper-Personalized Travel Advice".center(78) + "█")
    print("█" + " " * 78 + "█")
    print("█" * 80)
    
    # Step 1: Check installation
    if not check_installation():
        print("\n❌ Setup failed. Please install missing packages.")
        sys.exit(1)
    
    # Step 2: Check API key
    api_key = check_api_key()
    if not api_key:
        print("\n⚠️  Continuing without API key (won't work).")
        sys.exit(1)
    
    # Step 3: Check data file
    data_file = check_data_file()
    if not data_file:
        print("\n❌ No data file provided. Exiting.")
        sys.exit(1)
    
    # Step 4: Test system
    if test_rag_system(api_key, data_file):
        # Step 5: Show options
        print("\n")
        options = show_usage_options()
        
        choice = input("Choose an option (1-4, or press Enter to show more): ").strip()
        
        if choice == "1":
            print("\nStarting Streamlit app...")
            print("Command: streamlit run streamlit_app.py")
            os.system("streamlit run streamlit_app.py")
        
        elif choice == "2":
            print("\nRunning examples...")
            print("Command: python examples.py")
            os.system("python examples.py")
        
        elif choice == "3":
            print("\nStarting Python REPL...")
            os.system("python3")
        
        elif choice == "4":
            run_custom_query(api_key, data_file)
            show_next_steps()
        
        else:
            show_next_steps()
    
    else:
        print("\n❌ System test failed. Check your API key and data file.")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        sys.exit(1)
