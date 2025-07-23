# Offline RAG Chatbot

A fully offline Retrieval-Augmented Generation (RAG) chatbot that answers user queries based on your own PDF and DOCX documents, using only open-source models and tools.

---

## 🚀 Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/Doni1905/RAP-Document_Chatbot.git
cd RAP-Document_Chatbot
```

### 2. Install Python & Dependencies
- **Python 3.10+** is required.
- Create and activate a virtual environment:
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```
- Install dependencies (offline, from wheels):
  ```bash
  pip install --no-cache-dir --find-links=./wheels -r requirements.txt
  ```

### 3. Start Qdrant (Vector Database)
- **Requires Docker**. Start Qdrant with:
  ```bash
  docker start qdrant_rag || docker run -d --name qdrant_rag -p 6333:6333 -v $(pwd)/docs_index:/qdrant/storage qdrant/qdrant
  ```

### 4. Start Ollama (LLM Server)
- Make sure [Ollama](https://ollama.com/) is installed and running:
  ```bash
  ollama serve
  ollama pull mistral  # or phi3, llama3, etc.
  ```

### 5. Run the Chatbot
```bash
streamlit run app.py
```
- Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 💬 How to Use the Chatbot
1. **Upload Documents:** Use the sidebar to upload PDF or DOCX files.
2. **Ingest & Index:** The app will automatically chunk, embed, and index your documents.
3. **Ask Questions:** Enter your question in the main input box and click "Get Answer".
4. **View Answers:** The chatbot will answer using only your documents, showing filename, page, and chunk for each source.

---

## 🏗️ Architecture & Tools Used
- **UI:** [Streamlit](https://streamlit.io/) for a simple, interactive web interface.
- **Document Loading:** `pypdf` for PDFs, `python-docx` for DOCX files.
- **Chunking:** Custom overlapping chunker for context-rich retrieval.
- **Embedding:** [bge-small-en-v1.5](https://huggingface.co/BAAI/bge-small-en-v1.5) via `sentence-transformers`.
- **Vector Store:** [Qdrant](https://qdrant.tech/) (local, via Docker) for fast vector search.
- **LLM:** [Ollama](https://ollama.com/) serving open-source models (e.g., Mistral 7B, Phi-3-mini) for answer generation.
- **Utilities:** Logging, timing, and setup scripts for offline operation.

---

## 📚 Chunking Strategy
- Documents are split into chunks of **512 words** with **128-word overlap**.
- Each chunk is tagged with filename, page, and chunk ID for traceability.
- Overlapping chunks ensure context continuity and better retrieval.

---

## 🔍 Retrieval & Embedding
- **Embedding Model:** `bge-small-en-v1.5` (384-dim, open-source, CPU/GPU compatible)
- **Retrieval:**
  - User query is embedded using the same model.
  - Qdrant performs a vector similarity search (cosine distance) to find the top 3 most relevant chunks.
  - Retrieved chunks are passed as context to the LLM.

---

## 🖥️ Hardware Used
- **CPU:** Apple Silicon (M1/M2) or Intel/AMD (tested on MacBook Pro)
- **RAM:** 16GB recommended for smooth operation
- **GPU:** Not required, but supported for faster embedding/LLM (NVIDIA Tesla T4 or similar)
- **Disk:** Sufficient space for models and document indexes

---

## 📝 Key Observations & Learnings
- **Offline-First:** All models and dependencies are local; no internet required after setup.
- **Ollama Integration:** Makes it easy to swap LLMs (Mistral, Phi-3, Llama3, etc.) for different needs.
- **Chunk Overlap:** Improves retrieval accuracy by preserving context across chunk boundaries.
- **Qdrant Performance:** Fast and reliable for vector search, even on large document sets.
- **Streamlit Simplicity:** Enables rapid prototyping and user-friendly interaction.
- **Git Hygiene:** Use `.gitignore` and history cleaning to avoid pushing large files to GitHub.
- **Scalability:** Easily extendable to more documents, different embedding models, or LLMs.

---

## 📦 Directory Structure
```
├── app.py                # Streamlit UI
├── config.py             # Configuration
├── requirements.txt      # Python dependencies
├── setup.sh              # Offline installer
├── ingest/               # Document loader & chunker
├── retrieval/            # Embedder & vectorstore
├── generation/           # LLM wrapper
├── utils/                # Logger & timer
├── data/                 # User documents (PDF/DOCX)
├── docs_index/           # Indexed chunks & metadata
├── models/               # Local GGUF models
├── wheels/               # Offline Python wheels
└── README.md             # This file
```

---

## 🙏 Acknowledgements
- [Qdrant](https://qdrant.tech/), [Ollama](https://ollama.com/), [Streamlit](https://streamlit.io/), [HuggingFace](https://huggingface.co/BAAI/bge-small-en-v1.5), and the open-source community.
