FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git curl build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Set Ollama model directory to persistent volume
ENV OLLAMA_MODELS=/app/data/ollama-models

# Copy requirements and install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create data directory for persistent volume
RUN mkdir -p /app/data/ollama-models

# Expose port
EXPOSE 8000

# Railway will automatically set the PORT environment variable
# Start Ollama in background, pull model, then start FastAPI
CMD ["sh", "-c", "ollama serve & sleep 5 && ollama pull llama3.1:8b && uvicorn api_server:app --host 0.0.0.0 --port ${PORT:-8000}"]