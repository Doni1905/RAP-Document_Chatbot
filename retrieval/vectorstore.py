from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct, Filter, FieldCondition, MatchValue
from sentence_transformers import SentenceTransformer
import config
import os
import numpy as np

class QdrantVectorStore:
    def __init__(self):
        self.client = QdrantClient(host=config.QDRANT_HOST, port=config.QDRANT_PORT)

    def reset_collection(self):
        collections = [c.name for c in self.client.get_collections().collections]
        if config.QDRANT_COLLECTION in collections:
            self.client.delete_collection(collection_name=config.QDRANT_COLLECTION)
        self.client.recreate_collection(
            collection_name=config.QDRANT_COLLECTION,
            vectors_config=VectorParams(size=config.EMBEDDING_DIM, distance=Distance.COSINE)
        )

    def add_embeddings(self, embeddings, chunks):
        points = []
        for i, (emb, meta) in enumerate(zip(embeddings, chunks)):
            points.append(PointStruct(
                id=i,
                vector=np.array(emb, dtype=np.float32),
                payload={
                    "filename": meta["filename"],
                    "page": meta.get("page"),  # Will be None for DOCX
                    "total_pages": meta.get("total_pages"),  # Will be None for DOCX
                    "chunk_id": meta["chunk_id"],
                    "chunk_text": meta["chunk_text"],
                    "source_ref": meta.get("source_ref")
                }
            ))
        self.client.upsert(collection_name=config.QDRANT_COLLECTION, points=points)

    def search(self, query, top_k=3):
        # Use the same embedder as in embedder.py for consistency
        from retrieval.embedder import get_embedder
        embedder = get_embedder()
        query_emb = embedder.encode([query], normalize_embeddings=True)[0]
        results = self.client.search(
            collection_name=config.QDRANT_COLLECTION,
            query_vector=query_emb,
            limit=top_k
        )
        print("[DEBUG] Qdrant search results:", results)
        context_chunks = []
        for r in results:
            payload = r.payload
            context_chunks.append({
                "chunk_text": payload["chunk_text"],
                "filename": payload["filename"],
                "chunk_id": payload["chunk_id"],
                "page": payload.get("page"),
                "total_pages": payload.get("total_pages"),
                "source_ref": payload.get("source_ref")
            })
        return context_chunks 