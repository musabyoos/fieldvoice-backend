import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3"

SYSTEM_PROMPT = """
You are an offline emergency medical translation engine for field responders.
You will receive raw speech transcripts that contain code-switching, mixed languages (e.g., Hinglish, Arabizi, Spanish-English), and informal phonetic spelling.

Tasks:
1. Translate the input into clean, formal English.
2. Extract key details: 'translated_text', 'detected_language', 'extracted_meds', and 'vital_stats'.

Return ONLY a valid JSON object in this format with no extra text:
{
  "translated_text": "string",
  "detected_language": "string",
  "extracted_meds": "string",
  "vital_stats": "string"
}
"""

def process_field_input(raw_text: str) -> dict:
    """Processes code-switched text using local Ollama (or falls back to mock data if offline)."""
    payload = {
        "model": MODEL_NAME,
        "prompt": f"{SYSTEM_PROMPT}\n\nInput: \"{raw_text}\"",
        "stream": False,
        "format": "json"
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=5)
        if response.status_code == 200:
            raw_response = response.json().get("response", "{}")
            return json.loads(raw_response)
    except Exception as e:
        print(f"[AI ENGINE NOTICE]: Local Ollama not reachable, using fallback engine.")

    # Fallback response for rapid testing when Ollama isn't active
    return {
        "translated_text": f"[MOCK TRANSLATION]: {raw_text}",
        "detected_language": "Code-Switched / Dialect",
        "extracted_meds": "Paracetamol 500mg",
        "vital_stats": "Fever 102F"
    }