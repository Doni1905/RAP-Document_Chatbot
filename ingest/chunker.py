from typing import List, Dict
import config
from ingest.document_loader import chunk_documents as docx_chunk_documents

def chunk_documents(docs: List[Dict], chunk_size: int, overlap: int) -> List[Dict]:
    # Use the chunking logic from document_loader.py which handles both PDF and DOCX
    from ingest.document_loader import chunk_documents as docx_chunk_documents
    return docx_chunk_documents(docs, chunk_size, overlap) 