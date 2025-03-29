from pathlib import Path
import joblib
import numpy as np
import pandas as pd

# Automatically find the base directory of the script
BASE_DIR = Path(__file__).resolve().parent

# Model paths relative to this script's location
MODEL_PATH = BASE_DIR / "drying_time_model.joblib"
SCALER_PATH = BASE_DIR / "drying_time_scaler.joblib"

def load_drying_time_model():
    drying_model = joblib.load(MODEL_PATH)
    drying_scaler = joblib.load(SCALER_PATH)
    return drying_model, drying_scaler


def predict_drying_time(initial_moisture, temperature, humidity, final_moisture):
    model, scaler = load_drying_time_model()
    combined_features = np.array([
        float(initial_moisture),
        float(temperature),
        float(humidity),
        float(final_moisture)
    ]).reshape(1, -1)
    
    # Scale the features
    combined_features_scaled = scaler.transform(combined_features)
    
    # Predict
    predicted_time = model.predict(combined_features_scaled)[0]
    
    # Convert to hours and minutes
    hours = int(predicted_time)
    minutes = int(round((predicted_time - hours) * 60))
    
    return hours, minutes
