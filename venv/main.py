from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import database
import ai_engine

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

@app.get("/")
def home():
    return {"status": "FieldVoice Backend Active"}

@app.post("/api/process-and-save")
def process_and_save(data: FieldInputRequest):
    if not data.raw_text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    
    # 1. Process using ai_engine.py
    ai_result = ai_engine.process_field_input(data.raw_text)
    
    # 2. Save result to SQLite database
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

@app.get("/api/logs/search")
def search_patient_logs(q: str = ""):
    if not q.strip():
        return {"logs": database.get_all_logs()}
    return {"query": q, "results": database.search_logs(q)}

@app.delete("/api/logs/{log_id}")
def delete_patient_log(log_id: int):
    database.delete_log(log_id)
    return {"success": True, "message": f"Log {log_id} deleted successfully."}