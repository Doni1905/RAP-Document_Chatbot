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
    sources = [{"filename": c["filename"], "page": c["page"], "chunk_id": c["chunk_id"]} for c in context_chunks]
    if config.LLM_BACKEND == "ollama":
        # Use Ollama server
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
    else:
        llm = get_llm()
        output = llm(prompt, max_new_tokens=128, stop=["\n"])
    return {"text": output.strip(), "sources": sources} 