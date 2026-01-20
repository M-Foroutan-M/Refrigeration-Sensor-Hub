import RPi.GPIO as GPIO
import time

DOOR_PIN = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(DOOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

try:
    while True:
        state = GPIO.input(DOOR_PIN)
        print("Door OPEN" if state else "Door CLOSED")
        time.sleep(1)
except KeyboardInterrupt:
    GPIO.cleanup()
