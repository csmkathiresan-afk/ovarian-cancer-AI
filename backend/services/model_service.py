from pathlib import Path

import joblib
import numpy as np
from tensorflow import keras

from config import MODEL_DIR
from schemas.prediction_schema import FEATURE_ORDER

_model = None
_scaler = None


def load_model_artifacts() -> None:
    global _model, _scaler
    model_path = MODEL_DIR / "ovarian_cancer_metadata_model.keras"
    scaler_path = MODEL_DIR / "scaler.pkl"
    if not model_path.exists() or not scaler_path.exists():
        raise FileNotFoundError(
            "Trained model or scaler missing. Run backend/scripts/train_model.py once "
            "to create ovarian_cancer_metadata_model.keras and scaler.pkl."
        )
    _model = keras.models.load_model(model_path)
    _scaler = joblib.load(scaler_path)


def model_ready() -> bool:
    return _model is not None and _scaler is not None


def predict_probability(feature_values: list[float]) -> float:
    if not model_ready():
        load_model_artifacts()
    if len(feature_values) != len(FEATURE_ORDER):
        raise ValueError("Feature vector length does not match training feature order.")
    array = np.array([feature_values], dtype=np.float32)
    scaled = _scaler.transform(array)
    probability = float(_model.predict(scaled, verbose=0)[0][0])
    return max(0.0, min(1.0, probability))


def metrics_payload() -> dict:
    metrics_path = Path(MODEL_DIR / "metrics.json")
    if metrics_path.exists():
        import json

        return json.loads(metrics_path.read_text(encoding="utf-8"))
    return {
        "available": False,
        "message": "No saved evaluation metrics were found next to the trained model.",
    }
