import asyncio
import os
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import ollama

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # goes up one (/app)
DATA_DIR = os.path.join(BASE_DIR, "data")
INDEX_FILE = os.path.join(BASE_DIR, "faiss_index.bin")
DOCS_FILE = os.path.join(BASE_DIR, "docs.npy")

# Load or create embeddings model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Will split the documents into smaller pieces to be vectrorized and indexed
def split_text(text, chunk_size=750, overlap=100):
    # chunk_size is max number of chars per chunk
    # overlap is how many chars from previous chunk appear at start of next chunk
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size-overlap  # Move start forward by chunk_size - overlap
    return chunks

# Opens every file that ends with .txt, and reads file as string into docs
def load_docs():
    docs = []
    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".txt"):
            with open(os.path.join(DATA_DIR, filename), "r", encoding="utf-8") as f:
                text = f.read()
                chunks = split_text(text) # split documents into smaller pieces
                docs.extend(chunks)       # add all chunks individually to the docs list
    return docs

# Takes list of docs, creates a FAISS index, adds all embedding to the index
# saves the index and document for future use.
def build_vector_store(docs):
    embeddings = model.encode(docs, convert_to_numpy=True) # Turns each doc into a numerical vector to be analyzed later
    dim = embeddings.shape[1]                              # gets the length of each embedding vector
    index = faiss.IndexHNSWFlat(dim, 32)                   # Creates a FAISS index to get vector similarity search 
    index.add(embeddings)                                  # adds all document embeddings into the FAISS index
    # Save index and docs for reuse
    faiss.write_index(index, INDEX_FILE)
    np.save(DOCS_FILE, docs)
    return index, docs

# Checks if the saved index and doc exist
# returns them if available
def load_vector_store():
    if os.path.exists(INDEX_FILE) and os.path.exists(DOCS_FILE):
        index = faiss.read_index(INDEX_FILE)
        docs = np.load(DOCS_FILE, allow_pickle=True)
        return index, docs.tolist()
    return None, None

# Takes a user query and encodes it
# searches the FAISS index for the kth closest document
# returns the document texts
def get_relevant_docs(query, index, docs, k=2):          # k is the number of top matches to return
    q_emb = model.encode([query], convert_to_numpy=True) # NumPy array of shape (1, embedding_dim) 1 doc and length of each embedding
    D, I = index.search(q_emb, k)                        # FAISS searches the index for most similar vectors
    return [docs[i] for i in I[0]]                       # D is distance of matches and I is the index of each match within docs

# Sends the user's query and the retrieved context to the Mistral LLM via Ollama
# Final step in the RAG pipeline
def query_mistral_with_context(query, context_docs, conversation_history=None):
    if conversation_history is None:
        conversation_history = []

    # Combine context and query for prompt
    context = "\n\n".join(context_docs) # join all relevant documents into one big string
    system_message = f"""Use the following info to answer the question:
    {context}
    Do not mention that I gave you context."""

    # Start building the message chain with context at the top
    # context will change from message to message, but chat history will
    # stay the same
    messages = [{"role": "system", "content": system_message}]

    # Only add this if you want conversation history, but it bloats the tokens for Mistral
    # Add conversation history next
    # for message in conversation_history:
    #     messages.append({"role": "user", "content": message.question})
    #     messages.append({"role": "assistant", "content": message.answer})
    #------------------------------------------------------------------------------

    # Finally add most recent query at the bottom
    messages.append({"role": "user", "content": query})
    
    # Gets the response back from the Mistral AI
    try:
        response = ollama.chat(
            model="llama3.1:8b",
            messages=messages)

    except Exception as e:
        print(f"Error querying Llama: {e}")
        return {"error": str(e)}

    return response

# Combines everything for the RAG pipeline
# def answer_query(query, conversation_history=None):
#     # This is done on startup instead
#     # index, docs = load_vector_store()                     # load an existing FAISS index and its associated documents from disk 
#     # if index is None or docs is None:                     # If one doesn't exist, create one
#     #     print("Building vector store...")
#     #     docs = load_docs()
#     #     index, docs = build_vector_store(docs)
#     relevant_docs = get_relevant_docs(query, index, docs) # Grabs the top relevent documents from the docs based on the user query
#     answer = query_mistral_with_context(query, relevant_docs, conversation_history) # Returns the answer after asking the LLM
#     return answer

# Run server to talk to backend TSOA

from fastapi import FastAPI, HTTPException # Web framework for building APIs
from pydantic import BaseModel           # Defines request and Response models
from typing import List, Optional # Defines types
import uvicorn                           # Runs Server

app = FastAPI()

class HistoryItem(BaseModel):
    question: str
    answer: str

class QueryRequest(BaseModel):
    message: str # User query message
    history: Optional[List[HistoryItem]] = None # If on first message there is no history, set None

class QueryResponse(BaseModel):
    response: str # Response from the LLM
    history: List[HistoryItem] # Updated chat history

# Load these are globals to stop them from searching on every query
index, docs = load_vector_store()  # global variables

# load on startup to prevent it from searching memory over and over 
@app.on_event("startup")
def startup_event():
    global index, docs # define these here so that they can be used above
    if index is None or docs is None:
        docs = load_docs()
        index, docs = build_vector_store(docs)

# Define endpoint
@app.post("/query", response_model=QueryResponse) # defines POST at query endpoint
async def query_rag(data: QueryRequest):
    try:
        relevant_docs = get_relevant_docs(data.message, index, docs)
        result = await asyncio.to_thread(query_mistral_with_context, data.message, relevant_docs)
        # result = answer_query(data.message, data.history) # function called
        return {
            "response": result['message']['content'],
            "history": (data.history or []) + [HistoryItem(question=data.message, answer=result['message']['content'])]
        }
    except HTTPException as e: # Future proof in case I want to add more specific error handling
        raise                  # if I get a 400, it will just kick that back, not make it a 500
    except Exception as e:     # Catch all for everything else, making them 500 errors
        print(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# This is only for local development; Docker CMD will run this when launched through Docker
if __name__ == "__main__":
    uvicorn.run("rag_pipeline:app", host="0.0.0.0", port=8000, reload=True) # Runs the FastAPI app