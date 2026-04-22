"""
CampGPT RAG System - Complete Usage Guide & Examples
====================================================

This guide demonstrates how to use the CampGPT RAG system with different approaches.
"""

import json
import os
from campgpt_rag import CampGPTRAG

# ============================================================================
# 1. BASIC USAGE - Single Campsite
# ============================================================================

def example_basic_usage():
    """Example: Basic query on single campsite data."""
    print("\n" + "="*80)
    print("EXAMPLE 1: Basic Usage with Single Campsite")
    print("="*80 + "\n")
    
    # Initialize RAG system
    rag = CampGPTRAG()
    
    # Ingest single campsite data
    json_file = "/home/claude/sample_campsites.json"
    rag.ingest_json_data(json_file)
    
    # Single query
    question = "Is this site safe for my 70-year-old father who uses a walker?"
    response = rag.query(question)
    
    print(f"Question: {question}")
    print(f"\nAnswer: {response['answer']}")
    print(f"\nSources Used: {len(response.get('sources', []))} documents")


# ============================================================================
# 2. BATCH PROCESSING - Multiple Questions
# ============================================================================

def example_batch_queries():
    """Example: Process multiple questions in batch mode."""
    print("\n" + "="*80)
    print("EXAMPLE 2: Batch Query Processing")
    print("="*80 + "\n")
    
    rag = CampGPTRAG()
    rag.ingest_json_data("/home/claude/sample_campsites.json")
    
    # Multiple questions
    questions = [
        "Can we bring our electric car and charge it?",
        "What are the quiet hours?",
        "Is the campsite accessible for wheelchair users?",
        "Are dogs allowed?"
    ]
    
    print(f"Processing {len(questions)} questions in batch mode...\n")
    responses = rag.batch_query(questions)
    
    for i, (question, response) in enumerate(zip(questions, responses), 1):
        print(f"\n{i}. Q: {question}")
        print(f"   A: {response['answer'][:150]}...")
        print(f"   Status: {'✓ Success' if response['success'] else '✗ Failed'}")


# ============================================================================
# 3. USE CASE A: Multi-Generational Filter
# ============================================================================

def example_multi_generational_filter():
    """Example Use Case A: Filtering for elderly guests with mobility needs."""
    print("\n" + "="*80)
    print("EXAMPLE 3: Use Case A - Multi-Generational Filter")
    print("="*80 + "\n")
    print("Scenario: Family with 5 people (including elderly person with walker)")
    print("-" * 80 + "\n")
    
    rag = CampGPTRAG()
    rag.ingest_json_data("/home/claude/sample_campsites.json")
    
    queries = [
        "I'm traveling with 5 people, including one person over 70 with a walker. Is this a good fit?",
        "What accessibility features do you have for elderly guests?",
        "Are there wheelchair-accessible toilets and showers?",
        "What do guests say about cleanliness and safety?",
        "Are restaurants accessible?"
    ]
    
    responses = rag.batch_query(queries)
    
    for question, response in zip(queries, responses):
        print(f"Q: {question}")
        print(f"A: {response['answer']}\n")
        print("-" * 80 + "\n")


# ============================================================================
# 4. USE CASE B: Logistic Planning
# ============================================================================

def example_logistic_planning():
    """Example Use Case B: EV charging and vehicle logistics."""
    print("\n" + "="*80)
    print("EXAMPLE 4: Use Case B - Logistic Planning")
    print("="*80 + "\n")
    print("Scenario: Traveling with electric vehicle and checking logistics")
    print("-" * 80 + "\n")
    
    rag = CampGPTRAG()
    rag.ingest_json_data("/home/claude/sample_campsites.json")
    
    queries = [
        "Can we charge our Tesla there?",
        "What's the charging speed?",
        "Are there any restrictions on vehicle height or length?",
        "What's the maximum amps available?",
        "Is there parking for large vehicles?"
    ]
    
    responses = rag.batch_query(queries)
    
    for question, response in zip(queries, responses):
        print(f"Q: {question}")
        print(f"A: {response['answer']}\n")


# ============================================================================
# 5. USE CASE C: Real-World Sentiment Analysis
# ============================================================================

