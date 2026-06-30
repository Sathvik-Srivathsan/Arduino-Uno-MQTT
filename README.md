# Arduino Uno → MQTT IR Obstacle Dashboard

Reads an IR obstacle sensor on an Arduino Uno and publishes detection events to HiveMQ Cloud. A live browser dashboard displays status and a rolling detection chart.

## Hardware

| Component | Qty |
|-----------|-----|
| Arduino Uno | 1 |
| IR Obstacle Avoidance Sensor | 1 |
| Male-to-female jumper wires | 3 |

### Wiring

| Sensor | Arduino Uno |
|--------|-------------|
| VCC | 5V |
| GND | GND |
| OUT | A2 |

## Getting Started

### 1. Upload Arduino Firmware

1. Open `arduino_simple_test/arduino_simple_test.ino` in Arduino IDE
2. Select **Board:** Arduino Uno, **Port:** (your COM port)
3. Click Upload

The firmware reads the IR sensor on A2 every 500ms and sends `obstacle=yes` or `obstacle=no` over USB Serial at 9600 baud.

### 2. Set Up Python

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure MQTT Credentials

Copy `.env.example` to `.env` and fill in your HiveMQ Cloud broker details:

```env
MQTT_BROKER=your-cluster-id.s1.eu.hivemq.cloud
MQTT_PORT=8883
MQTT_USERNAME=your_username
MQTT_PASSWORD=your_password
MQTT_TOPIC_PREFIX=arduino/sensor
```

### 4. Run the Bridge

```bash
python bridge.py
```

This auto-detects the Arduino COM port, opens a serial connection, and publishes every reading to HiveMQ Cloud topic `arduino/sensor/data`.

### 5. Open the Dashboard

Open `dashboard.html` in a browser. It connects directly to HiveMQ Cloud via WebSocket and shows live status.

<img width="1064" height="814" alt="image" src="https://github.com/user-attachments/assets/e2ca356a-ca85-4644-bec2-338c790dd20c" />

## Data Flow

```
Arduino (IR sensor on A2)
  ↓ USB Serial @ 9600 baud
bridge.py
  ↓ MQTT over TLS :8883
HiveMQ Cloud Broker
  ↓ WebSocket WSS :8884
dashboard.html (browser)
```
