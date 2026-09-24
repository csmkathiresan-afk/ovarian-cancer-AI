#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <Wire.h>
#include "config.h"

#if USE_OLED
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);
#endif

#if USE_LCD
#include <LiquidCrystal_I2C.h>
LiquidCrystal_I2C lcd(LCD_ADDRESS, LCD_COLS, LCD_ROWS);
#endif

struct DemoPatient {
  const char* id;
  float age;
  float ca125;
  float tumor_size;
  int menopause;
  int family_history;
  int ascites;
  int bilateral;
  int solid_component;
  int septation;
};

DemoPatient demos[] = {
  {"DEMO-A", 32, 18, 2.1, 0, 0, 0, 0, 0, 0},
  {"DEMO-B", 48, 85, 6.0, 0, 1, 0, 1, 0, 1},
  {"DEMO-C", 62, 600, 11.5, 1, 1, 1, 1, 1, 0}
};

int demoIndex = 0;
unsigned long lastHeartbeat = 0;
unsigned long lastPoll = 0;
unsigned long buzzerUntil = 0;
int buzzerBeepsLeft = 0;
unsigned long nextBeepToggle = 0;
bool buzzerState = false;
String lastRisk = "-";

void showLines(const char* line1, const char* line2, const char* line3 = "", const char* line4 = "") {
#if USE_OLED
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.println(line1);
  display.println("------------");
  display.println(line2);
  if (strlen(line3)) display.println(line3);
  if (strlen(line4)) display.println(line4);
  display.display();
#endif
#if USE_LCD
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print(line1);
  lcd.setCursor(0, 1);
  lcd.print(line2);
#endif
}

void displayPrediction(const char* risk, float probability) {
  char probLine[24];
  snprintf(probLine, sizeof(probLine), "Probability:");
  char pct[16];
  snprintf(pct, sizeof(pct), "%d%%", (int)round(probability * 100.0f));

  if (strcmp(risk, "HIGH") == 0) {
    showLines("OVARIAN AI", "HIGH RISK", probLine, pct);
#if USE_LCD
    delay(20);
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("HIGH RISK");
    lcd.setCursor(0, 1);
    char lcd2[17];
    snprintf(lcd2, sizeof(lcd2), "PROB: %d%%", (int)round(probability * 100.0f));
    lcd.print(lcd2);
#endif
  } else if (strcmp(risk, "MEDIUM") == 0) {
    showLines("OVARIAN AI", "MEDIUM RISK", probLine, pct);
#if USE_LCD
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("OVARIAN AI");
    lcd.setCursor(0, 1);
    lcd.print("MEDIUM RISK");
#endif
  } else {
    showLines("OVARIAN AI", "LOW RISK", probLine, pct);
#if USE_LCD
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("OVARIAN AI");
    lcd.setCursor(0, 1);
    lcd.print("LOW RISK");
#endif
  }

  delay(1800);
  showLines("OVARIAN AI", "CONSULT", "CLINICIAN", "");
}

void updateLED(const char* risk) {
  digitalWrite(PIN_LED_GREEN, LOW);
  digitalWrite(PIN_LED_YELLOW, LOW);
  digitalWrite(PIN_LED_RED, LOW);
  if (strcmp(risk, "HIGH") == 0) digitalWrite(PIN_LED_RED, HIGH);
  else if (strcmp(risk, "MEDIUM") == 0) digitalWrite(PIN_LED_YELLOW, HIGH);
  else digitalWrite(PIN_LED_GREEN, HIGH);
}

void triggerBuzzer(const char* risk) {
  if (strcmp(risk, "LOW") == 0) {
    buzzerBeepsLeft = 0;
    digitalWrite(PIN_BUZZER, LOW);
    return;
  }
  buzzerBeepsLeft = (strcmp(risk, "HIGH") == 0) ? 6 : 2;
  nextBeepToggle = millis();
  buzzerState = false;
}

void serviceBuzzer() {
  if (buzzerBeepsLeft <= 0) {
    digitalWrite(PIN_BUZZER, LOW);
    return;
  }
  if (millis() < nextBeepToggle) return;
  buzzerState = !buzzerState;
  digitalWrite(PIN_BUZZER, buzzerState ? HIGH : LOW);
  nextBeepToggle = millis() + 120;
  if (!buzzerState) buzzerBeepsLeft--;
}

bool connectWiFi() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  showLines("OVARIAN AI", "CONNECTING", "WIFI...", "");
  unsigned long start = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - start < 20000) {
    delay(400);
  }
  if (WiFi.status() != WL_CONNECTED) {
    showLines("SERVER OFFLINE", "CHECK WIFI", "", "");
    return false;
  }
  return true;
}

String localIp() {
  return WiFi.localIP().toString();
}

bool checkBackend() {
  if (WiFi.status() != WL_CONNECTED) return false;
  HTTPClient http;
  http.begin(String(SERVER_URL) + "/health");
  http.setTimeout(4000);
  int code = http.GET();
  http.end();
  return code == 200;
}

void showDeviceStatus() {
  char sig[24];
  snprintf(sig, sizeof(sig), "RSSI %d", WiFi.RSSI());
  showLines("OVARIAN AI", WiFi.status() == WL_CONNECTED ? "WIFI OK" : "WIFI FAIL", sig, lastRisk.c_str());
}

void registerDevice() {
  if (WiFi.status() != WL_CONNECTED) return;
  HTTPClient http;
  http.begin(String(SERVER_URL) + "/iot/register");
  http.addHeader("Content-Type", "application/json");
  http.addHeader("X-Device-Token", DEVICE_TOKEN);
  JsonDocument doc;
  doc["device_id"] = DEVICE_ID;
  doc["device_name"] = DEVICE_NAME;
  doc["ip_address"] = localIp();
  doc["wifi_signal"] = WiFi.RSSI();
  String body;
  serializeJson(doc, body);
  http.POST(body);
  http.end();
}

