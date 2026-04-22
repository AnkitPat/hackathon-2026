"""
CampGPT Streamlit Web Interface
Interactive chatbot for camping trip planning using RAG
"""

import streamlit as st
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

# Import RAG system
from campgpt_rag import CampGPTRAG, create_sample_campsite_json

# Page configuration
st.set_page_config(
    page_title="CampGPT - Campsite Concierge",
    page_icon="🏕️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-title {
        color: #2E7D32;
        text-align: center;
        margin-bottom: 10px;
    }
    .subtitle {
        color: #558B2F;
        text-align: center;
        font-size: 18px;
        margin-bottom: 20px;
    }
    .response-box {
        background-color: #F1F8E9;
        border-left: 5px solid #4CAF50;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .source-box {
        background-color: #E8F5E9;
        border-left: 5px solid #81C784;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
        font-size: 12px;
    }
    .status-box {
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .status-ready {
        background-color: #C8E6C9;
        color: #1B5E20;
    }
    .status-error {
        background-color: #FFCDD2;
        color: #B71C1C;
    }
    .query-input {
        border: 2px solid #4CAF50;
        border-radius: 5px;
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def initialize_rag(google_api_key: str, json_file_path: str) -> Optional[CampGPTRAG]:
    """Initialize RAG system (cached to avoid re-initialization)."""
    try:
        # Set environment variable if API key provided
        if google_api_key:
            os.environ["GOOGLE_API_KEY"] = google_api_key
        
        rag = CampGPTRAG(google_api_key=google_api_key)
        
        # Check if file exists
        if not os.path.exists(json_file_path):
            st.warning(f"JSON file not found at {json_file_path}")
            return None
        
        # Ingest data
        with st.spinner("📚 Ingesting campsite data..."):
            rag.ingest_json_data(json_file_path)
        
        return rag
    except Exception as e:
        st.error(f"Error initializing RAG system: {str(e)}")
        return None


def reset_cache():
    """Reset session cache."""
    st.cache_resource.clear()
    if 'rag_system' in st.session_state:
        del st.session_state.rag_system
    if 'chat_history' in st.session_state:
        del st.session_state.chat_history
    st.success("Cache cleared!")


def main():
    # Title section
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 class='main-title'>🏕️ CampGPT</h1>", unsafe_allow_html=True)
        st.markdown("<p class='subtitle'>Your Intelligent Campsite Concierge</p>", unsafe_allow_html=True)
    
    # Sidebar configuration
    with st.sidebar:
        st.markdown("## ⚙️ Configuration")
        
        # API Key input
        api_key = st.text_input(
            "Google API Key",
            type="password",
            help="Get your free API key from https://ai.google.dev/"
        )
        
        # File upload or selection
        st.markdown("### 📂 Data Source")
        
        data_source = st.radio(
            "Choose data source:",
            ["Upload JSON File", "Use Sample Data"]
        )
        
        json_file_path = None
        
        if data_source == "Upload JSON File":
            uploaded_file = st.file_uploader(
                "Upload campsite JSON file",
                type=['json'],
                help="Upload a JSON file with campsite information"
            )
            
            if uploaded_file:
                # Save uploaded file temporarily
                json_file_path = f"/tmp/{uploaded_file.name}"
                with open(json_file_path, 'wb') as f:
                    f.write(uploaded_file.getbuffer())
                st.success(f"✓ File uploaded: {uploaded_file.name}")
        else:
            # Create and use sample data
            json_file_path = create_sample_campsite_json()
            st.info("✓ Using sample campsite data")
        
        # Initialize button
        if st.button("🚀 Initialize CampGPT", use_container_width=True, type="primary"):
            if not api_key:
                st.error("❌ Please provide your Google API Key")
            elif not json_file_path:
                st.error("❌ Please upload or select a JSON file")
            else:
                st.session_state.rag_system = initialize_rag(api_key, json_file_path)
                st.session_state.chat_history = []
                st.success("✓ CampGPT initialized successfully!")
        
        # Reset button
        if st.button("🔄 Reset System", use_container_width=True):
            reset_cache()
        
        # System info
        st.markdown("### 📊 System Status")
        if 'rag_system' in st.session_state and st.session_state.rag_system:
            rag = st.session_state.rag_system
            info = rag.get_campsite_info()
            
            st.markdown(
                f"<div class='status-box status-ready'>"
                f"<b>Status:</b> ✓ Ready<br>"
                f"<b>Campsites:</b> {info['total_campsites']}<br>"
                f"<b>Model:</b> {info['model_info']['llm_model']}<br>"
                f"<b>Embedding:</b> {info['model_info']['embedding_model']}"
                f"</div>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                "<div class='status-box status-error'>"
                "<b>Status:</b> ⚠️ Not Initialized<br>"
                "Configure and click 'Initialize CampGPT' to begin"
                "</div>",
                unsafe_allow_html=True
            )
    
    # Main content area
    if 'rag_system' not in st.session_state or not st.session_state.rag_system:
        st.info("👈 Configure the system in the sidebar to get started!")
        
        # Show example queries
        st.markdown("### 💡 Example Questions")
        examples = [
            "Is this site safe for my 70-year-old father who uses a walker?",
            "Can we charge our electric car there?",
            "Is dog-friendly and what are the rules?",
            "What do people say about extra costs?",
            "How many wheelchair-accessible pitches do you have?",
            "What are the quiet hours?"
        ]
        
        for example in examples:
            st.markdown(f"• {example}")
    else:
        rag = st.session_state.rag_system
        
        # Chat interface
        st.markdown("### 🎯 Ask Your Camping Questions")
        
        # Display chat history
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        
        # Chat display area
        chat_container = st.container()
        
        with chat_container:
            for i, message in enumerate(st.session_state.chat_history):
                if message['role'] == 'user':
                    st.markdown(f"**You:** {message['content']}")
                else:
                    st.markdown(f"<div class='response-box'><b>🤖 CampGPT:</b> {message['content']}</div>", unsafe_allow_html=True)
                    if 'sources' in message and message['sources']:
                        with st.expander(f"📚 Sources ({len(message['sources'])})"):
                            for j, source in enumerate(message['sources'], 1):
                                st.markdown(f"<div class='source-box'><b>Source {j}:</b> {source['content']}<br><i>{source['metadata']['campsite_name']} - {source['metadata']['section']}</i></div>", unsafe_allow_html=True)
        
        # Query input
        st.markdown("---")
        
        col1, col2 = st.columns([4, 1])
        
        with col1:
            user_input = st.text_input(
                "Your question:",
                placeholder="E.g., Can we bring our electric car?",
                label_visibility="collapsed"
            )
        
        with col2:
            submit_button = st.button("📤 Send", use_container_width=True, type="primary")
        
        # Process query
        if submit_button and user_input.strip():
            # Add user message to history
            st.session_state.chat_history.append({
                'role': 'user',
                'content': user_input
            })
            
            # Get response
            with st.spinner("🤔 Thinking..."):
                response = rag.query(user_input)
            
            # Add assistant response to history
            message_data = {
                'role': 'assistant',
                'content': response['answer']
            }
            
            if response.get('sources'):
                message_data['sources'] = response['sources']
            
            st.session_state.chat_history.append(message_data)
            st.rerun()
        
        # Quick actions
        st.markdown("---")
        st.markdown("### ⚡ Quick Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔧 Show System Info", use_container_width=True):
                info = rag.get_campsite_info()
                st.json(info)
        
        with col2:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()
        
        with col3:
            if st.button("📋 Example Queries", use_container_width=True):
                st.session_state.show_examples = not st.session_state.get('show_examples', False)
        
        if st.session_state.get('show_examples', False):
            st.markdown("### 💡 Suggested Questions")
            examples = [
                "Is this site safe for elderly visitors with mobility issues?",
                "What electric vehicle charging options are available?",
                "Are pets allowed? What are the restrictions?",
                "What do reviews say about cleanliness?",
                "What are the accessibility features?",
                "How does the wifi work?",
                "What are the facility operating hours?"
            ]
            
            for example in examples:
                if st.button(example, use_container_width=True, key=f"example_{example}"):
                    st.session_state.chat_history.append({
                        'role': 'user',
                        'content': example
                    })
                    
                    with st.spinner("🤔 Thinking..."):
                        response = rag.query(example)
                    
                    message_data = {
                        'role': 'assistant',
                        'content': response['answer']
                    }
                    
                    if response.get('sources'):
                        message_data['sources'] = response['sources']
                    
                    st.session_state.chat_history.append(message_data)
                    st.rerun()


if __name__ == "__main__":
    # Initialize session state
    if 'rag_system' not in st.session_state:
        st.session_state.rag_system = None
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    main()

