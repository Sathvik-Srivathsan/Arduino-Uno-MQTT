# Arduino Uno → MQTT IR Obstacle Dashboard

Reads an IR obstacle sensor on an Arduino Uno and publishes detection events to HiveMQ Cloud. A live browser dashboard displays status and a rolling detection chart.

## Hardware

| Component | Qty |
|-----------|-----|
| Arduino Uno | 1 |
| IR Obstacle Avoidance Sensor | 1 |
| Male-to-female jumper wires | 3 |

No breadboard needed — wire directly.

### Wiring

| Sensor | Arduino Uno |
|--------|-------------|
| VCC | 5V |
| GND | GND |
| OUT | A2 |

Adjust the potentiometer on the sensor to set the detection range. When an obstacle is within range, OUT goes LOW.

## Getting Started

### 1. Set Up HiveMQ Cloud

1. Sign up at [console.hivemq.com](https://console.hivemq.com) (free serverless cluster, no credit card)
2. Create a cluster and a set of MQTT credentials

### 2. Upload Arduino Firmware

1. Open `arduino_simple_test/arduino_simple_test.ino` in Arduino IDE
2. Select **Board:** Arduino Uno, **Port:** (your COM port)
3. Click Upload

The firmware reads the IR sensor on A2 every 500ms and sends `obstacle=yes` or `obstacle=no` over USB Serial at 9600 baud.

### 3. Set Up Python

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Configure MQTT Credentials

Copy `.env.example` to `.env` and fill in your HiveMQ Cloud broker details:

```env
MQTT_BROKER=your-cluster-id.s1.eu.hivemq.cloud
MQTT_PORT=8883
MQTT_USERNAME=your_username
MQTT_PASSWORD=your_password
MQTT_TOPIC_PREFIX=arduino/sensor
```

### 5. Run the Bridge

```bash
python bridge.py
```

Auto-detects the Arduino COM port, opens serial at 9600 baud, connects to HiveMQ Cloud via TLS on port 8883, and publishes each reading as JSON `{"raw": "...", "timestamp": ...}` to `arduino/sensor/data`.

### 6. Run the Subscriber (optional)

```bash
python subscriber.py
```

Subscribes to `arduino/sensor/#` and prints every message to the terminal.

### 7. Open the Dashboard

Open `dashboard.html` in a browser. It connects to HiveMQ Cloud via WebSocket (WSS on port 8884) and shows:

- **Status ring** — green ✓ (clear) or red ⚠ pulsing (obstacle)
- **Bar chart** — rolling 15-minute detection rate
- **Event log** — collapsible, shows each detection with timestamp
- **Connection indicator** — online/offline

<img width="1064" height="814" alt="image" src="https://github.com/user-attachments/assets/e2ca356a-ca85-4644-bec2-338c790dd20c" />

## Data Flow

```
Arduino (IR sensor on A2)
  ↓ USB Serial @ 9600 baud
bridge.py
  ↓ MQTT over TLS :8883
HiveMQ Cloud Broker
  ↙                      ↘
subscriber.py         dashboard.html
(terminal)             (browser, WSS :8884)
```
