# Configuration constants for the offline RAG chatbot

# Model names/paths
# For offline use, place bge-small-en-v1.5 in models/bge-small-en-v1.5/
# EMBEDDING_MODEL_NAME is only used as a fallback if the local model is missing
EMBEDDING_MODEL_NAME = "BAAI/bge-small-en-v1.5"
LLM_MODEL_PATH = "models/phi-3-mini-4k-instruct-q4.gguf"  # or mistral GGUF

# LLM backend: 'ctransformers' (default, local GGUF) or 'ollama' (Ollama server)
LLM_BACKEND = "ollama"
OLLAMA_MODEL = "mistral"  # or "llama3", "phi3", etc. (must match a model you have pulled in Ollama)

# Chunking
CHUNK_SIZE = 512
CHUNK_OVERLAP = 128
EMBEDDING_DIM = 384  # bge-small-en-v1.5

# Directories
DATA_DIR = "data"
INDEX_DIR = "docs_index"
MODELS_DIR = "models"

# Qdrant
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
QDRANT_COLLECTION = "rag_chunks"

# Other
MAX_CONTEXT_CHUNKS = 3