#ifndef CONFIG_H
#define CONFIG_H

// Replace these placeholders with your lab Wi-Fi credentials.
// Do not commit real passwords.
#define WIFI_SSID "YOUR_WIFI"
#define WIFI_PASSWORD "YOUR_PASSWORD"

// Backend base URL. On Windows, find the laptop IP with:
//   ipconfig
// Look for IPv4 Address under the active adapter (example: 192.168.1.20).
// The ESP32 and laptop must be on the same Wi-Fi network.
#define SERVER_URL "http://YOUR_LAPTOP_IP:5000"

// Must match backend IOT_DEVICE_TOKEN in backend/.env
#define DEVICE_TOKEN "change-me-device-token"
#define DEVICE_ID "ESP32_001"
#define DEVICE_NAME "ESP32 Clinical Node"

// Display: set USE_OLED or USE_LCD (one should be 1)
#define USE_OLED 1
#define USE_LCD 0

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
#define OLED_ADDRESS 0x3C
#define LCD_ADDRESS 0x27
#define LCD_COLS 16
#define LCD_ROWS 2

#define PIN_LED_GREEN 25
#define PIN_LED_YELLOW 26
#define PIN_LED_RED 27
#define PIN_BUZZER 14
#define PIN_BUTTON 13

#define HEARTBEAT_MS 15000
#define POLL_MS 4000

#endif