def example_sentiment_analysis():
    """Example Use Case C: Guest reviews and sentiment."""
    print("\n" + "="*80)
    print("EXAMPLE 5: Use Case C - Real-World Sentiment Analysis")
    print("="*80 + "\n")
    print("Scenario: Understanding guest experiences and hidden costs")
    print("-" * 80 + "\n")
    
    rag = CampGPTRAG()
    rag.ingest_json_data("/home/claude/sample_campsites.json")
    
    queries = [
        "What do people say about the extra costs?",
        "Is the food reasonably priced?",
        "What do guests think about cleanliness?",
        "Are there hidden charges I should know about?",
        "Do guests feel the campsite is worth the money?"
    ]
    
    responses = rag.batch_query(queries)
    
    for question, response in zip(queries, responses):
        print(f"Q: {question}")
        print(f"A: {response['answer']}\n")


# ============================================================================
# 6. ADVANCED: Custom Configuration
# ============================================================================

def example_custom_configuration():
    """Example: Advanced configuration with custom parameters."""
    print("\n" + "="*80)
    print("EXAMPLE 6: Custom Configuration")
    print("="*80 + "\n")
    
    # Initialize with custom settings
    rag = CampGPTRAG(
        embedding_model="models/embedding-001",
        llm_model="gemini-1.5-flash",
        chroma_persist_dir="./custom_chroma_db",
        temperature=0.5  # Lower temperature = more consistent, less creative
    )
    
    # Ingest with custom chunk settings
    rag.ingest_json_data(
        json_file_path="/home/claude/sample_campsites.json",
        chunk_size=300,  # Smaller chunks for more specific retrieval
        chunk_overlap=50
    )
    
    # Get system info
    info = rag.get_campsite_info()
    
    print("System Configuration:")
    print(json.dumps(info, indent=2))
    
    # Query with custom config
    response = rag.query("What makes this campsite special?")
    print(f"\nQuery Response:\n{response['answer']}")


# ============================================================================
# 7. ERROR HANDLING & VALIDATION
# ============================================================================

def example_error_handling():
    """Example: Proper error handling and validation."""
    print("\n" + "="*80)
    print("EXAMPLE 7: Error Handling & Validation")
    print("="*80 + "\n")
    
    try:
        rag = CampGPTRAG()
        
        # Try to ingest non-existent file
        print("Attempting to ingest non-existent file...")
        rag.ingest_json_data("/path/that/does/not/exist.json")
        
    except FileNotFoundError as e:
        print(f"✓ Caught expected error: {e}")
    except Exception as e:
        print(f"✓ Caught error: {type(e).__name__}: {e}")
    
    # Proper initialization
    print("\nInitializing with valid data...")
    rag = CampGPTRAG()
    rag.ingest_json_data("/home/claude/sample_campsites.json")
    
    # Query with empty string
    response = rag.query("")
    print(f"Empty query response: {response['answer'][:100]}...")


# ============================================================================
# 8. JSON DATA STRUCTURE EXAMPLES
# ============================================================================

def example_json_structure_guide():
    """Show optimal JSON structure for RAG system."""
    print("\n" + "="*80)
    print("EXAMPLE 8: Recommended JSON Structure")
    print("="*80 + "\n")
    
    optimal_structure = {
        "id": "unique_campsite_id",
        "name": "Campsite Name",
        "location": {
            "country": "Country",
            "region": "Region",
            "city": "City",
            "coordinates": {
                "latitude": 0.0,
                "longitude": 0.0
            }
        },
        "facilities": {
            "toilets": {
                "count": 10,
                "wheelchair_accessible": True,
                "hot_showers": True
            },
            "electricity": {
                "available": True,
                "amps": 16,
                "connection_points": 45
            },
            "ev_charging": {
                "available": True,
                "charging_points": 3,
                "charging_speed": "7kW"
            }
        },
        "rules": {
            "quiet_hours": {
                "start": "22:00",
                "end": "08:00"
            },
            "pets": {
                "allowed": True,
                "restrictions": "Description here"
            }
        },
        "reviews": [
            {
                "rating": 4.5,
                "comment": "Review text here",
                "verified": True
            }
        ],
        "accessibility": {
            "wheelchair_accessible_pitches": 5,
            "accessible_toilets": True,
            "ramps": "Everywhere"
        },
        "amenities": {
            "restaurants": 2,
            "wifi": True,
            "pool": True
        }
    }
    
    print("Optimal JSON Structure for Campsite Data:")
    print(json.dumps(optimal_structure, indent=2))
    print("\nBest Practices:")
    print("✓ Use consistent key naming (snake_case)")
    print("✓ Include detailed facility information")
    print("✓ Add guest reviews for sentiment analysis")
    print("✓ Be specific about accessibility features")
    print("✓ Include pricing and extra costs")
    print("✓ Add location coordinates for geo-features (future)")


