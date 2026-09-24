from datetime import datetime, timezone

from sqlalchemy.orm import Session

from config import get_settings
from database.database import IoTDevice, Patient, PredictionHistory
from schemas.prediction_schema import ClinicalFeatures
from services.model_service import predict_probability

DISCLAIMER = (
    "AI-generated risk assessment for academic/research demonstration. "
    "This system does not replace professional medical diagnosis."
)


def classify_risk(probability: float) -> tuple[int, str, str]:
    settings = get_settings()
    prediction = 1 if probability >= 0.5 else 0
    classification = "Malignant" if prediction == 1 else "Benign"
    if probability < settings.risk_low_threshold:
        risk = "LOW"
    elif probability <= settings.risk_high_threshold:
        risk = "MEDIUM"
    else:
        risk = "HIGH"
    return prediction, classification, risk


def risk_display_name(risk: str) -> str:
    mapping = {"LOW": "Low Risk", "MEDIUM": "Medium Risk", "HIGH": "High Risk"}
    return mapping.get(risk, risk)


def run_prediction(
    db: Session,
    features: ClinicalFeatures,
    patient_id: str,
    device_id: str | None,
) -> dict:
    probability = predict_probability(features.as_feature_vector())
    prediction, classification, risk = classify_risk(probability)
    now = datetime.now(timezone.utc)

    if patient_id:
        existing = db.query(Patient).filter(Patient.patient_id == patient_id).first()
        if existing is None:
            db.add(Patient(patient_id=patient_id))

    record = PredictionHistory(
        patient_id=patient_id,
        device_id=device_id,
        age=features.age,
        ca125=features.ca125,
        tumor_size=features.tumor_size,
        menopause=features.menopause,
        family_history=features.family_history,
        ascites=features.ascites,
        bilateral=features.bilateral,
        solid_component=features.solid_component,
        septation=features.septation,
        prediction=prediction,
        classification=classification,
        probability=probability,
        risk_level=risk,
        timestamp=now,
    )
    db.add(record)

    if device_id and device_id != "WEB_DASHBOARD":
        device = db.query(IoTDevice).filter(IoTDevice.device_id == device_id).first()
        if device:
            device.last_prediction = risk
            device.last_seen = now
            device.status = "online"

    db.commit()

    return {
        "prediction": prediction,
        "classification": classification,
        "probability": round(probability, 4),
        "risk_level": risk_display_name(risk),
        "risk_code": risk,
        "patient_id": patient_id,
        "device_id": device_id,
        "timestamp": now.isoformat(),
        "disclaimer": DISCLAIMER,
    }
