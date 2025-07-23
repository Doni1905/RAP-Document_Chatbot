import streamlit as st
from ingest.document_loader import load_documents
from ingest.chunker import chunk_documents
from retrieval.embedder import embed_chunks
from retrieval.vectorstore import QdrantVectorStore
from generation.llm_wrapper import generate_answer
from utils.logger import get_logger
from utils.timer import Timer
import config
import os

logger = get_logger()

st.set_page_config(page_title="Offline RAG Chatbot", layout="wide")
st.title("📄 Offline RAG Chatbot")

# Upload documents
st.sidebar.header("Upload Documents")
uploaded_files = st.sidebar.file_uploader(
    "Upload PDF or DOCX files", type=["pdf", "docx"], accept_multiple_files=True
)

if uploaded_files:
    with st.spinner("Saving and processing documents..."):
        for file in uploaded_files:
            file_path = os.path.join(config.DATA_DIR, file.name)
            with open(file_path, "wb") as f:
                f.write(file.getbuffer())
        docs = load_documents(config.DATA_DIR)
        chunks = chunk_documents(docs, config.CHUNK_SIZE, config.CHUNK_OVERLAP)
        embed_chunks(chunks)
    st.success("Documents ingested and indexed!")

# User query
st.header("Ask a question about your documents:")
user_query = st.text_input("Your question:")

if st.button("Get Answer") and user_query:
    with Timer("Total retrieval + generation"), st.spinner("Retrieving answer..."):
        vectorstore = QdrantVectorStore()
        with Timer("Qdrant search"):
            context_chunks = vectorstore.search(user_query, top_k=config.MAX_CONTEXT_CHUNKS)
        with Timer("LLM generation"):
            answer = generate_answer(user_query, context_chunks)
        st.markdown(f"**Answer:** {answer['text']}")
        st.markdown("---")
        st.markdown("**Sources:**")
        for meta in answer['sources']:
            st.markdown(f"- `{meta['filename']}` | Page: {meta['page']}, Chunk: {meta['chunk_id']}") 