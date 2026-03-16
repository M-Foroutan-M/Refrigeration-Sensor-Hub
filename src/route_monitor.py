import os
import time
import json
import math
import requests
from datetime import datetime, timezone
import threading
import board
import serial
import pynmea2
import RPi.GPIO as GPIO
from adafruit_sht31d import SHT31D

# ============================================================
# CONFIGURATION
# ============================================================

DESTINATION_LAT = 52.4062   # <-- CHANGE THIS
DESTINATION_LON = -1.8004   # <-- CHANGE THIS

MOVEMENT_THRESHOLD_METERS = 300
ROUTE_CHECK_INTERVAL = 60  # seconds

ORS_API_KEY = os.getenv("ORS_API_KEY")
if ORS_API_KEY is None:
    raise Exception("ORS_API_KEY not set in environment variables.")

# ============================================================
# GPIO SETUP
# ============================================================

DOOR_PIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(DOOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# ============================================================
# DATA DIRECTORY
# ============================================================

BASE_DATA_DIR = os.path.expanduser("~/Refrigeration-Sensor-Hub/data")
os.makedirs(BASE_DATA_DIR, exist_ok=True)

# ============================================================
# I2C SENSOR
# ============================================================

i2c = board.I2C()
sht31 = SHT31D(i2c)

# ============================================================
# GPS SETUP
# ============================================================

gps_serial = serial.Serial('/dev/serial0', 9600, timeout=1)

latest_gps = {
    "latitude": None,
    "longitude": None,
    "altitude_m": None,
    "fix": False
}

gps_lock = threading.Lock()

def gps_reader():
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

threading.Thread(target=gps_reader, daemon=True).start()

# ============================================================
# ROUTE FUNCTIONS
# ============================================================

def distance_between(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi/2)**2 + \
        math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2

    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1-a))


def get_route_info(current_lat, current_lon):

    url = "https://api.openrouteservice.org/v2/directions/driving-car"

    headers = {
        "Authorization": ORS_API_KEY,
        "Content-Type": "application/json"
    }

    body = {
        "coordinates": [
            [current_lon, current_lat],
            [DESTINATION_LON, DESTINATION_LAT]
        ],
        "preference": "fastest"
    }

    response = requests.post(url, headers=headers, json=body)
    data = response.json()

    summary = data['routes'][0]['summary']

    return {
        "distance_km": round(summary['distance'] / 1000, 2),
        "duration_min": round(summary['duration'] / 60, 1)
    }

# ============================================================
# MAIN LOOP
# ============================================================

last_route_check_time = 0
last_route_lat = None
last_route_lon = None
cached_route = None

while True:

    with gps_lock:
        gps_data = latest_gps.copy()

    route_data = None

    current_time = time.time()

    if gps_data["fix"]:

        if last_route_lat is None:
            movement = MOVEMENT_THRESHOLD_METERS + 1
        else:
            movement = distance_between(
                last_route_lat,
                last_route_lon,
                gps_data["latitude"],
                gps_data["longitude"]
            )

        if (movement > MOVEMENT_THRESHOLD_METERS and
            current_time - last_route_check_time > ROUTE_CHECK_INTERVAL):

            try:
                route_data = get_route_info(
                    gps_data["latitude"],
                    gps_data["longitude"]
                )

                cached_route = route_data
                last_route_lat = gps_data["latitude"]
                last_route_lon = gps_data["longitude"]
                last_route_check_time = current_time

                print("Route Updated:", route_data)

            except Exception as e:
                print("Route API Error:", e)

        else:
            route_data = cached_route

    data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "temperature_c": round(sht31.temperature, 2),
        "humidity_percent": round(sht31.relative_humidity, 2),
        "door_open": not GPIO.input(DOOR_PIN),
        "gps": gps_data,
        "route": route_data
    }

    filename = os.path.join(
        BASE_DATA_DIR,
        f"log_{datetime.utcnow().date()}.json"
    )

    with open(filename, "a") as f:
        f.write(json.dumps(data) + "\n")

    print(data)
    time.sleep(5)
