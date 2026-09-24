Keep the trained Keras model and StandardScaler here:

- ovarian_cancer_metadata_model.keras
- scaler.pkl
- metrics.json (written by scripts/train_model.py)

The API loads these artifacts at startup and does not retrain on each request.