void sendHeartbeat() {
  if (WiFi.status() != WL_CONNECTED) return;
  HTTPClient http;
  http.begin(String(SERVER_URL) + "/iot/heartbeat");
  http.addHeader("Content-Type", "application/json");
  http.addHeader("X-Device-Token", DEVICE_TOKEN);
  JsonDocument doc;
  doc["device_id"] = DEVICE_ID;
  doc["ip_address"] = localIp();
  doc["wifi_signal"] = WiFi.RSSI();
  doc["last_prediction"] = lastRisk;
  String body;
  serializeJson(doc, body);
  http.POST(body);
  http.end();
}

bool sendPredictionRequest(const DemoPatient& patient) {
  if (WiFi.status() != WL_CONNECTED) {
    showLines("SERVER OFFLINE", "CHECK WIFI", "", "");
    return false;
  }
  if (!checkBackend()) {
    showLines("DEVICE OFFLINE", "API FAIL", "", "");
    return false;
  }

  HTTPClient http;
  http.begin(String(SERVER_URL) + "/iot/predict");
  http.addHeader("Content-Type", "application/json");
  http.addHeader("X-Device-Token", DEVICE_TOKEN);

  JsonDocument doc;
  doc["device_id"] = DEVICE_ID;
  doc["patient_id"] = patient.id;
  doc["age"] = patient.age;
  doc["ca125"] = patient.ca125;
  doc["tumor_size"] = patient.tumor_size;
  doc["menopause"] = patient.menopause;
  doc["family_history"] = patient.family_history;
  doc["ascites"] = patient.ascites;
  doc["bilateral"] = patient.bilateral;
  doc["solid_component"] = patient.solid_component;
  doc["septation"] = patient.septation;
  doc["wifi_signal"] = WiFi.RSSI();
  doc["ip_address"] = localIp();

  String body;
  serializeJson(doc, body);
  int code = http.POST(body);
  String response = http.getString();
  http.end();

  if (code != 200) {
    showLines("PREDICTION ERROR", "TRY AGAIN", "", "");
    return false;
  }

  JsonDocument parsed;
  DeserializationError err = deserializeJson(parsed, response);
  if (err || !parsed["success"]) {
    showLines("INVALID INPUT", "CHECK DATA", "", "");
    return false;
  }

  const char* risk = parsed["risk_level"] | "LOW";
  float probability = parsed["probability"] | 0.0f;
  lastRisk = String(risk);
  updateLED(risk);
  triggerBuzzer(risk);
  displayPrediction(risk, probability);
  return true;
}

void pollPending() {
  if (WiFi.status() != WL_CONNECTED) return;
  HTTPClient http;
  http.begin(String(SERVER_URL) + "/iot/pending/" + String(DEVICE_ID));
  http.addHeader("X-Device-Token", DEVICE_TOKEN);
  int code = http.GET();
  String response = http.getString();
  http.end();
  if (code != 200) return;

  JsonDocument parsed;
  if (deserializeJson(parsed, response)) return;
  if (!parsed["pending"]) return;

  DemoPatient incoming;
  incoming.id = "WEB-PUSH";
  incoming.age = parsed["payload"]["age"] | 0;
  incoming.ca125 = parsed["payload"]["ca125"] | 0;
  incoming.tumor_size = parsed["payload"]["tumor_size"] | 0;
  incoming.menopause = parsed["payload"]["menopause"] | 0;
  incoming.family_history = parsed["payload"]["family_history"] | 0;
  incoming.ascites = parsed["payload"]["ascites"] | 0;
  incoming.bilateral = parsed["payload"]["bilateral"] | 0;
  incoming.solid_component = parsed["payload"]["solid_component"] | 0;
  incoming.septation = parsed["payload"]["septation"] | 0;
  sendPredictionRequest(incoming);
}

void setup() {
  Serial.begin(115200);
  pinMode(PIN_LED_GREEN, OUTPUT);
  pinMode(PIN_LED_YELLOW, OUTPUT);
  pinMode(PIN_LED_RED, OUTPUT);
  pinMode(PIN_BUZZER, OUTPUT);
  pinMode(PIN_BUTTON, INPUT_PULLUP);

  Wire.begin(21, 22);
#if USE_OLED
  display.begin(SSD1306_SWITCHCAPVCC, OLED_ADDRESS);
#endif
#if USE_LCD
  lcd.init();
  lcd.backlight();
#endif

  showLines("OVARIAN AI", "PROTOTYPE", "NOT CLINICAL", "");
  if (connectWiFi()) {
    registerDevice();
    showDeviceStatus();
  }
}

void loop() {
  serviceBuzzer();

  if (digitalRead(PIN_BUTTON) == LOW) {
    delay(40);
    if (digitalRead(PIN_BUTTON) == LOW) {
      DemoPatient patient = demos[demoIndex];
      demoIndex = (demoIndex + 1) % 3;
      char label[20];
      snprintf(label, sizeof(label), "DEMO %s", patient.id);
      showLines("OVARIAN AI", label, "SENDING...", "");
      sendPredictionRequest(patient);
      while (digitalRead(PIN_BUTTON) == LOW) {
        serviceBuzzer();
        delay(10);
      }
    }
  }

  if (millis() - lastHeartbeat > HEARTBEAT_MS) {
    lastHeartbeat = millis();
    if (WiFi.status() != WL_CONNECTED) {
      connectWiFi();
    } else {
      sendHeartbeat();
    }
  }

  if (millis() - lastPoll > POLL_MS) {
    lastPoll = millis();
    pollPending();
  }
}
