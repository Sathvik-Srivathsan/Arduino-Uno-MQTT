import serial
import serial.tools.list_ports
import paho.mqtt.client as mqtt
import time
import json
import ssl
import sys
import os
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

BROKER = os.environ.get("MQTT_BROKER")
PORT = int(os.environ.get("MQTT_PORT", 8883))
USERNAME = os.environ.get("MQTT_USERNAME")
PASSWORD = os.environ.get("MQTT_PASSWORD")
TOPIC_PREFIX = os.environ.get("MQTT_TOPIC_PREFIX", "arduino/sensor")

if not all([BROKER, USERNAME, PASSWORD]):
    print("[ERROR] Missing MQTT credentials. Set MQTT_BROKER, MQTT_USERNAME, and MQTT_PASSWORD in .env or environment variables.")
    sys.exit(1)

RECONNECT_INTERVAL = 5


def find_arduino_port():
    ports = serial.tools.list_ports.comports()
    for p in ports:
        desc = p.description.lower()
        if (
            "arduino" in desc
            or "ch340" in desc
            or "cp210" in desc
            or "ftdi" in desc
            or "usb serial" in desc
        ):
            return p.device
    if ports:
        return ports[0].device
    return None


def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(f"[MQTT] Connected to HiveMQ Cloud as {USERNAME}")
        client.subscribe(f"{TOPIC_PREFIX}/#")
    else:
        print(f"[MQTT] Connection failed (rc={rc})")


def on_disconnect(client, userdata, flags, rc, properties=None):
    print(f"[MQTT] Disconnected (rc={rc}), reconnecting in {RECONNECT_INTERVAL}s...")


def on_message(client, userdata, msg):
    print(f"[MQTT] Received on {msg.topic}: {msg.payload.decode()}")


def main():
    print("=" * 50)
    print("ARDUINO → HIVEMQ CLOUD BRIDGE")
    print("=" * 50)

    arduino_port = find_arduino_port()
    if not arduino_port:
        print("[ERROR] No Arduino found. Connect your Arduino via USB.")
        print("  Tips: Check drivers (CH340/FTDI), check cable, check Device Manager")
        sys.exit(1)
    print(f"[SERIAL] Found Arduino on {arduino_port}")

    try:
        ser = serial.Serial(arduino_port, 9600, timeout=2)
        time.sleep(2)
        print(f"[SERIAL] Opened {arduino_port} @ 9600 baud")
    except Exception as e:
        print(f"[ERROR] Could not open {arduino_port}: {e}")
        sys.exit(1)

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="arduino_bridge_pc")
    client.tls_set(tls_version=ssl.PROTOCOL_TLS)
    client.username_pw_set(USERNAME, PASSWORD)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message

    try:
        print(f"[MQTT] Connecting to {BROKER}:{PORT}...")
        client.connect(BROKER, PORT, keepalive=60)
        client.loop_start()
    except Exception as e:
        print(f"[ERROR] MQTT connection failed: {e}")
        ser.close()
        sys.exit(1)

    print("\n[READY] Listening to Arduino. Publishing to HiveMQ Cloud.")
    print(f"       Topic: {TOPIC_PREFIX}/data")
    print("       Press Ctrl+C to stop.\n")

    try:
        while True:
            if ser.in_waiting:
                raw = ser.readline()
                try:
                    line = raw.decode("utf-8", errors="replace").strip()
                except Exception:
                    line = str(raw)

                if line:
                    ts = datetime.now().strftime("%H:%M:%S")
                    print(f"[{ts}] Arduino: {line}")

                    payload = json.dumps({
                        "raw": line,
                        "timestamp": time.time()
                    })
                    client.publish(f"{TOPIC_PREFIX}/data", payload, qos=1)
            else:
                time.sleep(0.05)
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] Stopping...")
    finally:
        client.loop_stop()
        client.disconnect()
        ser.close()
        print("[SHUTDOWN] Done.")


if __name__ == "__main__":
    main()
