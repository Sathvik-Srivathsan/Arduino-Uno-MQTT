import serial
import serial.tools.list_ports
import time


def list_ports():
    print("=" * 50)
    print("SCANNING COM PORTS...")
    print("=" * 50)
    ports = serial.tools.list_ports.comports()
    if not ports:
        print("No COM ports found.")
        return []
    for p in ports:
        print(f"  Port: {p.device}")
        print(f"  Description: {p.description}")
        print(f"  Manufacturer: {p.manufacturer}")
        print(f"  Hardware ID: {p.hwid}")
        print(f"  Serial #: {p.serial_number}")
        print("-" * 50)
    return ports


def try_connect(port, baudrate=9600, timeout=2):
    try:
        ser = serial.Serial(port, baudrate, timeout=timeout)
        time.sleep(2)
        data = b""
        start = time.time()
        while time.time() - start < timeout:
            if ser.in_waiting:
                chunk = ser.read(ser.in_waiting)
                data += chunk
                start = time.time()
        ser.close()
        return data
    except Exception as e:
        return None


def main():
    ports = list_ports()
    if not ports:
        print("\nNo Arduino detected. Make sure your Arduino Uno is")
        print("connected via USB and has the necessary drivers installed.")
        return

    for p in ports:
        desc_lower = p.description.lower()
        # Heuristic: Arduinos usually mention "arduino" or "ch340"/"cp210x" USB-serial
        is_arduino = (
            "arduino" in desc_lower
            or "ch340" in desc_lower
            or "cp210" in desc_lower
            or "usb serial" in desc_lower
        )
        if is_arduino:
            print(f"\n>>> Trying to connect to {p.device} ({p.description})...")
            for baud in [9600, 115200, 57600, 19200]:
                print(f"    Trying baud rate {baud}...")
                data = try_connect(p.device, baud)
                if data:
                    decoded = data.decode("utf-8", errors="replace").strip()
                    print(f"    Response: {decoded}" if decoded else "    (connected, no data)")
                    break
            print(f"    Device details:")
            print(f"      Port:        {p.device}")
            print(f"      Description: {p.description}")
            print(f"      Manufacturer: {p.manufacturer}")
            print(f"      HW ID:       {p.hwid}")
            print(f"      Serial #:    {p.serial_number}")
            print()


if __name__ == "__main__":
    main()
