from typing import List, Dict
import config
from ingest.document_loader import chunk_documents as docx_chunk_documents

def chunk_documents(docs: List[Dict], chunk_size: int, overlap: int) -> List[Dict]:
    # If DOCX chunking logic is present in document_loader, use it for DOCX; otherwise, handle PDF here
    # This function will handle PDF chunking, and delegate DOCX to the loader's chunker
    if docs and "paragraphs" in docs[0]:
        # DOCX: use the new logic
        return docx_chunk_documents(docs, chunk_size, overlap)
    # PDF logic (default)
    chunks = []
    global_chunk_id = 0
    for doc in docs:
        text = doc["text"]
        words = text.split()
        start = 0
        while start < len(words):
            end = min(start + chunk_size, len(words))
            chunk_words = words[start:end]
            chunk_text = " ".join(chunk_words)
            chunks.append({
                "chunk_text": chunk_text,
                "filename": doc["filename"],
                "page": doc["page"],
                "total_pages": doc.get("total_pages"),
                "chunk_id": global_chunk_id,
                "source_ref": f"Page: {doc['page']}"
            })
            global_chunk_id += 1
            start += chunk_size - overlap
    return chunks 