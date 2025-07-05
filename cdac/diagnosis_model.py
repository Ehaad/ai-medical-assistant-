import json
import re

with open("data/symptoms_conditions.json") as f:
    symptoms_db = json.load(f)

def generate_diagnosis(user_input):
    user_input = user_input.lower()
    matched = []

    for symptom, message in symptoms_db.items():
        # Match entire words only (fever ≠ feverish)
        if re.search(r'\b' + re.escape(symptom) + r'\b', user_input):
            matched.append(f" <b>{symptom.title()}:</b>  {message}")

    if not matched:
        return ["⚠️ Sorry, I couldn't identify the condition. Please consult a doctor."]
    
    return list(set(matched))  # Remove duplicates if any
