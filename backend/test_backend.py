import requests

BASE_URL = "http://localhost:8000"

TEST_SAMPLES = [
    "Patient ko fever hai 102, gave paracetamol 500mg, kal shaam ko wapas aana",
    "Ich bin nicht so gut, My head hurts badly and high temperature",
    "3andana mushkila fil pump, bleeding severe in leg, patient unconscious",
    "Fitter line me leakage h, worker got burned on hand with hot steam"
]

def run_tests():
    print("--- TESTING FIELDVOICE BACKEND & LOCAL AI ---")
    
    for sample in TEST_SAMPLES:
        print(f"\n[INPUT]: {sample}")
        response = requests.post(
            f"{BASE_URL}/api/process-and-save",
            json={"raw_text": sample}
        )
        if response.status_code == 200:
            res_data = response.json()
            print(f"[TRANSLATED]: {res_data['data'].get('translated_text')}")
            print(f"[MEDS]: {res_data['data'].get('extracted_meds')}")
            print(f"[VITALS]: {res_data['data'].get('vital_stats')}")
            print(f"[SAVED LOG ID]: {res_data.get('log_id')}")
        else:
            print(f"[ERROR]: {response.status_code}")

if __name__ == "__main__":
    run_tests()