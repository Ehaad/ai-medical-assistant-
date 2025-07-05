import os
import re
import json
import easyocr
import numpy as np
from PIL import Image
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from pdf2image import convert_from_path

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'txt', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Load symptom-diagnosis data
with open("data/symptoms_conditions.json") as f:
    symptoms_db = json.load(f)

# Initialize EasyOCR reader
reader = easyocr.Reader(['en'], gpu=False)

# --- Helper Functions ---

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_file(file_path):
    ext = file_path.rsplit('.', 1)[1].lower()
    try:
        if ext in ['png', 'jpg', 'jpeg']:
            print("🔍 OCR: Reading image...")
            result = reader.readtext(file_path, detail=0)
            text = ' '.join(result)

        elif ext == 'pdf':
            print("📄 OCR: Converting PDF pages to images...")
            images = convert_from_path(file_path)
            result = []
            for img in images:
                img_np = np.array(img)
                result += reader.readtext(img_np, detail=0)
            text = ' '.join(result)

        elif ext == 'txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()

        elif ext == 'docx':
            import docx
            doc = docx.Document(file_path)
            text = '\n'.join([para.text for para in doc.paragraphs])

        else:
            text = ''

        print("🧾 Extracted Text:\n", text)
        return text

    except Exception as e:
        print("❌ OCR Error:", e)
        return ""

def generate_diagnosis(user_input):
    user_input = user_input.lower()
    matches = []
    for symptom, suggestion in symptoms_db.items():
        if re.search(r'\b' + re.escape(symptom) + r'\b', user_input):
            matches.append(f"if it is <b>{symptom.title()}:</b> {suggestion}")
    if not matches:
        return ["⚠️ Sorry, no recognizable symptoms found. Please consult a doctor."]
    print("🧠 Diagnosis:", matches)
    return list(set(matches))

# --- Routes ---

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api", methods=["POST"])
def diagnose_from_text():
    data = request.get_json()
    user_input = data.get("message", "")
    result = generate_diagnosis(user_input)
    return jsonify({"response": result})

@app.route("/upload", methods=["POST"])
def upload_prescription():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"})
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"})
    if file and allowed_file(file.filename):
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        extracted_text = extract_text_from_file(filepath)
        diagnosis = generate_diagnosis(extracted_text)
        return jsonify({"text": extracted_text, "response": diagnosis})

    return jsonify({"error": "Unsupported file format"})

# --- Main ---
if __name__ == "__main__":
    app.run(debug=True)
