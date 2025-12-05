import os
import joblib
import numpy as np
from django.conf import settings
from tensorflow.keras.models import load_model

# ------------------------------
# 1. Define paths to ML files
# ------------------------------
ML_FOLDER = os.path.join(settings.BASE_DIR, "disease_prediction", "ml")

MODEL_PATH = os.path.join(ML_FOLDER, "livestock_disease_mlp.h5")
ENCODER_PATH = os.path.join(ML_FOLDER, "label_encoder.pkl")
SCALER_PATH = os.path.join(ML_FOLDER, "scaler.pkl")
SYMPTOM_COLUMNS_PATH = os.path.join(ML_FOLDER, "symptom_columns.pkl")
ANIMAL_COLUMNS_PATH = os.path.join(ML_FOLDER, "animal_columns.pkl")

# ------------------------------
# 2. Load model + encoder + scaler + columns
# ------------------------------
mlp_model = load_model(MODEL_PATH)
label_encoder = joblib.load(ENCODER_PATH)
scaler = joblib.load(SCALER_PATH)
symptom_columns = joblib.load(SYMPTOM_COLUMNS_PATH)
animal_columns = joblib.load(ANIMAL_COLUMNS_PATH)

# ------------------------------
# 3. Prediction function
# ------------------------------
def predict_disease(animal, age, temperature, symptoms_list):
    """
    Predict livestock disease from input features.
    
    Parameters:
    - animal: str ("cow", "buffalo", "sheep")
    - age: float or int
    - temperature: float
    - symptoms_list: list of strings (e.g., ["depression", "painless lumps"])
    
    Returns:
    - predicted disease (string)
    """
    
    # Encode animal
    animal_vector = [1 if col == f"Animal_{animal}" else 0 for col in animal_columns]

    # Encode symptoms
    symptom_vector = [1 if symptom in symptoms_list else 0 for symptom in symptom_columns]

    # Combine features
    X = np.array([age, temperature] + animal_vector + symptom_vector).reshape(1, -1)

    # Scale numerical features (age and temperature are the first two columns)
    X[:, :2] = scaler.transform(X[:, :2])

    # Predict
    pred_probs = mlp_model.predict(X)
    pred_class = np.argmax(pred_probs)

    # Convert back to disease label
    predicted_disease = label_encoder.inverse_transform([pred_class])[0]

    return predicted_disease
