import os
import time
import json
from datetime import datetime, timezone
import threading
import board
import serial
import pynmea2
import RPi.GPIO as GPIO
from adafruit_sht31d import SHT31D

# --------------------
# GPIO SETUP
# --------------------
DOOR_PIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(DOOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# --------------------
# DATA DIRECTORY SETUP
# --------------------
BASE_DATA_DIR = os.path.expanduser("~/Refrigeration-Sensor-Hub/data")
os.makedirs(BASE_DATA_DIR, exist_ok=True)

# --------------------
# I2C SENSOR
# --------------------
i2c = board.I2C()
sht31 = SHT31D(i2c)

# --------------------
# GPS SETUP
# --------------------
gps_serial = serial.Serial('/dev/serial0', 9600, timeout=1)

latest_gps = {
    "latitude": None,
    "longitude": None,
    "altitude_m": None,
    "fix": False
}

gps_lock = threading.Lock()

def gps_reader():
    """Continuously read GPS and update latest fix."""
    global latest_gps

    while True:
        try:
            line = gps_serial.readline().decode('ascii', errors='replace')

            if line.startswith('$GPGGA'):
                msg = pynmea2.parse(line)

                with gps_lock:
                    if int(msg.gps_qual) > 0:
                        latest_gps = {
                            "latitude": msg.latitude,
                            "longitude": msg.longitude,
                            "altitude_m": msg.altitude,
                            "fix": True
                        }
                    else:
                        latest_gps = {
                            "latitude": None,
                            "longitude": None,
                            "altitude_m": None,
                            "fix": False
                        }

        except Exception:
            pass

# Start GPS thread
threading.Thread(target=gps_reader, daemon=True).start()

# --------------------
# MAIN LOG LOOP
# --------------------
while True:
    with gps_lock:
        gps_data = latest_gps.copy()

    data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "temperature_c": round(sht31.temperature, 2),
        "humidity_percent": round(sht31.relative_humidity, 2),
        "door_open": not GPIO.input(DOOR_PIN),
        "gps": gps_data
    }

    filename = os.path.join(
    	BASE_DATA_DIR,
    	f"log_{datetime.utcnow().date()}.json"
    )

    with open(filename, "a") as f:
    	f.write(json.dumps(data) + "\n")


    print(data)
    time.sleep(5)
