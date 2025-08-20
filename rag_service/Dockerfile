FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git curl build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Set Ollama model directory
ENV OLLAMA_MODELS=/app/ollama-models

# Copy requirements and install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Expose ports
EXPOSE 8000

# Start Ollama in background + your app
# Start Ollama server and app at runtime
# Also runs FastAPI
# Use an entrypoint script to start both Ollama and FastAPI
CMD ["sh", "-c", "ollama serve & sleep 5 && ollama pull llama3.1:8b && uvicorn rag_pipeline:app --host 0.0.0.0 --port 8000"]
