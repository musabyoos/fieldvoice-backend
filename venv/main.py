from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import database

app = FastAPI(title="FieldVoice Emergency API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    database.init_db()

class FieldInputRequest(BaseModel):
    raw_text: str

OLLAMA_URL = "http://localhost:11434/api/generate"

def query_ollama_or_mock(raw_text: str) -> dict:
    system_prompt = (
        "Translate code-switched or dialect speech to formal English. "
        "Extract medications and vitals. Return JSON format with keys: "
        "'translated_text', 'detected_language', 'extracted_meds', 'vital_stats'."
    )
    
    payload = {
        "model": "llama3",
        "prompt": f"{system_prompt}\nInput: {raw_text}",
        "stream": False,
        "format": "json"
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=3)
        if response.status_code == 200:
            import json
            return json.loads(response.json().get("response", "{}"))
    except Exception:
        pass
    
    return {
        "translated_text": f"[MOCK TRANSLATION]: {raw_text}",
        "detected_language": "Code-switched (Hindi/English)",
        "extracted_meds": "Paracetamol 500mg",
        "vital_stats": "Fever 102F"
    }

@app.get("/")
def home():
    return {"status": "FieldVoice Backend Active"}

@app.post("/api/process-and-save")
def process_and_save(data: FieldInputRequest):
    if not data.raw_text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    
    ai_result = query_ollama_or_mock(data.raw_text)
    
    log_id = database.add_log(
        raw_input=data.raw_text,
        translated_text=ai_result.get("translated_text", data.raw_text),
        detected_language=ai_result.get("detected_language", "Unknown"),
        extracted_meds=ai_result.get("extracted_meds", "None"),
        vital_stats=ai_result.get("vital_stats", "None")
    )
    
    return {
        "success": True,
        "log_id": log_id,
        "data": ai_result
    }

@app.get("/api/logs")
def fetch_logs():
    return {"logs": database.get_all_logs()}