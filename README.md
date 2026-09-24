# OVARIAN CANCER AI – Smart IoT Clinical Risk Detection System

Academic and research prototype that connects a **clinical-metadata deep neural network** to a **Flask/FastAPI-style REST API**, a **React dashboard**, and an **ESP32** node with OLED/LCD, LEDs, and a buzzer.

**Prototype for Research & Demonstration – Not for Clinical Diagnosis**

This is not a medical device. Outputs are **risk assessments** for demonstration (low / medium / high presentation bands). The system must never be described as “cancer confirmed”.

## Project Overview

A user (or ESP32 demo profile) submits nine clinical features. The backend applies the **same StandardScaler and feature order used at training time**, runs a saved Keras model, maps probability to a configurable risk band, stores history in SQLite, and can push the result back to the IoT node.

## Features

- Metadata DNN inference without retraining on each request
- FastAPI backend with OpenAPI/Swagger
- React + Vite medical-tech dashboard
- ESP32 Wi-Fi HTTP client, OLED or LCD, RGB-style LEDs, non-blocking buzzer
- Device registration, heartbeat, and dashboard “Send to ESP32”
- Prediction history and analytics charts
- Demo patients A/B/C
- Reference scan page that **does not** feed the DNN
- Input validation, CORS, device token, `.env` secrets, request logging

## Architecture

```
WEB DASHBOARD  --REST-->  PYTHON BACKEND  --Wi-Fi/HTTP-->  ESP32
   React                    validation                         OLED/LCD
                            StandardScaler                     LEDs
                            Keras DNN                          Buzzer
                            SQLite history
```

## AI Model

Architecture:

Input (9 features) → Dense 64 + ReLU → Dropout 30% → Dense 32 + ReLU → Dropout → Dense 16 + ReLU → Dense 1 + Sigmoid

Features (fixed order): Age, CA125, Tumor_Size, Menopause, Family_History, Ascites, Bilateral, Solid_Component, Septation

Target encoding used for training: `0 = Benign`, `1 = Malignant` as a **research label**, not a clinical diagnosis.

Saved artifacts (loaded at API startup):

- `backend/model/ovarian_cancer_metadata_model.keras`
- `backend/model/scaler.pkl`
- `backend/model/metrics.json` (only if produced by `scripts/train_model.py`)

If you already have a trained `.keras` file and scaler from a prior course project, copy them into `backend/model/` instead of running the trainer.

**Do not invent accuracy numbers.** The Model page shows metrics only when `metrics.json` exists.

If no prior dataset is available, `scripts/train_model.py` fits the specified network on a **synthetic research dataset** so the prototype can run. Those metrics are **not** clinical validation.

Risk bands (`RISK_LOW_THRESHOLD`, `RISK_HIGH_THRESHOLD` in `.env`) are **prototype presentation cutoffs**. They do not change model weights and are not clinically validated.

## IoT Architecture

ESP32 joins Wi-Fi, registers with `POST /iot/register`, heartbeats, and posts `POST /iot/predict`. Firmware polls `GET /iot/pending/{device_id}` so the dashboard can queue a profile with **Send to ESP32**.

## Hardware Requirements

- ESP32 development board
- 0.96" SSD1306 OLED (I2C) and/or 16x2 I2C LCD
- Green, yellow, red LEDs with series resistors (~220 Ω)
- Active buzzer
- Push button

## Software Requirements

- Python 3.10+ (3.11 recommended for TensorFlow)
- Node.js 18+
- Arduino IDE (for firmware)
- Windows, macOS, or Linux laptop on the same Wi-Fi as the ESP32

## Installation

Clone or copy this folder, then set up backend and frontend as below.

