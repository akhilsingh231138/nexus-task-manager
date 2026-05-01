import pandas as pd
import pickle
import os

MODEL_PATH = "hypertention.pkl"
DATA_PATH = "hypertension_dataset.csv"

def load_model():
    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, "rb") as file:
            return pickle.load(file)
    return None

def get_dataset_preview():
    if os.path.exists(DATA_PATH):
        df = pd.read_csv(DATA_PATH)
        return df.head(5).to_dict(orient="records")
    return {"error": "Dataset not found on server."}

def predict(input_data: list):
    model = load_model()
    if not model:
        return {"error": "Model not found on server."}
    try:
        prediction = model.predict([input_data])
        return {"prediction": int(prediction[0])}
    except Exception as e:
        return {"error": str(e)}