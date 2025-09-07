# In backend/main_api.py

import os
import json
import io
import gdown 
import requests # Make sure requests is imported
from fastapi import FastAPI, File, UploadFile, Query
from PIL import Image
import numpy as np
import tensorflow as tf
from dotenv import load_dotenv, find_dotenv
import google.generativeai as genai

# --- NEW: Automatic Model Downloader ---
working_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(working_dir, "plant_disease_model.h5")

# Check if the model file exists. If not, download it.
if not os.path.exists(model_path):
    print(f"🟢 Model not found at {model_path}. Downloading...")
    
    # Your personal direct download link is now here
    file_url = "https://drive.google.com/file/d/10e5IxWZv4_k4_eQGvuYiONlEExiCa00A/view?usp=sharing"
    
    try:
        # Use gdown to download the file correctly
        gdown.download(url=file_url, output=model_path, quiet=False)
        print("✅ Model downloaded successfully.")
    except Exception as e:
        print(f"🔴 Failed to download model with gdown. Error: {e}")
# --- END: Automatic Model Downloader ---


# --- The rest of your file is the same ---
class_indices_path = os.path.join(working_dir, "class_indices.json")

# ... (The rest of your main_api.py file remains exactly the same) ...
model = tf.keras.models.load_model(model_path)
with open(class_indices_path, 'r') as f:
    class_indices = json.load(f)

# --- Robust Gemini API Loading ---
load_dotenv(find_dotenv())
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("🔴 ERROR: GOOGLE_API_KEY not found in .env file.")
else:
    print("🟢 SUCCESS: Google API Key loaded.")
genai.configure(api_key=api_key)
gemini_model = genai.GenerativeModel("gemini-1.5-flash")

# --- FastAPI App ---
app = FastAPI(title="AgroDoctor API")

@app.post("/predict_disease")
async def predict_disease_endpoint(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        img = Image.open(io.BytesIO(contents)).convert('RGB')
        img = img.resize((224, 224))
        img_array = np.array(img) / 255.0
        img_array = img_array.reshape(1, 224, 224, 3)
        predictions = model.predict(img_array)
        predicted_index = str(np.argmax(predictions))
        predicted_class_name = class_indices.get(predicted_index, "Unknown Disease")
        confidence = float(np.max(predictions))
        return {"predicted_disease": predicted_class_name, "confidence": confidence}
    except Exception as e:
        return {"error": f"Prediction failed: {e}"}

@app.get("/get_treatment")
async def get_treatment_endpoint(disease_name: str = Query(...), language: str = Query("English")):
    prompt = (
    f"You are an expert agricultural advisor for farmers in Andhra Pradesh, India. "
    f"Provide a detailed and practical medication and treatment plan for the plant disease '{disease_name}', written in the {language} language. "
    f"The plan must be tailored specifically to Indian standards.\n\n"
    f"Crucially, you must follow these rules:\n"
    f"1. **Format the entire response using simple Markdown.** Use `##` for main headings and `*` for bullet points. Do not use complex Markdown.\n"
    f"2. **Do not create tables using characters like '|' and '-'.** Instead, list product details using bullet points under a heading.\n"
    f"3. All suggested chemical pesticides or commercial products must be brands **commonly available in India**.\n"
    f"4. Provide an estimated cost for these products in **Indian Rupees (INR, ₹)**.\n"
    f"5. Include detailed sections for organic/home remedies and preventive measures suitable for local conditions.\n"
    f"6. The outcome must not contain any comments."
)
    try:
        response = gemini_model.generate_content(prompt)
        return {"treatment_plan": response.text}
    except Exception as e:
        print(f"🔴 GEMINI API ERROR: {e}")
        return {"error": f"Failed to fetch medication details: {e}"}