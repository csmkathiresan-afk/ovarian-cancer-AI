from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from config import get_settings
from database.database import IoTDevice, get_db
from schemas.prediction_schema import (
    DeviceRegisterRequest,
    HeartbeatRequest,
    IoTPredictRequest,
    IoTPredictResponse,
    PushToDeviceRequest,
)
from services.prediction_service import run_prediction

router = APIRouter(prefix="/iot", tags=["IoT"])
ONLINE_WINDOW = timedelta(seconds=45)


def require_device_token(x_device_token: str | None = Header(default=None)) -> None:
    expected = get_settings().iot_device_token
    if not x_device_token or x_device_token != expected:
        raise HTTPException(status_code=401, detail="Invalid or missing device token.")


def _serialize_device(device: IoTDevice) -> dict:
    now = datetime.now(timezone.utc)
    last_seen = device.last_seen
    online = False
    if last_seen is not None:
        if last_seen.tzinfo is None:
            last_seen = last_seen.replace(tzinfo=timezone.utc)
        online = (now - last_seen) <= ONLINE_WINDOW
    status = "online" if online else "offline"
    return {
        "device_id": device.device_id,
        "device_name": device.device_name,
        "ip_address": device.ip_address,
        "wifi_signal": device.wifi_signal,
        "status": status,
        "last_prediction": device.last_prediction,
        "last_seen": last_seen.isoformat() if last_seen else None,
        "pending_payload": bool(device.pending_payload),
    }


@router.post("/register")
def register_device(
    payload: DeviceRegisterRequest,
    db: Session = Depends(get_db),
    _: None = Depends(require_device_token),
):
    device = db.query(IoTDevice).filter(IoTDevice.device_id == payload.device_id).first()
    now = datetime.now(timezone.utc)
    if device is None:
        device = IoTDevice(
            device_id=payload.device_id,
            device_name=payload.device_name,
            ip_address=payload.ip_address,
            wifi_signal=payload.wifi_signal,
            status="online",
            last_seen=now,
        )
        db.add(device)
    else:
        device.device_name = payload.device_name
        device.ip_address = payload.ip_address
        device.wifi_signal = payload.wifi_signal
        device.status = "online"
        device.last_seen = now
    db.commit()
    return {"success": True, "device": _serialize_device(device)}


@router.post("/heartbeat")
def heartbeat(
    payload: HeartbeatRequest,
    db: Session = Depends(get_db),
    _: None = Depends(require_device_token),
):
    device = db.query(IoTDevice).filter(IoTDevice.device_id == payload.device_id).first()
    if device is None:
        device = IoTDevice(device_id=payload.device_id, device_name=payload.device_id)
        db.add(device)
    now = datetime.now(timezone.utc)
    device.status = "online"
    device.last_seen = now
    if payload.wifi_signal is not None:
        device.wifi_signal = payload.wifi_signal
    if payload.ip_address:
        device.ip_address = payload.ip_address
    if payload.last_prediction:
        device.last_prediction = payload.last_prediction
    db.commit()
    return {"success": True, "device": _serialize_device(device)}


@router.post("/predict", response_model=IoTPredictResponse)
def iot_predict(
    payload: IoTPredictRequest,
    db: Session = Depends(get_db),
    _: None = Depends(require_device_token),
):
    device = db.query(IoTDevice).filter(IoTDevice.device_id == payload.device_id).first()
    now = datetime.now(timezone.utc)
    if device is None:
        device = IoTDevice(
            device_id=payload.device_id,
            device_name=payload.device_id,
            ip_address=payload.ip_address,
            wifi_signal=payload.wifi_signal,
            status="online",
            last_seen=now,
        )
        db.add(device)
        db.flush()
    else:
        device.status = "online"
        device.last_seen = now
        if payload.wifi_signal is not None:
            device.wifi_signal = payload.wifi_signal
        if payload.ip_address:
            device.ip_address = payload.ip_address

    result = run_prediction(db, payload, payload.patient_id, payload.device_id)
    return IoTPredictResponse(
        success=True,
        prediction=result["prediction"],
        classification=result["classification"],
        probability=result["probability"],
        risk_level=result["risk_code"],
        disclaimer=result["disclaimer"],
    )


@router.get("/status")
def iot_status(db: Session = Depends(get_db)):
    devices = db.query(IoTDevice).order_by(IoTDevice.last_seen.desc()).all()
    primary = devices[0] if devices else None
    if primary is None:
        return {
            "device_id": "ESP32_001",
            "status": "offline",
            "wifi_signal": None,
            "last_prediction": None,
            "last_seen": None,
            "devices": [],
        }
    data = _serialize_device(primary)
    data["devices"] = [_serialize_device(item) for item in devices]
    return data


@router.get("/devices")
def list_devices(db: Session = Depends(get_db)):
    devices = db.query(IoTDevice).order_by(IoTDevice.device_id.asc()).all()
    return {"devices": [_serialize_device(item) for item in devices]}


@router.post("/push")
def push_to_device(
    payload: PushToDeviceRequest,
    db: Session = Depends(get_db),
):
    import json

    device = db.query(IoTDevice).filter(IoTDevice.device_id == payload.device_id).first()
    if device is None:
        raise HTTPException(status_code=404, detail="Device is not registered.")
    device.pending_payload = json.dumps(payload.model_dump())
    db.commit()
    return {"success": True, "message": "Patient profile queued for ESP32 polling."}


@router.get("/pending/{device_id}")
def pending_for_device(
    device_id: str,
    db: Session = Depends(get_db),
    _: None = Depends(require_device_token),
):
    import json

    device = db.query(IoTDevice).filter(IoTDevice.device_id == device_id).first()
    if device is None or not device.pending_payload:
        return {"pending": False}
    data = json.loads(device.pending_payload)
    device.pending_payload = None
    db.commit()
    return {"pending": True, "payload": data}
