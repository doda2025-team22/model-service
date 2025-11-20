"""
Flask API of the SMS Spam detection model model.
"""
import joblib
from flask import Flask, jsonify, request
from flasgger import Swagger
import pandas as pd
import os
import requests

from text_preprocessing import prepare, _extract_message_len, _text_process

app = Flask(__name__)
swagger = Swagger(app)

DEFAULT_MODEL_URL = "https://api.github.com/repos/doda2025-team22/model-service/releases/latest"
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "/app/output")
MODEL_PATH = os.path.join(OUTPUT_DIR, "model.joblib")
PREPROCESSOR_PATH = os.path.join(OUTPUT_DIR, "preprocessor.joblib")
PREPROCESSED_DATA_PATH = os.path.join(OUTPUT_DIR, "preprocessed_data.joblib")

# def get_latest():
#     resp = requests.get(DEFAULT_MODEL_URL)
#     resp.raise_for_status()
#     data = resp.json()
#     for asset in data["assets"]:
#         if asset["name"] == "model.joblib":
#             return asset["browser_download_url"]
#     raise FileNotFoundError("model.joblib not found")
    
# def download_model(model_path: str):
#     url = get_latest()
#     os.makedirs(os.path.dirname(model_path), exist_ok=True)
#     r = requests.get(url)
#     r.raise_for_status()
#     with open(model_path, "wb") as f:
#         f.write(r.content)

# def load_model():
#     model_path = os.environ.get("MODEL_PATH", "app/output/model.joblib")
#     if not os.path.exists(model_path):
#         download_model(model_path)
#     return joblib.load(model_path)

# model = load_model()

def download_artifacts(output_dir):
    if all(os.path.exists(p) for p in [MODEL_PATH, PREPROCESSOR_PATH, PREPROCESSED_DATA_PATH]):
        return
    resp = requests.get(DEFAULT_MODEL_URL)
    resp.raise_for_status()
    data = resp.json()
    for asset in data["assets"]:
        name = asset["name"]
        download_url = asset["browser_download_url"]
        local_path = os.path.join(output_dir, name)
        if not os.path.exists(local_path):
            r = requests.get(download_url)
            r.raise_for_status()
            with open(local_path, "wb") as f:
                f.write(r.content)

download_artifacts(OUTPUT_DIR)
model = joblib.load(MODEL_PATH)
preprocessor = joblib.load(PREPROCESSOR_PATH)
preprocessed_data = joblib.load(PREPROCESSED_DATA_PATH)

@app.route('/predict', methods=['POST'])
def predict():
    """
    Predict whether an SMS is Spam.
    ---
    consumes:
      - application/json
    parameters:
        - name: input_data
          in: body
          description: message to be classified.
          required: True
          schema:
            type: object
            required: sms
            properties:
                sms:
                    type: string
                    example: This is an example of an SMS.
    responses:
      200:
        description: "The result of the classification: 'spam' or 'ham'."
    """
    input_data = request.get_json()
    sms = input_data.get('sms')
    processed_sms = prepare(sms)
    prediction = model.predict(processed_sms)[0]
    
    res = {
        "result": prediction,
        "classifier": "decision tree",
        "sms": sms
    }
    print(res)
    return jsonify(res)

if __name__ == '__main__':
    #clf = joblib.load('output/model.joblib')
    app.run(host="0.0.0.0", port=8081, debug=True)
