"""Train the ovarian-cancer metadata DNN once and persist model + scaler + metrics.

This script is the only place the network is fitted. The API loads the saved
artifacts and never retrains during a prediction request.

If a prior clinical dataset is not present, a synthetic research dataset is
generated so the prototype can run end-to-end. Metrics written to metrics.json
are computed from that training run and must not be treated as clinical
performance.
"""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from tensorflow import keras
from tensorflow.keras import layers

FEATURE_ORDER = [
    "Age",
    "CA125",
    "Tumor_Size",
    "Menopause",
    "Family_History",
    "Ascites",
    "Bilateral",
    "Solid_Component",
    "Septation",
]

ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = ROOT / "model"
MODEL_DIR.mkdir(parents=True, exist_ok=True)


def generate_synthetic_dataset(n: int = 2500, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    age = rng.integers(18, 85, size=n)
    menopause = (age >= 50).astype(int)
    family_history = rng.binomial(1, 0.22, size=n)
    ascites = rng.binomial(1, 0.18, size=n)
    bilateral = rng.binomial(1, 0.25, size=n)
    solid_component = rng.binomial(1, 0.30, size=n)
    septation = rng.binomial(1, 0.35, size=n)
    tumor_size = np.clip(rng.normal(5.5, 3.2, size=n), 0.4, 20.0)
    ca125 = np.clip(rng.lognormal(mean=3.4, sigma=1.1, size=n), 5, 2500)

    latent = (
        0.018 * (age - 40)
        + 0.0045 * ca125
        + 0.22 * tumor_size
        + 0.55 * menopause
        + 0.85 * family_history
        + 0.95 * ascites
        + 0.60 * bilateral
        + 0.80 * solid_component
        + 0.25 * septation
        - 4.2
    )
    prob = 1 / (1 + np.exp(-latent))
    label = (rng.random(n) < prob).astype(int)

    return pd.DataFrame(
        {
            "Age": age,
            "CA125": ca125,
            "Tumor_Size": tumor_size,
            "Menopause": menopause,
            "Family_History": family_history,
            "Ascites": ascites,
            "Bilateral": bilateral,
            "Solid_Component": solid_component,
            "Septation": septation,
            "label": label,
        }
    )


def build_model(input_dim: int) -> keras.Model:
    model = keras.Sequential(
        [
            layers.Input(shape=(input_dim,)),
            layers.Dense(64, activation="relu"),
            layers.Dropout(0.30),
            layers.Dense(32, activation="relu"),
            layers.Dropout(0.30),
            layers.Dense(16, activation="relu"),
            layers.Dense(1, activation="sigmoid"),
        ]
    )
    model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
    return model


def main() -> None:
    df = generate_synthetic_dataset()
    x = df[FEATURE_ORDER].to_numpy(dtype=np.float32)
    y = df["label"].to_numpy(dtype=np.float32)
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, random_state=42, stratify=y
    )
    scaler = StandardScaler()
    x_train_s = scaler.fit_transform(x_train)
    x_test_s = scaler.transform(x_test)

    model = build_model(len(FEATURE_ORDER))
    model.fit(
        x_train_s,
        y_train,
        validation_split=0.15,
        epochs=50,
        batch_size=32,
        verbose=1,
    )

    y_prob = model.predict(x_test_s, verbose=0).ravel()
    y_hat = (y_prob >= 0.5).astype(int)
    metrics = {
        "available": True,
        "dataset": "synthetic_research_prototype",
        "n_samples": int(len(df)),
        "accuracy": float(accuracy_score(y_test, y_hat)),
        "precision": float(precision_score(y_test, y_hat, zero_division=0)),
        "recall": float(recall_score(y_test, y_hat, zero_division=0)),
        "f1": float(f1_score(y_test, y_hat, zero_division=0)),
        "note": (
            "Metrics come from a held-out split of the synthetic research dataset used "
            "to bootstrap this prototype. They are not clinical validation results."
        ),
    }

    model.save(MODEL_DIR / "ovarian_cancer_metadata_model.keras")
    joblib.dump(scaler, MODEL_DIR / "scaler.pkl")
    (MODEL_DIR / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print("Saved model, scaler, and metrics to", MODEL_DIR)
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