## Backend Setup

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python scripts\train_model.py
uvicorn app:app --host 0.0.0.0 --port 5000
```

`--host 0.0.0.0` is required so the ESP32 can reach the laptop.

Set `IOT_DEVICE_TOKEN` in `.env` to a private value and copy the same token into `esp32/config.h`.

## Frontend Setup

```powershell
cd frontend
npm install
npm run dev
```

Dashboard: http://127.0.0.1:5173  
Swagger: http://127.0.0.1:5000/docs

## ESP32 Setup

1. Install libraries: ArduinoJson, Adafruit GFX, Adafruit SSD1306, optional LiquidCrystal_I2C.
2. Edit `esp32/config.h`:
   - `WIFI_SSID` / `WIFI_PASSWORD` (do not commit real passwords)
   - `SERVER_URL` such as `http://192.168.1.20:5000`
   - `DEVICE_TOKEN` matching `.env`
   - `USE_OLED` or `USE_LCD`
3. Find the laptop IPv4:
   - Windows: `ipconfig`
   - macOS/Linux: `ip addr` or `ifconfig`
4. Flash `ovarian_iot.ino`.

## Wiring

ESP32 → OLED: VCC→3.3V, GND→GND, SDA→GPIO 21, SCL→GPIO 22  
Green LED→GPIO 25, Yellow→GPIO 26, Red→GPIO 27 (use resistors)  
Buzzer→GPIO 14, Button→GPIO 13 to GND  

The dashboard **Hardware Wiring** page repeats this map.

## API Documentation

Interactive OpenAPI: `/docs` (Swagger UI) and `/redoc`.

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/` | Service banner and disclaimer |
| GET | `/health` | API and model load status |
| POST | `/predict` | Web assessment |
| POST | `/iot/predict` | ESP32 assessment (`X-Device-Token`) |
| GET | `/iot/status` | Primary device + list |
| POST | `/iot/register` | Device registration |
| POST | `/iot/heartbeat` | Keep-alive |
| GET | `/iot/pending/{id}` | Dashboard-to-device queue |
| POST | `/iot/push` | Queue a profile for ESP32 |
| GET | `/predictions` | History |
| GET | `/analytics` | Chart payloads |
| GET | `/model-info` | Architecture + saved metrics only |
| GET | `/settings` | Thresholds |

Web `POST /predict` example response:

```json
{
  "prediction": 1,
  "classification": "Malignant",
  "probability": 0.91,
  "risk_level": "High Risk",
  "patient_id": "PATIENT-C",
  "timestamp": "2026-09-21T16:00:00+00:00",
  "disclaimer": "AI-generated risk assessment..."
}
```

IoT `risk_level` uses `LOW` / `MEDIUM` / `HIGH` for compact OLED text.

## Running the Project

1. Train or copy model artifacts into `backend/model/`.
2. Start uvicorn on port 5000, bound to all interfaces.
3. Start the Vite dashboard.
4. Power the ESP32 on the same LAN.
5. Use Patient Assessment → ANALYZE PATIENT, or press the ESP32 button for demo profiles.

## Demo Mode

- **Patient A**: lower-risk style metadata  
- **Patient B**: mixed / medium-style metadata  
- **Patient C**: Age 62, CA125 600, Tumor 11.5, most binary flags = 1  

**Send to ESP32** queues the current form for `ESP32_001`.

On-device, the button cycles the same three profiles.

## Screenshots

Capture your local dashboard, Swagger `/docs`, OLED result, and LED states during the lab demo and drop images here if you write a report.

## Future Enhancements

- Replace SQLite with PostgreSQL
- TLS reverse proxy
- Role-based access
- Optional imaging model as a **separate** research track (not this DNN)

## Limitations

- Not clinically validated
- Synthetic bootstrap data if no institutional dataset is supplied
- Risk thresholds are presentation-only
- Scan images are visual aids only
- Local HTTP is for a lab network, not production PHI workflows

## Medical Disclaimer

AI-generated risk assessment for academic/research demonstration. This system does not replace professional medical diagnosis. Do not use it for patient care, screening programs, or emergency decisions. Always consult a qualified clinician.

Preferred language: **high-risk prediction**, **low-risk prediction**, **clinical review recommended**. Forbidden language: **cancer confirmed**.
