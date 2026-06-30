import paho.mqtt.client as mqtt
import ssl
import json
import os
import sys
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

BROKER = os.environ.get("MQTT_BROKER")
PORT = int(os.environ.get("MQTT_PORT", 8883))
USERNAME = os.environ.get("MQTT_USERNAME")
PASSWORD = os.environ.get("MQTT_PASSWORD")
TOPIC = os.environ.get("MQTT_TOPIC_PREFIX", "arduino/sensor") + "/#"

if not all([BROKER, USERNAME, PASSWORD]):
    print("[ERROR] Missing MQTT credentials. Set MQTT_BROKER, MQTT_USERNAME, and MQTT_PASSWORD in .env or environment variables.")
    sys.exit(1)


def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(f"[CONNECTED] Subscribed to {TOPIC}")
        client.subscribe(TOPIC)
    else:
        print(f"[ERROR] Connection failed (rc={rc})")


def on_message(client, userdata, msg):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] Topic: {msg.topic}")
    try:
        data = json.loads(msg.payload)
        print(f"       Payload: {json.dumps(data, indent=2)}")
    except Exception:
        print(f"       Payload: {msg.payload.decode()}")
    print("-" * 50)


def main():
    print("=" * 50)
    print("MQTT SUBSCRIBER — HiveMQ Cloud")
    print(f"Broker: {BROKER}:{PORT}")
    print(f"Topic:  {TOPIC}")
    print("=" * 50)

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="pc_subscriber_1")
    client.tls_set(tls_version=ssl.PROTOCOL_TLS)
    client.username_pw_set(USERNAME, PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(BROKER, PORT, keepalive=60)
        client.loop_forever()
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] Disconnecting...")
        client.disconnect()
    except Exception as e:
        print(f"[ERROR] {e}")


if __name__ == "__main__":
    main()
