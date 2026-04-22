# CampGPT - Intelligent Campsite Concierge

An AI-powered RAG (Retrieval-Augmented Generation) system that transforms static campsite data into a live expert chatbot, providing instant, hyper-personalized travel advice.

## 🌟 Features

✅ **RAG-Based Intelligence**: Uses semantic search + large language models for context-aware responses
✅ **JSON Data Processing**: Automatically extracts and indexes campsite information
✅ **Multi-Lingual Support**: Query in English, Dutch, German, French, Italian, etc.
✅ **Zero-Cost Scaling**: Free tier APIs (Google Gemini, Embeddings)
✅ **Production-Ready**: Proper error handling, logging, and caching
✅ **Web Interface**: Interactive Streamlit UI for non-developers
✅ **Batch Processing**: Handle multiple queries efficiently
✅ **Metadata Tracking**: Know which data sources support each response

---

## 🏗️ Architecture

```
User Question
     ↓
[Semantic Search] ← Vector Database (Chroma)
     ↓
[Context Retrieval] ← Embeddings (Google)
     ↓
[LLM Processing] → Gemini 1.5 Flash
     ↓
Hyper-Personalized Answer + Sources
```

### Tech Stack

| Component | Technology | Cost |
|-----------|-----------|------|
| **Embedding Model** | Google `text-embedding-004` | Free |
| **LLM** | Gemini 1.5 Flash | Free tier |
| **Vector Database** | ChromaDB (Local) | Free |
| **Orchestration** | LangChain | Free |
| **UI Framework** | Streamlit | Free |

---

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or download the project
cd campgpt

# Install dependencies
pip install -r requirements.txt

# Set up your Google API key
export GOOGLE_API_KEY="your-api-key-here"
```

### 2. Get Google API Key (Free)

1. Visit https://ai.google.dev/
2. Click "Get API Key"
3. Create a new API key
4. Copy and use it

### 3. Prepare Your Data

Create a JSON file with campsite information:

```json
{
  "id": "camp_001",
  "name": "Sunny Valley Campsite",
  "location": {
    "country": "Netherlands",
    "region": "Friesland"
  },
  "facilities": {
    "ev_charging": {
      "available": true,
      "charging_points": 3
    },
    "accessibility": {
      "wheelchair_accessible_pitches": 8
    }
  },
  "reviews": [
    {
      "rating": 4.8,
      "comment": "Excellent cleanliness, very accessible!"
    }
  ]
}
```

### 4. Run the System

#### Option A: Python API (Programmatic)

```python
from campgpt_rag import CampGPTRAG

# Initialize
rag = CampGPTRAG(google_api_key="your-api-key")

# Ingest data
rag.ingest_json_data("sample_campsites.json")

# Ask a question
response = rag.query("Can we bring our electric car?")
print(response['answer'])
```

#### Option B: Web Interface (Streamlit)

```bash
streamlit run streamlit_app.py
```

Then open http://localhost:8501 in your browser.

---

## 📖 Detailed Documentation

### Class: `CampGPTRAG`

#### Initialization

```python
rag = CampGPTRAG(
    google_api_key="your-key",           # Required
    embedding_model="models/embedding-001",
    llm_model="gemini-1.5-flash",
    chroma_persist_dir="./chroma_db",
    temperature=0.7
)
```

**Parameters:**
- `google_api_key`: Your Google API key (or use `GOOGLE_API_KEY` env var)
- `embedding_model`: Google embedding model to use
- `llm_model`: Gemini model variant
- `chroma_persist_dir`: Where to store vector DB locally
- `temperature`: LLM creativity (0=deterministic, 1=creative)

#### Methods

##### `ingest_json_data(json_file_path, chunk_size=500, chunk_overlap=100)`

Load and index campsite data.

```python
rag.ingest_json_data(
    "campsites.json",
    chunk_size=500,      # Size of text chunks
    chunk_overlap=100    # Overlap between chunks
)
```

##### `query(question, use_context=True)`

Ask a single question.

```python
response = rag.query("Is the campsite accessible for wheelchairs?")

# Response structure:
{
    "answer": "Yes, the campsite has 8 wheelchair-accessible pitches...",
    "sources": [
        {
            "content": "ACCESSIBILITY (Sunny Valley): ...",
            "metadata": {
                "campsite_name": "Sunny Valley",
                "section": "accessibility"
            }
        }
    ],
    "timestamp": "2024-03-15T10:30:00",
    "success": True
}
```

##### `batch_query(questions)`

Process multiple questions efficiently.

```python
questions = [
    "Can we bring a dog?",
    "What's the EV charging speed?",
    "Are there accessible toilets?"
]

