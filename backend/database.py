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

def search_logs(query: str):
    """Searches patient logs by raw input, translated text, or extracted meds."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    search_term = f"%{query}%"
    cursor.execute('''
        SELECT * FROM patient_logs 
        WHERE raw_input LIKE ? 
           OR translated_text LIKE ? 
           OR extracted_meds LIKE ?
        ORDER BY id DESC
    ''', (search_term, search_term, search_term))
    
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def delete_log(log_id: int):
    """Deletes a specific log record by ID."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM patient_logs WHERE id = ?', (log_id,))
    conn.commit()
    conn.close()

def search_logs(query: str):
    """Searches logs matching raw input, translated text, or meds."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    search_term = f"%{query}%"
    cursor.execute('''
        SELECT * FROM patient_logs 
        WHERE raw_input LIKE ? 
           OR translated_text LIKE ? 
           OR extracted_meds LIKE ?
        ORDER BY id DESC
    ''', (search_term, search_term, search_term))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def delete_log(log_id: int):
    """Deletes a specific patient log entry."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM patient_logs WHERE id = ?', (log_id,))
    conn.commit()
    conn.close()

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        location TEXT NOT NULL,
        field_notes TEXT NOT NULL,
        ai_summary TEXT
    )
''')

conn.commit()
conn.close()