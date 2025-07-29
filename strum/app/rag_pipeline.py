import os
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import ollama

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
INDEX_FILE = os.path.join(BASE_DIR, "faiss_index.bin")
DOCS_FILE = os.path.join(BASE_DIR, "docs.npy")

# Load or create embeddings model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Opens every file that ends with .txt, and reads file as string into docs
def load_docs():
    docs = []
    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".txt"):
            with open(os.path.join(DATA_DIR, filename), "r", encoding="utf-8") as f:
                docs.append(f.read()) # reads entire contens of file as a string
    return docs

# Takes list of docs, creates a FAISS index, adds all embedding to the index
# saves the index and document for future use.
def build_vector_store(docs):
    embeddings = model.encode(docs, convert_to_numpy=True) # Turns each doc into a numerical vector to be analyzed later
    dim = embeddings.shape[1]                              # gets the length of each embedding vector
    index = faiss.IndexFlatL2(dim)                         # Creates a FAISS index to get vector similarity search 
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
def get_relevant_docs(query, index, docs, k=3):          # k is the number of top matches to return
    q_emb = model.encode([query], convert_to_numpy=True) # NumPy array of shape (1, embedding_dim) 1 doc and lenght of each embedding
    D, I = index.search(q_emb, k)                        # FAISS searches the index for most similar vectors
    return [docs[i] for i in I[0]]                       # D is distance of matches and I is the index of each match within docs

# Sends the user's query and the retrieved context to the Mistral LLM via Ollama
# Final step in the RAG pipeline
def query_mistral_with_context(query, context_docs):
    # Combine context and query for prompt
    context = "\n\n".join(context_docs)                                                        # join all relevant documents into one big string
    prompt = f"Use the following info to answer the question:\n{context}\n\nQuestion: {query}" # Creates the final prompt to send to the LLM
    response = ollama.chat(
        model="mistral",
        messages=[{"role": "user", "content": prompt}])                                                  # Gets the response back from the Mistral AI
    return response

# Combines everything for the RAG pipeline
def answer_query(query):
    index, docs = load_vector_store()                         # load an existing FAISS index and its associated documents from disk 
    if index is None or docs is None:                         # If one doesn't exist, create one
        print("Building vector store...")
        docs = load_docs()
        index, docs = build_vector_store(docs)
    relevant_docs = get_relevant_docs(query, index, docs)     # Grabs the top relevent documents from the docs based on the user query
    answer = query_mistral_with_context(query, relevant_docs) # Returns the answer after asking the LLM
    return answer
