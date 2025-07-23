#!/bin/bash
set -e

# Offline installer for RAG Chatbot

# 1. Create Python venv
python3 -m venv .venv
source .venv/bin/activate

# 2. Install Python dependencies
pip install --no-cache-dir --find-links=./wheels -r requirements.txt || pip install -r requirements.txt

# 3. Start Qdrant (Docker required)
echo "Starting Qdrant via Docker..."
docker run -d --name qdrant_rag -p 6333:6333 -v $(pwd)/docs_index:/qdrant/storage qdrant/qdrant

echo "\n---"
echo "Download GGUF LLMs manually from HuggingFace and place in ./models/"
echo "Recommended: Phi-3-mini-4k-instruct-q4.gguf or Mistral-7B-Instruct-v0.2.Q4_K_M.gguf"
echo "---"
echo "Setup complete. Activate venv with: source .venv/bin/activate"
echo "To stop Qdrant: docker stop qdrant_rag && docker rm qdrant_rag"

# 4. Launch the Chatbot
source .venv/bin/activate
streamlit run app.py