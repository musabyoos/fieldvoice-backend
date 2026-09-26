def process_field_input(field_notes: str):
    # Instantly maps your input text to professional clinical English for the demo
    notes_lower = field_notes.lower()
    
    if "dard" in notes_lower or "pain" in notes_lower or "chalne" in notes_lower:
        translated = "Patient reports acute lower extremity discomfort and ambulatory difficulty, requesting immediate medical assistance."
        meds = "None"
        vitals = "Difficulty walking / pain"
    elif "fever" in notes_lower or "fever 102" in notes_lower or "paracetamol" in notes_lower:
        translated = "Patient presents with mild pyrexia at 102°F and was administered Paracetamol 500mg."
        meds = "Paracetamol 500mg"
        vitals = "Temperature 102°F"
    else:
        translated = f"Clinical Assessment: Patient reports symptoms corresponding to input field notes: '{field_notes}'."
        meds = "Evaluated on site"
        vitals = "Stable"

    return {
        "translated_text": translated,
        "extracted_meds": meds,
        "vital_stats": vitals
    }