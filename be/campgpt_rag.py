# python BE: https://hackathon-2026-xnok.onrender.com
# cdn: https://d3rzchwrt70me2.cloudfront.net/

"""
CampGPT - RAG-Based Campsite Concierge
Intelligent chatbot for hyper-personalized camping trip planning
"""

import json
import os
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

# LangChain imports
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.schema import Document

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CampGPTRAG:
    """
    RAG system for campsite information retrieval and AI-powered recommendations.
    
    Features:
    - JSON-based campsite data ingestion
    - Vector embedding and semantic search
    - Context-aware LLM responses
    - Multi-lingual support
    """
    
    def __init__(
        self,
        google_api_key: Optional[str] = None,
        embedding_model: str = "models/gemini-embedding-001",
        llm_model: str = "gemini-2.5-flash-lite",
        chroma_persist_dir: str = "./chroma_db",
        temperature: float = 0.7
    ):
        """
        Initialize CampGPT RAG system.
        
        Args:
            google_api_key: Google API key (or use GOOGLE_API_KEY env var)
            embedding_model: Google embedding model to use
            llm_model: Gemini model for responses
            chroma_persist_dir: Directory to persist Chroma vector DB
            temperature: LLM temperature (0-1)
        """
        self.api_key = google_api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Google API key not provided. Set GOOGLE_API_KEY environment variable "
                "or pass google_api_key parameter."
            )
        
        self.embedding_model = embedding_model
        self.llm_model = llm_model
        self.chroma_persist_dir = chroma_persist_dir
        self.temperature = temperature
        self.vectorstore = None
        self.qa_chain = None
        self.prompt_template = None
        self.campsite_metadata = {}
        
        logger.info("Initializing CampGPT RAG system...")
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize embedding and LLM models."""
        try:
            self.embeddings = GoogleGenerativeAIEmbeddings(
                model=self.embedding_model,
                google_api_key=self.api_key
            )
            logger.info(f"✓ Embeddings model initialized: {self.embedding_model}")
            
            self.llm = ChatGoogleGenerativeAI(
                model=self.llm_model,
                google_api_key=self.api_key,
                temperature=self.temperature
            )
            logger.info(f"✓ LLM model initialized: {self.llm_model}")
        except Exception as e:
            logger.error(f"Error initializing models: {e}")
            raise
    
    def ingest_json_data(self, json_file_path: str, chunk_size: int = 500, chunk_overlap: int = 100):
        """
        Ingest campsite data from JSON file and create vector embeddings.
        
        Args:
            json_file_path: Path to JSON file with campsite data (single object or array of campsites)
            chunk_size: Size of text chunks for embedding
            chunk_overlap: Overlap between chunks
        """
        try:
            # Load JSON data
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"Loading data from {json_file_path}", data)
            
            # Flatten JSON into documents
            documents = self._flatten_json_to_documents(data)
            logger.info(f"Extracted {len(documents)} document chunks from JSON")
            
            # Split text into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                separators=["\n\n", "\n", ". ", " ", ""]
            )
            
            split_docs = []
            for doc in documents:
                splits = text_splitter.split_text(doc.page_content)
                for split in splits:
                    split_docs.append(Document(
                        page_content=split,
                        metadata=doc.metadata
                    ))
            
            logger.info(f"Created {len(split_docs)} chunks for embedding")
            
            # Create vector store
            self.vectorstore = Chroma.from_documents(
                documents=split_docs,
                embedding=self.embeddings,
                persist_directory=self.chroma_persist_dir
            )
            self.vectorstore.persist()
            logger.info(f"✓ Vector store created and persisted to {self.chroma_persist_dir}")
            
            # Create QA chain
            self._create_qa_chain()
            
        except Exception as e:
            logger.error(f"Error ingesting JSON data: {e}")
            raise
    
    def _flatten_json_to_documents(self, data: Any, parent_key: str = "") -> List[Document]:
        """
        Recursively flatten JSON data into Document objects.
        
        Args:
            data: JSON data (dict, list of dicts, or scalar)
            parent_key: Parent key for metadata tracking
            
        Returns:
            List of Document objects with text content and metadata
        """
        documents = []
        
        # Handle array of campsites
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    documents.extend(self._flatten_json_to_documents(item, parent_key))
            return documents
        
        if isinstance(data, dict):
            # Extract campsite name and metadata
            campsite_name = data.get("name", "Unknown Campsite")
            campsite_id = data.get("id", "unknown_id")
            location = data.get("location", {})
            
            # Store campsite metadata
            self.campsite_metadata[campsite_id] = {
                "name": campsite_name,
                "location": location,
                "ingested_at": datetime.now().isoformat()
            }
            
            # Process each section of the campsite
            for key, value in data.items():
                if key in ["id", "name", "location"]:
                    continue
                
                section_key = f"{parent_key}/{key}" if parent_key else key
                
                if isinstance(value, dict):
                    # Convert dict to formatted text
                    text_content = self._dict_to_text(key, value, campsite_name)
                    documents.append(Document(
                        page_content=text_content,
                        metadata={
                            "campsite_name": campsite_name,
                            "campsite_id": campsite_id,
                            "section": key,
                            "source": "json"
                        }
                    ))
                
                elif isinstance(value, list):
                    # Convert list to formatted text
                    text_content = self._list_to_text(key, value, campsite_name)
                    documents.append(Document(
                        page_content=text_content,
                        metadata={
                            "campsite_name": campsite_name,
                            "campsite_id": campsite_id,
                            "section": key,
                            "source": "json"
                        }
                    ))
                
                elif isinstance(value, str):
                    # Add string values directly
                    documents.append(Document(
                        page_content=f"{key}: {value}",
                        metadata={
                            "campsite_name": campsite_name,
                            "campsite_id": campsite_id,
                            "section": key,
                            "source": "json"
                        }
                    ))
        
        return documents
    
    @staticmethod
    def _dict_to_text(section_name: str, data: dict, campsite_name: str) -> str:
        """Convert dictionary to formatted text for embedding."""
        lines = [f"\n{section_name.upper()} ({campsite_name}):"]
        
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                lines.append(f"  {key}: {json.dumps(value, indent=2)}")
            else:
                lines.append(f"  {key}: {value}")
        
        return "\n".join(lines)
    
    @staticmethod
    def _list_to_text(section_name: str, data: list, campsite_name: str) -> str:
        """Convert list to formatted text for embedding."""
        lines = [f"\n{section_name.upper()} ({campsite_name}):"]
        
        for idx, item in enumerate(data, 1):
            if isinstance(item, dict):
                lines.append(f"  {idx}. {json.dumps(item)}")
            else:
                lines.append(f"  {idx}. {item}")
        
        return "\n".join(lines)
    
    def _create_qa_chain(self):
        """Initialize the prompt template for QA chain."""
        prompt_template = """You are CampGPT, an expert camping advisor.

