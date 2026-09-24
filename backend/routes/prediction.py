from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.database import get_db
from schemas.prediction_schema import PredictRequest, PredictResponse
from services.prediction_service import run_prediction

router = APIRouter(tags=["Prediction"])


@router.post("/predict", response_model=PredictResponse)
def predict(payload: PredictRequest, db: Session = Depends(get_db)):
    result = run_prediction(db, payload, payload.patient_id, payload.device_id)
    return PredictResponse(
        prediction=result["prediction"],
        classification=result["classification"],
        probability=result["probability"],
        risk_level=result["risk_level"],
        patient_id=result["patient_id"],
        timestamp=result["timestamp"],
        disclaimer=result["disclaimer"],
    )
