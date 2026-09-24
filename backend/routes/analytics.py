from datetime import datetime, timezone
from collections import Counter

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from config import get_settings
from database.database import IoTDevice, Patient, PredictionHistory, get_db
from services.model_service import metrics_payload
from services.prediction_service import DISCLAIMER

router = APIRouter(tags=["Analytics"])


@router.get("/predictions")
def list_predictions(limit: int = Query(default=50, ge=1, le=500), db: Session = Depends(get_db)):
    rows = (
        db.query(PredictionHistory)
        .order_by(PredictionHistory.timestamp.desc())
        .limit(limit)
        .all()
    )
    return {
        "items": [
            {
                "id": row.id,
                "patient_id": row.patient_id,
                "device_id": row.device_id,
                "age": row.age,
                "ca125": row.ca125,
                "tumor_size": row.tumor_size,
                "prediction": row.prediction,
                "classification": row.classification,
                "probability": row.probability,
                "risk_level": row.risk_level,
                "timestamp": row.timestamp.isoformat() if row.timestamp else None,
            }
            for row in rows
        ]
    }


@router.get("/analytics")
def analytics(db: Session = Depends(get_db)):
    rows = db.query(PredictionHistory).all()
    class_counts = Counter(row.classification for row in rows)
    risk_counts = Counter(row.risk_level for row in rows)
    history = [
        {
            "timestamp": row.timestamp.isoformat() if row.timestamp else None,
            "probability": row.probability,
            "classification": row.classification,
            "risk_level": row.risk_level,
        }
        for row in sorted(rows, key=lambda item: item.timestamp or datetime.min)
    ]
    scatter_ca125 = [{"ca125": row.ca125, "probability": row.probability} for row in rows]
    scatter_tumor = [{"tumor_size": row.tumor_size, "probability": row.probability} for row in rows]

    daily = {}
    for row in rows:
        if not row.timestamp:
            continue
        key = row.timestamp.date().isoformat()
        daily[key] = daily.get(key, 0) + 1
    daily_counts = [{"date": key, "count": daily[key]} for key in sorted(daily)]

    device_activity = (
        db.query(PredictionHistory.device_id, func.count(PredictionHistory.id))
        .group_by(PredictionHistory.device_id)
        .all()
    )

    return {
        "totals": {
            "patients": db.query(func.count(Patient.id)).scalar() or 0,
            "predictions": len(rows),
            "devices": db.query(func.count(IoTDevice.id)).scalar() or 0,
        },
        "prediction_distribution": {
            "Benign": class_counts.get("Benign", 0),
            "Malignant": class_counts.get("Malignant", 0),
        },
        "risk_distribution": {
            "LOW": risk_counts.get("LOW", 0),
            "MEDIUM": risk_counts.get("MEDIUM", 0),
            "HIGH": risk_counts.get("HIGH", 0),
        },
        "history": history,
        "ca125_vs_probability": scatter_ca125,
        "tumor_size_vs_probability": scatter_tumor,
        "daily_counts": daily_counts,
        "device_activity": [
            {"device_id": device_id or "UNKNOWN", "count": count} for device_id, count in device_activity
        ],
    }


@router.get("/model-info")
def model_info():
    settings = get_settings()
    metrics = metrics_payload()
    return {
        "model": "Deep Neural Network",
        "framework": "TensorFlow / Keras",
        "input_features": 9,
        "feature_order": [
            "Age",
            "CA125",
            "Tumor_Size",
            "Menopause",
            "Family_History",
            "Ascites",
            "Bilateral",
            "Solid_Component",
            "Septation",
        ],
        "output": "Binary classification (0 = Benign, 1 = Malignant) used as a research risk score",
        "layers": [
            "Dense 64 + ReLU",
            "Dropout 30%",
            "Dense 32 + ReLU",
            "Dropout",
            "Dense 16 + ReLU",
            "Dense 1 + Sigmoid",
        ],
        "training": {
            "epochs": 50,
            "optimizer": "Adam",
            "loss": "Binary Crossentropy",
        },
        "risk_thresholds": {
            "low_below": settings.risk_low_threshold,
            "high_above": settings.risk_high_threshold,
            "note": "These thresholds are prototype presentation cutoffs and are not clinically validated.",
        },
        "metrics": metrics,
        "disclaimer": DISCLAIMER,
    }


@router.get("/settings")
def settings_view():
    settings = get_settings()
    return {
        "risk_low_threshold": settings.risk_low_threshold,
        "risk_high_threshold": settings.risk_high_threshold,
        "cors_origins": settings.cors_origin_list,
        "note": "Risk thresholds are presentation-only and not clinically validated.",
    }