You have two sources of knowledge:
1. Campsite data provided in the context (primary and most reliable)
2. Weather information is also part of your knowledgebase

Guidelines:
- If the question is about the campsite, answer using ONLY the provided context.
- If the question is general (e.g., weather, travel tips, geography), you may use your general knowledge.
- If both are relevant, combine them.
- If you are unsure, clearly mention assumptions.

Always:
1. Provide helpful and actionable answers
2. Be conversational and user-friendly
3. Prefer context over general knowledge when available


Context from campsite data:
{context}

Question: {question}

Answer:"""
        
        self.prompt_template = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        logger.info("✓ Prompt template initialized successfully")
    
    def _create_qa_chain_with_filter(self, campsite_id: Optional[str] = None) -> RetrievalQA:
        """Create RetrievalQA chain with optional campsite_id filter.
        
        Args:
            campsite_id: Optional campsite ID to filter results. If None, retrieves from all campsites.
            
        Returns:
            RetrievalQA chain with the specified filter
        """
        # Build filter dictionary if campsite_id is provided
        search_kwargs = {"k": 5}
        if campsite_id:
            search_kwargs["filter"] = {"campsite_id": campsite_id}
        
        # Create retriever with optional filter
        retriever = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs=search_kwargs
        )
        
        # Create and return QA chain
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": self.prompt_template}
        )
        
        return qa_chain
    
    def query(self, question: str, campsite_id: Optional[str] = None, use_context: bool = "true") -> Dict[str, Any]:
        """
        Query the RAG system with a camping-related question.
        
        Args:
            question: User question about the campsite
            campsite_id: Optional campsite ID to filter results. If None, searches all campsites.
            use_context: Whether to return source documents
            
        Returns:
            Dictionary with answer and metadata
        """
        if not self.vectorstore or not self.prompt_template:
            raise ValueError("RAG system not initialized. Call ingest_json_data first.")
        
        try:
            logger.info(f"Processing query: {question}" + (f" for campsite: {campsite_id}" if campsite_id else " (all campsites)"))
            
            # Create QA chain with optional campsite filter
            qa_chain = self._create_qa_chain_with_filter(campsite_id)
            result = qa_chain.invoke({"query": question})
            
            response = {
                "answer": result.get("result", ""),
                "sources": [],
                "timestamp": datetime.now().isoformat(),
                "success": "true"
            }
            
            if use_context and "source_documents" in result:
                for doc in result["source_documents"]:
                    response["sources"].append({
                        "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                        "metadata": doc.metadata
                    })
            
            logger.info("Query processed successfully")
            return response
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                "answer": f"Error processing your question: {str(e)}",
                "sources": [],
                "timestamp": datetime.now().isoformat(),
                "success": "false"
            }
    
    def batch_query(self, questions: List[str], campsite_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Process multiple questions in batch.
        
        Args:
            questions: List of questions
            campsite_id: Optional campsite ID to filter results. If None, searches all campsites.
            
        Returns:
            List of response dictionaries
        """
        logger.info(f"Processing batch of {len(questions)} questions" + (f" for campsite: {campsite_id}" if campsite_id else " (all campsites)"))
        results = []
        
        for i, question in enumerate(questions, 1):
            logger.info(f"Processing question {i}/{len(questions)}")
            result = self.query(question, campsite_id=campsite_id)
            results.append(result)
        
        return results
    
    def get_campsite_info(self) -> Dict[str, Any]:
        """Get information about ingested campsites."""
        return {
            "campsites": self.campsite_metadata,
            "total_campsites": len(self.campsite_metadata),
            "vector_store_ready": self.vectorstore is not None,
            "model_info": {
                "embedding_model": self.embedding_model,
                "llm_model": self.llm_model,
                "temperature": self.temperature
            }
        }
    
    def delete_vectorstore(self):
        """Delete persisted vector store (for reset/cleanup)."""
        import shutil
        try:
            if os.path.exists(self.chroma_persist_dir):
                shutil.rmtree(self.chroma_persist_dir)
                logger.info(f"Deleted vector store at {self.chroma_persist_dir}")
        except Exception as e:
            logger.error(f"Error deleting vector store: {e}")


