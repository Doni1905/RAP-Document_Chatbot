from ctransformers import AutoModelForCausalLM
import config
import os
import requests

PROMPT_TEMPLATE = """
You are a helpful assistant. Answer the user's question using only the context below.
If the answer is not in the context, reply with: 'The answer is not available in the documents provided.'

Context:
{context}

Question:
{question}

Answer:
"""

_llm = None

def get_llm():
    global _llm
    if _llm is None and config.LLM_BACKEND == "ctransformers":
        _llm = AutoModelForCausalLM.from_pretrained(config.LLM_MODEL_PATH, model_type="phi3", gpu_layers=32)
    return _llm

def generate_answer(user_query, context_chunks):
    context = "\n---\n".join([c["chunk_text"] for c in context_chunks])
    prompt = PROMPT_TEMPLATE.format(context=context, question=user_query)
    # Debug: print context_chunks
    print("[DEBUG] context_chunks:", context_chunks)
    sources = [{
        "filename": c.get("filename"),
        "chunk_id": c.get("chunk_id"),
        "page": c.get("page"),
        "total_pages": c.get("total_pages"),
        "source_ref": c.get("source_ref")
    } for c in context_chunks]
    # Debug: print sources
    print("[DEBUG] sources:", sources)
    if config.LLM_BACKEND == "ollama":
        # Use Ollama server
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": config.OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"num_predict": 128}
                },
                timeout=120
            )
            response.raise_for_status()
            result = response.json()
            output = result.get("response", "")
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Ollama API call failed: {e}")
            output = "I apologize, but I'm unable to generate a response at the moment. Please check if Ollama is running and the model is available."
    else:
        llm = get_llm()
        output = llm(prompt, max_new_tokens=128, stop=["\n"])
    return {"text": output.strip(), "sources": sources} 