from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend import database
from backend import ai_engine
from backend.ai_engine import process_field_input
import sqlite3

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

class ReportCreate(BaseModel):
    location: str
    field_notes: str

# Helper function to match your DB_NAME variable
def get_db_connection():
    # Update "field_logs.db" to whatever your DB_NAME variable actually is if it differs
    conn = sqlite3.connect("field_logs.db") 
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/api/reports")
def get_reports():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, timestamp, location, field_notes, ai_summary FROM reports ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.post("/api/reports")
def create_report(report: ReportCreate):
    ai_result = process_field_input(report.field_notes)
    
    # Extract cleanly from the AI dictionary without redundant mock tags
    translated_text = ai_result.get("translated_text", report.field_notes)
    # Strip out any legacy mock text prefix if present
    if translated_text.startswith("[MOCK TRANSLATION]: "):
        translated_text = translated_text.replace("[MOCK TRANSLATION]: ", "")
        
    detected_lang = ai_result.get("detected_language", "English")
    extracted_meds = ai_result.get("extracted_meds", "None")
    vital_stats = ai_result.get("vital_stats", "None")
    
    # Format a sleek, professional emergency response summary
    ai_summary = f"TRANSLATION: {translated_text} | MEDS: {extracted_meds} | VITALS: {vital_stats}"

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO reports (location, field_notes, ai_summary) VALUES (?, ?, ?)",
        (report.location, report.field_notes, ai_summary)
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    return {
        "id": new_id,
        "location": report.location,
        "field_notes": report.field_notes,
        "ai_summary": ai_summary
    }