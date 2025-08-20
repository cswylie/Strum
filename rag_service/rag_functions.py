import os
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import ollama

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
INDEX_FILE = os.path.join(BASE_DIR, "faiss_index.bin")
DOCS_FILE = os.path.join(BASE_DIR, "docs.npy")

# Load or create embeddings model
model = SentenceTransformer('all-MiniLM-L6-v2')

def split_text(text, chunk_size=750, overlap=100):
    """Split the documents into smaller pieces to be vectorized and indexed"""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

def load_docs():
    """Opens every file that ends with .txt, and reads file as string into docs"""
    docs = []
    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".txt"):
            with open(os.path.join(DATA_DIR, filename), "r", encoding="utf-8") as f:
                text = f.read()
                chunks = split_text(text)
                docs.extend(chunks)
    return docs

def build_vector_store(docs):
    """Takes list of docs, creates a FAISS index, adds all embeddings to the index"""
    embeddings = model.encode(docs, convert_to_numpy=True)
    dim = embeddings.shape[1]
    index = faiss.IndexHNSWFlat(dim, 32)
    index.add(embeddings)
    
    # Save index and docs for reuse
    faiss.write_index(index, INDEX_FILE)
    np.save(DOCS_FILE, docs)
    return index, docs

def load_vector_store():
    """Checks if the saved index and docs exist, returns them if available"""
    if os.path.exists(INDEX_FILE) and os.path.exists(DOCS_FILE):
        index = faiss.read_index(INDEX_FILE)
        docs = np.load(DOCS_FILE, allow_pickle=True)
        return index, docs.tolist()
    return None, None

def get_relevant_docs(query, index, docs, k=2):
    """Takes a user query and searches the FAISS index for the k closest documents"""
    q_emb = model.encode([query], convert_to_numpy=True)
    D, I = index.search(q_emb, k)
    return [docs[i] for i in I[0]]

def query_llm_with_context(query, context_docs, conversation_history=None):
    """Sends the user's query and retrieved context to the LLM via Ollama"""
    if conversation_history is None:
        conversation_history = []

    # Combine context and query for prompt
    context = "\n\n".join(context_docs)
    system_message = f"""Use the following info to answer the question:
    {context}
    Do not mention that I gave you context."""

    messages = [{"role": "system", "content": system_message}]
    messages.append({"role": "user", "content": query})
    
    try:
        response = ollama.chat(
            model="llama3.1:8b",
            messages=messages
        )
        return response
    except Exception as e:
        print(f"Error querying Llama: {e}")
        return {"error": str(e)}

def initialize_vector_store():
    """Initialize the vector store on startup"""
    index, docs = load_vector_store()
    if index is None or docs is None:
        print("Building vector store...")
        docs = load_docs()
        index, docs = build_vector_store(docs)
    return index, docs