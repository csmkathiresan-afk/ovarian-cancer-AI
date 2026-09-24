from pydantic import BaseModel, Field


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


class ClinicalFeatures(BaseModel):
    age: float = Field(..., ge=1, le=120)
    ca125: float = Field(..., ge=0, le=20000)
    tumor_size: float = Field(..., ge=0, le=50)
    menopause: int = Field(..., ge=0, le=1)
    family_history: int = Field(..., ge=0, le=1)
    ascites: int = Field(..., ge=0, le=1)
    bilateral: int = Field(..., ge=0, le=1)
    solid_component: int = Field(..., ge=0, le=1)
    septation: int = Field(..., ge=0, le=1)

    def as_feature_vector(self) -> list[float]:
        return [
            self.age,
            self.ca125,
            self.tumor_size,
            self.menopause,
            self.family_history,
            self.ascites,
            self.bilateral,
            self.solid_component,
            self.septation,
        ]


class PredictRequest(ClinicalFeatures):
    patient_id: str = Field(default="WEB-PATIENT", min_length=1, max_length=64)
    device_id: str | None = Field(default="WEB_DASHBOARD", max_length=64)


class PredictResponse(BaseModel):
    prediction: int
    classification: str
    probability: float
    risk_level: str
    patient_id: str
    timestamp: str
    disclaimer: str


class IoTPredictRequest(ClinicalFeatures):
    device_id: str = Field(default="ESP32_001", min_length=1, max_length=64)
    patient_id: str = Field(default="IOT-PATIENT", min_length=1, max_length=64)
    wifi_signal: int | None = None
    ip_address: str | None = None


class IoTPredictResponse(BaseModel):
    success: bool
    prediction: int
    classification: str
    probability: float
    risk_level: str
    disclaimer: str


class DeviceRegisterRequest(BaseModel):
    device_id: str = Field(..., min_length=1, max_length=64)
    device_name: str = Field(default="ESP32 Clinical Node", max_length=128)
    ip_address: str | None = None
    wifi_signal: int | None = None


class HeartbeatRequest(BaseModel):
    device_id: str
    wifi_signal: int | None = None
    ip_address: str | None = None
    last_prediction: str | None = None


class PushToDeviceRequest(ClinicalFeatures):
    device_id: str = Field(default="ESP32_001")
    patient_id: str = Field(default="DEMO-PUSH")
