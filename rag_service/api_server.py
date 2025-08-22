import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

from rag_functions import initialize_vector_store, get_relevant_docs, query_llm_with_context

app = FastAPI()

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173",
                   "https://christianswylie.com",
                   "http://localhost:7860"], # vite frontend
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["Content-Type"],
)

class HistoryItem(BaseModel):
    question: str
    answer: str

class QueryRequest(BaseModel):
    message: str
    history: Optional[List[HistoryItem]] = None

class QueryResponse(BaseModel):
    response: str
    history: List[HistoryItem]

# Global variables for vector store
index = None
docs = None

@app.on_event("startup")
async def startup_event():
    """Initialize vector store on startup"""
    global index, docs
    index, docs = initialize_vector_store()

@app.post("/query", response_model=QueryResponse)
async def query_rag(data: QueryRequest):
    try:
        relevant_docs = get_relevant_docs(data.message, index, docs)
        result = await asyncio.to_thread(query_llm_with_context, data.message, relevant_docs)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return QueryResponse(
            response=result,
            history=(data.history or []) + [HistoryItem(
                question=data.message, 
                answer=result
            )]
        )
    except HTTPException as e:
        raise
    except Exception as e:
        print(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=True)