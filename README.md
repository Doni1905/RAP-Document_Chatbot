# Offline RAG Chatbot

A fully offline Retrieval-Augmented Generation (RAG) chatbot using open-source models and tools.

## Features
- Ingests PDF and DOCX documents
- Embeds with `bge-small-en-v1.5`
- Stores vectors in Qdrant (local, via Docker)
- Answers with quantized LLMs (Phi-3-mini, Mistral, etc. via GGUF/ctransformers)
- Streamlit UI
- Displays filename, page, and chunk for each answer
- 100% offline, optimized for CPU or Tesla T4 GPU

## Setup

1. **Download Python wheels:**
   ```bash
   ./download_wheels.sh
   ```
2. **Download models:**
   - Place GGUF LLMs in `models/`
   - Place bge-small-en-v1.5 in `models/` (or update config to point to local path)

3. **Run setup:**
   ```bash
   ./setup.sh
   ```

4. **Upload your documents and start chatting!**

## Architecture
- **Ingestion:** Loads PDF/DOCX, splits into overlapping chunks, tracks filename/page.
- **Embedding:** Uses bge-small-en-v1.5 to embed chunks.
- **Vector Store:** Stores embeddings and metadata in Qdrant.
- **Retrieval:** Finds relevant chunks for a user query.
- **Generation:** LLM (GGUF via ctransformers) answers using only retrieved context.
- **UI:** Streamlit app for uploads, queries, and displaying answers with sources.

## Chunking Logic
- Documents are split into chunks of 512 words with 128-word overlap.
- Each chunk is tagged with filename, page, and chunk_id for traceability.

## Example Test Case
- Upload a PDF or DOCX with known content.
- Ask a question about a specific section.
- The answer should cite the correct filename, page, and chunk.

## Notes
- For full offline use, pre-download all Python wheels and models.
- Qdrant runs locally via Docker.
- For GPU, ensure CUDA drivers are installed and ctransformers is built with GPU support.

## Offline Embedding Model Usage

For fully offline operation, download the bge-small-en-v1.5 embedding model from HuggingFace and place it in:

```
models/bge-small-en-v1.5/
```

The code will automatically use this local directory if it exists. If not, it will attempt to download from HuggingFace (requires internet).

Similarly, place your GGUF LLMs in the `models/` directory as described above.

## License
Open source, for research and educational use. 

---

## 1. Download All Required Files (On an Online Machine)

### a. Download Python Wheels for Offline Install
1. Open a terminal in your project directory.
2. Run:
   ```bash
   chmod +x download_wheels.sh
   ./download_wheels.sh
   ```
   This will create a `wheels/` directory with all required Python packages.

### b. Download Embedding Model (bge-small-en-v1.5)
1. Use the following Python snippet to download the model:
   ```python
   from huggingface_hub import snapshot_download
   snapshot_download(repo_id="BAAI/bge-small-en-v1.5", local_dir="models/bge-small-en-v1.5")
   ```
   Or download manually from [HuggingFace](https://huggingface.co/BAAI/bge-small-en-v1.5) and place the files in `models/bge-small-en-v1.5/`.

### c. Download GGUF LLM (e.g., Phi-3-mini)
1. Download the GGUF file (e.g., `phi-3-mini-4k-instruct-q4.gguf`) from [HuggingFace](https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf) or another source.
2. Place it in your `models/` directory.

---

## 2. Transfer Files to Your Offline Machine

- Copy the entire project directory, including:
  - `wheels/`
  - `models/`
  - All your code and scripts

---

## 3. Set Up and Run the Project (On the Offline Machine)

1. **Make sure Docker is installed and running** (for Qdrant).
2. **Run the setup script:**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```
   This will:
   - Create a Python virtual environment
   - Install all dependencies from your local `wheels/`
   - Start Qdrant via Docker
   - Launch the Streamlit UI

---

## 4. Use the Chatbot

1. Open the Streamlit UI (usually at http://localhost:8501).
2. Upload your PDF or DOCX files.
3. Ask questions about your documents.
4. The chatbot will answer, citing the filename, page, and chunk for each answer.

---

## 5. Stopping the System

- To stop Qdrant:
  ```bash
  docker stop qdrant_rag && docker rm qdrant_rag
  ```

---

## 6. Troubleshooting

- If you see any errors about missing models, double-check that:
  - `models/bge-small-en-v1.5/` contains the embedding model files.
  - `models/` contains your GGUF LLM file.
- If you see errors about missing Python packages, ensure all wheels are present in `wheels/`.

---

**You do not need to write or change any code. Just follow these steps and your offline RAG chatbot will be ready to use!**

If you want me to generate a script to automate any of these steps, or if you want a test document to try, just ask! 

### To use a different model with Ollama:

1. **Pull the desired model with Ollama**  
   For example, to use Mistral:
   ```bash
   ollama pull mistral
   ```
   Or for Llama 3:
   ```bash
   ollama pull llama3
   ```

2. **Update your `config.py`**  
   Change the `OLLAMA_MODEL` line to match the model you want to use:
   ```python
   LLM_BACKEND = "ollama"
   OLLAMA_MODEL = "mistral"   # or "llama3", "llama2", etc.
   ```

3. **Restart your chatbot**  
   (If it was running, stop and start it again so it picks up the new config.)

---

**That’s it!**  
Your chatbot will now use the new model via Ollama for all LLM responses.

If you want to use a custom model (e.g., one you’ve created or fine-tuned), just make sure it’s available in your local Ollama instance and set `OLLAMA_MODEL` to its name.

Let me know if you want a list of recommended models or further help! 

---

## 1. Make Sure Mistral 7B is Pulled in Ollama

You must have the model downloaded in Ollama.  
If you have internet, run:
```bash
ollama pull mistral
```
If you are offline and have never pulled it before, you cannot use it until you go online and pull it once.

---

## 2. Set Your Config to Use Ollama and Mistral

In your `config.py`, make sure you have:
```python
LLM_BACKEND = "ollama"
OLLAMA_MODEL = "mistral"
```
This tells your app to use the Mistral model from your local Ollama server.

---

## 3. Start Ollama (if not already running)

If Ollama is not running, start it:
```bash
ollama serve
```
If you see "address already in use", it means Ollama is already running (which is good).

---

## 4. Start Your Chatbot

Activate your virtual environment if needed:
```bash
source .venv/bin/activate
```
Then run:
```bash
streamlit run app.py
```

---

## 5. Use the Chatbot

- Open [http://localhost:8501](http://localhost:8501) in your browser.
- Upload your documents and ask questions. The answers will be generated by Mistral 7B via Ollama.

---

### Troubleshooting

- If you get a "model not found" error, make sure you have run `ollama pull mistral` and it completed successfully.
- If you get a connection error, make sure Ollama is running and listening on port 11434.
- If you are offline and have never pulled the model, you must connect to the internet and pull it at least once.

---

**Summary:**  
1. Pull the model with `ollama pull mistral` (online, only needed once).
2. Set `LLM_BACKEND = "ollama"` and `OLLAMA_MODEL = "mistral"` in `config.py`.
3. Start Ollama and your app.
4. Use your chatbot—Mistral 7B will answer your questions!

Let me know if you hit any issues or want to verify your setup! # RAP-Document_Chatbot
