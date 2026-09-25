import sqlite3
from datetime import datetime

DB_NAME = "field_logs.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patient_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            raw_input TEXT NOT NULL,
            translated_text TEXT NOT NULL,
            detected_language TEXT,
            extracted_meds TEXT,
            vital_stats TEXT,
            status TEXT DEFAULT 'logged'
        )
    ''')
    conn.commit()
    conn.close()

def add_log(raw_input: str, translated_text: str, detected_language: str = "Unknown", extracted_meds: str = "", vital_stats: str = ""):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        INSERT INTO patient_logs (timestamp, raw_input, translated_text, detected_language, extracted_meds, vital_stats)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (timestamp, raw_input, translated_text, detected_language, extracted_meds, vital_stats))
    conn.commit()
    log_id = cursor.lastrowid
    conn.close()
    return log_id

def get_all_logs():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM patient_logs ORDER BY id DESC')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]