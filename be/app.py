from fastapi import FastAPI
from pydantic import BaseModel
import os
from campgpt_rag import CampGPTRAG
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows all origins
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods (GET, POST, etc.)
    allow_headers=["*"], # Allows all headers
)
# ✅ Global RAG instance (IMPORTANT)
rag = None


# Request schema
class QueryRequest(BaseModel):
    question: str


@app.on_event("startup")
def startup_event():
    global rag

    print("🚀 Initializing RAG system...")

    rag = CampGPTRAG(
        # google_api_key=os.getenv("GOOGLE_API_KEY"),
        # embedding_model="models/text-embedding-004",
        # llm_model="gemini-1.5-flash"  # or your working one
    )

    # Ingest once
    rag.ingest_json_data("sample_campsites.json")

    print("✅ RAG ready!")


@app.get("/")
def health():
    return {"status": "ok"}


@app.post("/query")
def query_rag(request: QueryRequest):
    global rag

    result = rag.query(request.question)

    return {
        "answer": result["answer"],
        "sources": result.get("sources", [])
    }