# Use a lightweight Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies (git, FAISS build tools, curl for Ollama)
RUN apt-get update && apt-get install -y \
    git build-essential curl \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Optional: set Ollama model directory
ENV OLLAMA_MODELS=/app/ollama-models

# Copy requirements and install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project
COPY . .

# Expose ports: Gradio (7860) + Ollama API (11434)
EXPOSE 7860 11434

# Start Ollama in background + your app
# Start Ollama server and app at runtime
CMD ollama serve & \
    sleep 5 && \
    ollama pull mistral && \
    python strum/app/ui.py
