import os
from typing import List, Dict
from pypdf import PdfReader
from docx import Document

def load_documents(data_dir: str) -> List[Dict]:
    docs = []
    for fname in os.listdir(data_dir):
        fpath = os.path.join(data_dir, fname)
        if fname.lower().endswith(".pdf"):
            reader = PdfReader(fpath)
            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                if text:
                    docs.append({
                        "text": text,
                        "filename": fname,
                        "page": i + 1
                    })
        elif fname.lower().endswith(".docx"):
            doc = Document(fpath)
            full_text = []
            for para in doc.paragraphs:
                full_text.append(para.text)
            docs.append({
                "text": "\n".join(full_text),
                "filename": fname,
                "page": 1
            })
    return docs 