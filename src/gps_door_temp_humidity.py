import time
import json
from datetime import datetime
import board
import serial
import pynmea2
import RPi.GPIO as GPIO
from adafruit_sht31d import SHT31D

# GPIO
DOOR_PIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(DOOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# I2C Sensors
i2c = board.I2C()
sht31 = SHT31D(i2c)

# GPS
gps = serial.Serial('/dev/serial0', 9600, timeout=1)

def read_gps():
    try:
        line = gps.readline().decode('ascii', errors='replace')
        if line.startswith('$GPGGA'):
            msg = pynmea2.parse(line)
            return {
                "latitude": msg.latitude,
                "longitude": msg.longitude,
                "fix": msg.gps_qual
            }
    except:
        pass
    return {}

while True:
    data = {
        "timestamp": datetime.utcnow().isoformat(),
        "temperature_c": round(sht31.temperature, 2),
        "humidity_percent": round(sht31.relative_humidity, 2),
        "door_state": "open" if GPIO.input(DOOR_PIN) else "closed",
        "gps": read_gps()
    }

    filename = f"../data/log_{datetime.utcnow().date()}.json"
    with open(filename, "a") as f:
        f.write(json.dumps(data) + "\n")

    print(data)
    time.sleep(5)
