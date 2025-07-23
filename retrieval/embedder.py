from sentence_transformers import SentenceTransformer
from retrieval.vectorstore import QdrantVectorStore
import config
import os

_model = None

# Try to load embedding model from local path for offline use
def get_embedder():
    global _model
    if _model is None:
        local_model_path = os.path.join(config.MODELS_DIR, "bge-small-en-v1.5")
        if os.path.exists(local_model_path):
            _model = SentenceTransformer(local_model_path)
        else:
            _model = SentenceTransformer(config.EMBEDDING_MODEL_NAME)
    return _model

def embed_chunks(chunks):
    model = get_embedder()
    texts = [c["chunk_text"] for c in chunks]
    embeddings = model.encode(texts, show_progress_bar=True, normalize_embeddings=True)
    vectorstore = QdrantVectorStore()
    vectorstore.reset_collection()
    vectorstore.add_embeddings(embeddings, chunks) 