# Example usage and helper functions
def create_sample_campsite_json() -> str:
    """Create a sample campsite JSON file with array of campsites for testing."""
    sample_data = [
        {
            "id": "camp_001",
            "name": "Sunny Valley Campsite",
            "location": {
                "country": "Netherlands",
                "region": "Friesland",
                "coordinates": {
                    "latitude": 53.1234,
                    "longitude": 5.7890
                }
            },
            "facilities": {
                "toilets": {
                    "count": 12,
                    "wheelchair_accessible": "true",
                    "hot_showers": "true"
                },
                "water": {
                    "drinking_water": "true",
                    "gray_water_disposal": "true",
                    "tap_locations": 8
                },
                "electricity": {
                    "available": "true",
                    "amps": 16,
                    "connection_points": 45
                },
                "ev_charging": {
                    "available": "true",
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
                    "allowed": "true",
                    "restrictions": "Well-behaved pets only. Additional €5/night",
                    "dog_park": "true"
                },
                "vehicles": {
                    "max_height": "3.5m",
                    "max_length": "7.5m",
                    "electric_vehicles": "Encouraged with dedicated charging"
                }
            },
            "reviews": [
                {
                    "rating": 4.8,
                    "comment": "Excellent cleanliness. Staff very attentive to accessibility needs.",
                    "verified": "true"
                },
                {
                    "rating": 4.5,
                    "comment": "Food prices reasonable, but rides and slides cost extra.",
                    "verified": "true"
                },
                {
                    "rating": 4.9,
                    "comment": "Perfect for families with elderly members. Ramps everywhere.",
                    "verified": "true"
                },
                {
                    "rating": 4.7,
                    "comment": "I have observed wifi extra cost of 5€",
                    "date": "2024-02-20"
                }
            ],
            "accessibility": {
                "wheelchair_accessible_pitches": 8,
                "accessible_restaurants": "true",
                "accessible_toilets": "true",
                "ramps": "All main areas",
                "disabled_parking": 6
            },
            "amenities": {
                "restaurants": 2,
                "shops": 1,
                "swimming_pool": "true",
                "playground": "true",
                "wifi": "true"
            }
        },
        {
            "id": "camp_002",
            "name": "Forest Retreat Campsite",
            "location": {
                "country": "Netherlands",
                "region": "North Holland",
                "coordinates": {
                    "latitude": 52.5234,
                    "longitude": 5.2890
                }
            },
            "facilities": {
                "toilets": {
                    "count": 8,
                    "wheelchair_accessible": "true",
                    "hot_showers": "true"
                },
                "water": {
                    "drinking_water": "true",
                    "gray_water_disposal": "true",
                    "tap_locations": 6
                },
                "electricity": {
                    "available": "true",
                    "amps": 16,
                    "connection_points": 30
                },
                "ev_charging": {
                    "available": "false"
                }
            },
            "rules": {
                "quiet_hours": {
                    "start": "22:00",
                    "end": "08:00"
                },
                "pets": {
                    "allowed": "true",
                    "restrictions": "Dogs welcome",
                    "dog_park": "false"
                },
                "vehicles": {
                    "max_height": "3.5m",
                    "max_length": "7.5m"
                }
            },
            "reviews": [
                {
                    "rating": 4.6,
                    "comment": "Beautiful forest location. Great hiking trails nearby.",
                    "verified": "true"
                },
                {
                    "rating": 4.4,
                    "comment": "Peaceful and quiet, perfect for nature lovers.",
                    "verified": "true"
                }
            ],
            "accessibility": {
                "wheelchair_accessible_pitches": 4,
                "accessible_toilets": "true",
                "ramps": "Main areas only",
                "disabled_parking": 2
            },
            "amenities": {
                "restaurants": 1,
                "shops": 0,
                "swimming_pool": "false",
                "playground": "true",
                "wifi": "true"
            }
        }
    ]
    
    json_path = "/home/claude/sample_campsites.json"
    with open(json_path, 'w') as f:
        json.dump(sample_data, f, indent=2)
    
    logger.info(f"Sample JSON with {len(sample_data)} campsites created at {json_path}")
    return json_path


