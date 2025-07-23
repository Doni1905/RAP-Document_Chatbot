from typing import List, Dict
import config

def chunk_documents(docs: List[Dict], chunk_size: int, overlap: int) -> List[Dict]:
    chunks = []
    for doc in docs:
        text = doc["text"]
        words = text.split()
        start = 0
        chunk_id = 0
        while start < len(words):
            end = min(start + chunk_size, len(words))
            chunk_words = words[start:end]
            chunk_text = " ".join(chunk_words)
            chunks.append({
                "chunk_text": chunk_text,
                "filename": doc["filename"],
                "page": doc["page"],
                "chunk_id": chunk_id
            })
            chunk_id += 1
            start += chunk_size - overlap
    return chunks 