responses = rag.batch_query(questions)

for q, r in zip(questions, responses):
    print(f"{q}\n→ {r['answer']}\n")
```

##### `get_campsite_info()`

Get metadata about ingested data.

```python
info = rag.get_campsite_info()
# {
#     "campsites": {...},
#     "total_campsites": 4,
#     "vector_store_ready": True,
#     "model_info": {...}
# }
```

---

## 📊 JSON Data Structure Guide

### Recommended Structure

```json
{
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
      "wheelchair_accessible": true,
      "hot_showers": true
    },
    "electricity": {
      "available": true,
      "amps": 16,
      "connection_points": 45
    },
    "ev_charging": {
      "available": true,
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
      "allowed": true,
      "restrictions": "€5/night"
    }
  },
  "reviews": [
    {
      "rating": 4.8,
      "comment": "Excellent cleanliness!",
      "verified": true
    }
  ],
  "accessibility": {
    "wheelchair_accessible_pitches": 8,
    "accessible_toilets": true,
    "ramps": "All main areas"
  },
  "amenities": {
    "restaurants": 2,
    "wifi": true,
    "pool": true
  }
}
```

### Key Recommendations

✓ Use consistent key naming (snake_case)
✓ Include detailed facility information
✓ Add guest reviews for sentiment analysis
✓ Be specific about accessibility features
✓ Include pricing and extra costs
✓ Add location coordinates (future vision features)

---

## 💼 Use Cases

### Use Case 1: Multi-Generational Filter

**Scenario**: Family with elderly members who need accessibility

```python
question = """
I'm traveling with 5 people, including one person over 70 with a walker.
Is this a good fit?
"""
response = rag.query(question)
```

**What it retrieves:**
- Wheelchair-accessible pitches
- Accessible toilets and showers
- Guest reviews mentioning accessibility
- Ramp locations
- Disabled parking

---

### Use Case 2: Logistic Planning

**Scenario**: Traveling with electric vehicle

```python
questions = [
    "Can we charge our Tesla there?",
    "What's the charging speed?",
    "Are there restrictions on vehicle height?"
]
responses = rag.batch_query(questions)
```

**What it retrieves:**
- EV charging availability
- Charging speeds and connector types
- Vehicle size restrictions
- Parking availability
- Electrical amps available

---

### Use Case 3: Real-World Sentiment

**Scenario**: Understanding guest experiences

```python
question = "What do people say about extra costs?"
response = rag.query(question)
```

**What it retrieves:**
- Guest reviews mentioning prices
- Hidden costs mentioned by reviews
- Value for money sentiment
- Specific activity costs
- Overall satisfaction ratings

---

## 🎯 Integration Examples

### Flask Integration

```python
from flask import Flask, request
from campgpt_rag import CampGPTRAG

app = Flask(__name__)
rag = CampGPTRAG()
rag.ingest_json_data("campsites.json")

@app.route('/ask', methods=['POST'])
def ask():
    question = request.json.get('question')
    response = rag.query(question)
    return response
```

### FastAPI Integration

```python
from fastapi import FastAPI
from pydantic import BaseModel
from campgpt_rag import CampGPTRAG

app = FastAPI()
rag = CampGPTRAG()
rag.ingest_json_data("campsites.json")

class Question(BaseModel):
    text: str

@app.post("/ask")
def ask(q: Question):
    return rag.query(q.text)
```

### Slack Bot Integration

```python
from slack_bolt import App
from campgpt_rag import CampGPTRAG

app = App(token=os.environ["SLACK_BOT_TOKEN"])
rag = CampGPTRAG()
rag.ingest_json_data("campsites.json")

@app.message("camping")
def handle_camping_questions(message, say):
    response = rag.query(message['text'])
    say(response['answer'])
