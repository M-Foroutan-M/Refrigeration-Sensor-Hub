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

MOVEMENT_THRESHOLD_METERS = 300
ROUTE_CHECK_INTERVAL = 60

ORS_API_KEY = os.getenv("ORS_API_KEY")
if ORS_API_KEY is None:
    raise Exception("ORS_API_KEY not set in environment variables.")

BASE_DATA_DIR = os.path.expanduser("~/Refrigeration-Sensor-Hub/data")
os.makedirs(BASE_DATA_DIR, exist_ok=True)

# ============================================================
# GPIO
# ============================================================

DOOR_PIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(DOOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# ============================================================
# SHT31
# ============================================================

i2c = board.I2C()
sht31 = SHT31D(i2c)

# ============================================================
# GPS THREAD
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
# UTILITY FUNCTIONS
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


def geocode_postcode(postcode):
    url = "https://api.openrouteservice.org/geocode/search"

    headers = {"Authorization": ORS_API_KEY}

    params = {
        "text": postcode,
        "size": 1
    }

    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    coords = data["features"][0]["geometry"]["coordinates"]
    return coords[1], coords[0]  # lat, lon


def get_coordinates_from_input(label):
    user_input = input(f"Enter {label} (lat,lon OR postcode): ").strip()

    if "," in user_input:
        lat, lon = user_input.split(",")
        return float(lat), float(lon)
    else:
        return geocode_postcode(user_input)


def get_route_info(lat1, lon1, lat2, lon2):
    url = "https://api.openrouteservice.org/v2/directions/driving-car"

    headers = {
        "Authorization": ORS_API_KEY,
        "Content-Type": "application/json"
    }

    body = {
        "coordinates": [
            [lon1, lat1],
            [lon2, lat2]
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
# ASK USER FOR DESTINATIONS
# ============================================================

print("Insert three destinations.")

dest1 = get_coordinates_from_input("Destination 1")
dest2 = get_coordinates_from_input("Destination 2")
dest3 = get_coordinates_from_input("Destination 3")

print("Destinations confirmed:")
print(dest1, dest2, dest3)

# ============================================================
# MAIN LOOP
# ============================================================

last_route_time = 0
last_lat = None
last_lon = None

while True:

    with gps_lock:
        gps_data = latest_gps.copy()

    route_data = None
    current_time = time.time()

    if gps_data["fix"]:

        if last_lat is None:
            movement = MOVEMENT_THRESHOLD_METERS + 1
        else:
            movement = distance_between(
                last_lat,
                last_lon,
                gps_data["latitude"],
                gps_data["longitude"]
            )

        if (movement > MOVEMENT_THRESHOLD_METERS and
            current_time - last_route_time > ROUTE_CHECK_INTERVAL):

            try:
                leg1 = get_route_info(
                    gps_data["latitude"], gps_data["longitude"],
                    dest1[0], dest1[1]
                )

                leg2 = get_route_info(
                    dest1[0], dest1[1],
                    dest2[0], dest2[1]
                )

                leg3 = get_route_info(
                    dest2[0], dest2[1],
                    dest3[0], dest3[1]
                )

                route_data = {
                    "current_to_dest1": leg1,
                    "dest1_to_dest2": leg2,
                    "dest2_to_dest3": leg3
                }

                last_lat = gps_data["latitude"]
                last_lon = gps_data["longitude"]
                last_route_time = current_time

                print("Multi-leg Route Updated:", route_data)

            except Exception as e:
                print("Routing Error:", e)

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