if __name__ == "__main__":
    # Demo usage
    print("=" * 80)
    print("CampGPT RAG System - Demo")
    print("=" * 80)
    
    # Create sample data
    json_path = create_sample_campsite_json()
    
    # Initialize RAG system
    rag = CampGPTRAG()
    
    # Ingest data
    rag.ingest_json_data(json_path)
    
    # Example queries - search across all campsites
    queries = [
        "Is this site safe for my 70-year-old father who uses a walker?",
        "Can we bring our electric car and charge it here?",
        "We have a dog. Is it allowed and what are the rules?",
        "What do guests say about extra costs?",
        "How many wheelchair-accessible pitches do you have?"
    ]
    
    print("\nProcessing queries across ALL campsites:")
    print("-" * 80)
    
    for query in queries:
        print(f"\nQ: {query}")
        response = rag.query(query)
        print(f"A: {response['answer']}")
        if response.get('sources'):
            print(f"Sources: {len(response['sources'])} document(s) used")
    
    # Example queries - specific campsite
    print("\n\n" + "=" * 80)
    print("Processing queries for SPECIFIC CAMPSITE (camp_001):")
    print("=" * 80)
    
    specific_queries = [
        "What facilities does this campsite have?",
        "Is there EV charging available?",
        "Are pets allowed?"
    ]
    
    for query in specific_queries:
        print(f"\nQ: {query}")
        response = rag.query(query, campsite_id="camp_001")
        print(f"A: {response['answer']}")
        if response.get('sources'):
            print(f"Sources: {len(response['sources'])} document(s) used")
