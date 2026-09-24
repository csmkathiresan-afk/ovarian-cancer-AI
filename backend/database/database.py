from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from config import get_settings

settings = get_settings()
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String(64), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class PredictionHistory(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String(64), index=True, nullable=False)
    device_id = Column(String(64), nullable=True)
    age = Column(Float, nullable=False)
    ca125 = Column(Float, nullable=False)
    tumor_size = Column(Float, nullable=False)
    menopause = Column(Integer, nullable=False)
    family_history = Column(Integer, nullable=False)
    ascites = Column(Integer, nullable=False)
    bilateral = Column(Integer, nullable=False)
    solid_component = Column(Integer, nullable=False)
    septation = Column(Integer, nullable=False)
    prediction = Column(Integer, nullable=False)
    classification = Column(String(32), nullable=False)
    probability = Column(Float, nullable=False)
    risk_level = Column(String(32), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


class IoTDevice(Base):
    __tablename__ = "iot_devices"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(64), unique=True, index=True, nullable=False)
    device_name = Column(String(128), nullable=False, default="ESP32 Device")
    ip_address = Column(String(64), nullable=True)
    wifi_signal = Column(Integer, nullable=True)
    status = Column(String(32), nullable=False, default="offline")
    last_prediction = Column(String(32), nullable=True)
    last_seen = Column(DateTime, nullable=True)
    pending_payload = Column(String, nullable=True)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
