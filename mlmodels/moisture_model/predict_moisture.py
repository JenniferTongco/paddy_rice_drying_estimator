from pathlib import Path
import joblib
import numpy as np

# Automatically find the base directory of the script
BASE_DIR = Path(__file__).resolve().parent

# Model paths
MODEL_PATH = BASE_DIR / "moisture_content_model.joblib"
SCALER_PATH = BASE_DIR / "moisture_content_scaler.joblib"

def load_moisture_model():
    moisture_model = joblib.load(MODEL_PATH)
    moisture_scaler = joblib.load(SCALER_PATH)
    return moisture_model, moisture_scaler

def predict_moisture(capacitive, temperature, humidity):
    model, scaler = load_moisture_model()

    combined_features = np.array([
        float(capacitive),
        float(temperature),
        float(humidity)
    ]).reshape(1, -1)
    
    # Scale the features
    combined_features_scaled = scaler.transform(combined_features)

    # Predict and return rounded integer
    moisture_content = model.predict(combined_features_scaled)
    return int(round(moisture_content[0]))
