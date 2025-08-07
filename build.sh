#!/bin/bash

# Optional: Stop any running container named 'strum_container'
# docker stop strum_container 2>/dev/null && docker rm strum_container 2>/dev/null

# Build the Docker image
echo "🔨 Building Docker image..."
docker build -t strum .

# Run the container
echo "🚀 Running container..."
docker run --gpus all \
  --name strum_container \
  -e GRADIO_HOST=0.0.0.0 \
  -e GRADIO_PORT=7860 \
  -p 7860:7860 \
  strum
