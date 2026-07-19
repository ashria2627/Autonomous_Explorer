# Autonomous Explorer
### Navigate · Detect · Explore

> A low-cost autonomous disaster scout robot that enters hazardous zones before human responders, maps danger in real time using AI, and transmits intelligence over LoRa — built for under ৳10,000.

**BEAR Summit 2026 · CES Pavilion · Silicon River Initiative**

---

## What It Does

Autonomous Explorer is a robot that goes into disaster zones first — collapsed buildings, flood-damaged structures, fire sites — so humans don't have to. It continuously monitors carbon monoxide, air quality, temperature, and humidity. An on-device AI detects dangerous patterns before they cross critical thresholds. All data is transmitted wirelessly over LoRa (no WiFi needed) to a live cloud dashboard accessible from any device anywhere in the world.

---

## System Architecture

```
Robot ESP32 (sensors + AI)
    ↓ LoRa (up to 10km, no infrastructure)
Receiver ESP32
    ↓ WiFi → HTTP POST
Cloud Server (Railway)
    ↓
Live Dashboard (any browser, any device)
    +
ESP32-CAM (live video stream)
```

---

## Hardware

| Component | Model | Purpose |
|-----------|-------|---------|
| Microcontroller | ESP32 Dev Module | Main brain + sensors |
| Gas Sensor | MQ-7 | Carbon monoxide detection |
| Air Quality Sensor | MQ-135 | CO2 + air quality |
| Temp/Humidity | DHT11 | Environmental monitoring |
| Wireless | LoRa Ra-02 SX1278 433MHz | Long-range communication |
| Camera | ESP32-CAM AI Thinker | Live video stream |
| Motors | 4x DC Gear Motor 600RPM | Movement |
| Motor Driver | BTS7960B DC 43A | Motor control |
| Distance Sensors | HC-SR04 x3 | Obstacle avoidance |
| Battery | Li-Po 11.1V | Power |
| Chassis | 4WD Acrylic | Structure |

**Total cost: ~৳10,000**

---

## Software Files

| File | Upload To | Purpose |
|------|-----------|---------|
| `MAIN.ino` | Robot ESP32 | Sensors + AI + LoRa transmit |
| `receiver_cloud.ino` | Receiver ESP32 | Receive LoRa → send to cloud |
| `dashboard_cloud.py` | Railway (cloud) | Live web dashboard |
| `esp32cam.ino` | ESP32-CAM | Live video stream |
| `requirements.txt` | Railway | Python dependencies |
| `Procfile` | Railway | Deployment config |

---

## Wiring

### Robot ESP32 — Sensors
```
MQ-7    → Pin 34
MQ-135  → Pin 35
DHT11   → Pin 4
```

### Robot ESP32 — LoRa Ra-02
```
VCC  → 3.3V
GND  → GND
SCK  → Pin 18
MISO → Pin 19
MOSI → Pin 23
NSS  → Pin 5
RST  → Pin 14
DIO0 → Pin 2
```

### ESP32-CAM — Upload Mode
```
5V   → VCC
GND  → GND
U0R  → TX
U0T  → RX
GND  → IO0  ← disconnect after upload
```

---


## How the AI Works

The robot uses Z-score anomaly detection — no training data needed, no internet required.

On startup it takes 20 readings to learn what "normal" looks like in that environment. From then on, if any sensor reading deviates sharply from the learned pattern, it flags a DANGER alert — even before readings cross a fixed threshold.

```
Normal: readings stable → All Clear
Anomaly: pattern shifts sharply → DANGER
```

The robot adapts to any environment automatically.

---

## Dashboard Features

- Live sensor readings (CO, Air Quality, Temperature, Humidity)
- AI anomaly alerts with blinking danger indicator
- Auto-detects new robots when they power on
- Live camera feed per robot (toggle on/off)
- Fleet overview — total bots, danger count, average temp
- Responsive — works on mobile, tablet, desktop
- Accessible from any device via Railway URL

---


Navigate. Detect. Explore.