# ============================================================================
# 9. MULTI-LANGUAGE SUPPORT
# ============================================================================

def example_multi_language():
    """Example: Multi-language queries on same data."""
    print("\n" + "="*80)
    print("EXAMPLE 9: Multi-Language Support")
    print("="*80 + "\n")
    print("CampGPT supports queries in multiple languages!")
    print("-" * 80 + "\n")
    
    rag = CampGPTRAG()
    rag.ingest_json_data("/home/claude/sample_campsites.json")
    
    # Different language queries
    queries = {
        "English": "Can we bring our electric car and charge it?",
        "Dutch": "Kunnen we onze elektrische auto meenemen en hier opladen?",
        "German": "Können wir unser Elektroauto mitbringen und hier aufladen?",
        "French": "Pouvons-nous apporter notre voiture électrique et la recharger ici?",
        "Italian": "Possiamo portare la nostra auto elettrica e ricaricarla qui?"
    }
    
    for language, question in queries.items():
        print(f"[{language}] Q: {question}")
        response = rag.query(question)
        print(f"A: {response['answer'][:100]}...\n")


# ============================================================================
# 10. DEPLOYMENT & SCALING
# ============================================================================

def example_deployment_tips():
    """Best practices for deployment and scaling."""
    print("\n" + "="*80)
    print("EXAMPLE 10: Deployment & Scaling Tips")
    print("="*80 + "\n")
    
    tips = """
DEPLOYMENT BEST PRACTICES:

1. API KEY MANAGEMENT:
   - Use environment variables: os.getenv("GOOGLE_API_KEY")
   - For production: Use secrets management (AWS Secrets Manager, etc.)
   - Never commit API keys to version control

2. VECTOR DATABASE:
   - Chroma: Use for small-medium deployments (<1GB)
   - Pinecone: Use for large-scale deployments (free tier available)
   - Switch in 2 lines of code

3. CACHING:
   - Cache ingested data to avoid re-processing
   - Use Redis for multi-instance deployments
   - Implement chat history caching

4. SCALING STRATEGIES:
   - Use Gemini 1.5 Flash for cost-efficient scaling
   - Implement rate limiting on API calls
   - Use batch processing for multiple questions
   - Monitor API usage and costs

5. MONITORING:
   - Log all queries and responses
   - Track response times and quality
   - Monitor API error rates
   - Implement alerting for failures

6. SECURITY:
   - Validate and sanitize user inputs
   - Implement authentication for web interface
   - Use HTTPS for all communications
   - Regular security audits

7. PERFORMANCE:
   - Use persistent Chroma DB (don't recreate)
   - Implement query result caching
   - Optimize chunk size (300-500 chars typical)
   - Use k=5 for retrieval (sweet spot)

8. COST OPTIMIZATION:
   - Gemini 1.5 Flash: ~$0.075/M input, $0.30/M output tokens
   - Text Embedding: Free tier available
   - Batch similar queries together
   - Use lower temperature (0.3-0.5) for factual queries
    """
    
    print(tips)


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Run all examples."""
    print("\n" + "="*80)
    print("CampGPT RAG SYSTEM - COMPREHENSIVE EXAMPLES")
    print("="*80)
    
    examples = [
        ("1. Basic Usage", example_basic_usage),
        ("2. Batch Queries", example_batch_queries),
        ("3. Multi-Generational Filter", example_multi_generational_filter),
        ("4. Logistic Planning", example_logistic_planning),
        ("5. Sentiment Analysis", example_sentiment_analysis),
        ("6. Custom Configuration", example_custom_configuration),
        ("7. Error Handling", example_error_handling),
        ("8. JSON Structure Guide", example_json_structure_guide),
        ("9. Multi-Language Support", example_multi_language),
        ("10. Deployment Tips", example_deployment_tips),
    ]
    
    print("\nAvailable Examples:")
    for name, _ in examples:
        print(f"  • {name}")
    
    print("\nRunning examples...\n")
    
    for name, example_func in examples:
        try:
            print(f"\n{'#'*80}")
            print(f"# {name}")
            print(f"{'#'*80}")
            example_func()
        except Exception as e:
            print(f"⚠️  Error in {name}: {e}")
            continue


if __name__ == "__main__":
    main()
