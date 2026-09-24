# ESP32 Clinical Node

Arduino firmware for the Ovarian Cancer AI research prototype. The board does **not** diagnose disease. It posts clinical metadata to the laptop API and shows a **risk assessment** on OLED or LCD.

## Hardware

| Part | Notes |
| --- | --- |
| ESP32 development board | Wi-Fi required |
| 0.96" SSD1306 OLED (I2C) | Default display |
| 16x2 I2C LCD | Optional; set `USE_LCD 1` in `config.h` |
| Green / yellow / red LEDs | Use series resistors (~220Ω) |
| Active buzzer | GPIO 14 |
| Push button | GPIO 13 to GND, internal pull-up |

## Wiring

ESP32 → OLED

- VCC → 3.3V
- GND → GND
- SDA → GPIO 21
- SCL → GPIO 22

LEDs

- Green → GPIO 25
- Yellow → GPIO 26
- Red → GPIO 27

Buzzer

- Signal → GPIO 14
- GND → GND

Button

- One side → GPIO 13
- Other side → GND

## Configuration

Edit `config.h`:

1. `WIFI_SSID` / `WIFI_PASSWORD` — lab network (do not commit real secrets).
2. `SERVER_URL` — `http://LAPTOP_IPV4:5000`. On Windows run `ipconfig` and copy the IPv4 address.
3. `DEVICE_TOKEN` — must match `IOT_DEVICE_TOKEN` in `backend/.env`.
4. `USE_OLED` / `USE_LCD` — enable one display type.

## Libraries (Arduino Library Manager)

- ArduinoJson
- Adafruit GFX
- Adafruit SSD1306
- LiquidCrystal_I2C (only if LCD mode is enabled)

## Demo mode

Press the button to cycle three predefined patient profiles and POST `/iot/predict`.

The dashboard **Send to ESP32** button queues a profile. The firmware polls `/iot/pending/ESP32_001` every few seconds.

## Display copy (do not change)

Use risk language only: `LOW RISK`, `MEDIUM RISK`, `HIGH RISK`, then `CONSULT CLINICIAN`. Never show “Cancer confirmed”.