```

---

## 💰 Cost Analysis

### Free Tier (Unlimited)

| Service | Pricing | Usage |
|---------|---------|-------|
| Gemini 1.5 Flash | Free (15 requests/min) | LLM responses |
| Google Embeddings | Free | Text vectorization |
| ChromaDB | Free (Local) | Vector storage |
| LangChain | Free | Orchestration |
| Streamlit | Free | Web hosting option |

### Scaling Costs (if needed)

- **Gemini 1.5 Flash API**: ~$0.075/1M input tokens
- **Pinecone Vector DB**: $0-300/month (if Chroma insufficient)
- **Cloud Hosting**: $5-50/month

---

## 🔧 Advanced Configuration

### Tuning for Different Use Cases

#### For Factual Queries (Hotel Accessibility)
```python
rag = CampGPTRAG(
    temperature=0.3,        # Lower = more deterministic
    llm_model="gemini-1.5-flash"
)
```

#### For Creative Recommendations
```python
rag = CampGPTRAG(
    temperature=0.9,        # Higher = more creative
    llm_model="gemini-1.5-flash"
)
```

#### For Larger Datasets
```python
rag = CampGPTRAG()
rag.ingest_json_data(
    "large_campsites.json",
    chunk_size=300,         # Smaller chunks
    chunk_overlap=50        # Less overlap = faster
)
```

---

## 📊 Retrieval Configuration

Adjust retrieval in `_create_qa_chain()`:

```python
retriever=self.vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 5}  # Number of chunks to retrieve
)
```

**Tuning guidance:**
- `k=3`: Fast, for simple questions
- `k=5`: Balanced (default)
- `k=10`: Thorough, for complex questions

---

## 🐛 Troubleshooting

### Issue: "API Key not found"

**Solution:**
```bash
export GOOGLE_API_KEY="your-key-here"
# Or pass it directly
rag = CampGPTRAG(google_api_key="your-key")
```

### Issue: "No response from LLM"

**Solution:**
- Check API key is valid
- Check rate limits (15 requests/min free tier)
- Try again after 1 minute

### Issue: "Vector store not found"

**Solution:**
```python
# Delete and reinitialize
rag.delete_vectorstore()
rag.ingest_json_data("campsites.json")
```

### Issue: "Slow responses"

**Solution:**
- Reduce `k` in retrieval settings
- Use smaller `chunk_size`
- Use Pinecone instead of Chroma (if needed)

---

## 📈 Performance Metrics

Typical performance on Gemini 1.5 Flash:

| Metric | Value |
|--------|-------|
| Query latency | 2-5 seconds |
| Throughput | 15 requests/min (free tier) |
| Context window | Up to 1M tokens |
| Embedding speed | 500+ embeddings/sec |
| Vector retrieval | <100ms for k=5 |

---

## 🚀 Deployment Guide

### Local Development

```bash
python streamlit_app.py
```

### Production Deployment

#### Option 1: Streamlit Cloud

```bash
# Create requirements.txt (already done)
git push to GitHub
# Deploy from Streamlit Cloud dashboard
```

#### Option 2: Docker

```dockerfile
FROM python:3.10
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
ENV GOOGLE_API_KEY=$GOOGLE_API_KEY
CMD ["streamlit", "run", "streamlit_app.py"]
```

```bash
docker build -t campgpt .
docker run -e GOOGLE_API_KEY="..." -p 8501:8501 campgpt
```

#### Option 3: AWS Lambda (API)

```python
import json
from campgpt_rag import CampGPTRAG

rag = CampGPTRAG()
rag.ingest_json_data("campsites.json")

def lambda_handler(event, context):
    question = json.loads(event['body'])['question']
    response = rag.query(question)
    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }
```

---

## 📚 File Structure

```
campgpt/
├── campgpt_rag.py           # Main RAG system
├── streamlit_app.py         # Web interface
├── examples.py              # Example usage
├── requirements.txt         # Dependencies
├── sample_campsites.json    # Example data
├── README.md                # This file
└── chroma_db/              # Vector store (auto-created)
```

---

## 🔐 Security Best Practices

✓ Use environment variables for API keys
✓ Validate and sanitize user inputs
✓ Implement rate limiting on public endpoints
✓ Use HTTPS for all communications
✓ Regular security audits
✓ Log and monitor API usage

---

## 🎓 Learning Resources

- **LangChain**: https://python.langchain.com/
- **Gemini API**: https://ai.google.dev/
- **ChromaDB**: https://www.trychroma.com/
- **RAG Concepts**: https://arxiv.org/abs/2005.11401

---

## 📝 License

MIT License - Feel free to use this project!

---

## 🤝 Contributing

Found a bug or want to improve? Please open an issue or submit a PR!

---

## 📧 Support

For questions or issues:
1. Check troubleshooting section
2. Review example code
3. Check LangChain/Gemini documentation

---

## 🎉 Future Roadmap

- [ ] Vision RAG: Upload photo of tent/car, AI matches it to pitches
- [ ] Multi-lingual interface
- [ ] Booking integration
- [ ] Real-time availability checking
- [ ] Recommendation engine
- [ ] Mobile app
- [ ] Voice query support

---

**Happy camping! 🏕️**
