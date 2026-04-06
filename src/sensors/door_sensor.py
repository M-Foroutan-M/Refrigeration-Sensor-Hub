from typing import Optional

import RPi.GPIO as GPIO


class DoorSensor:
    def __init__(self, gpio_pin: int, pull_up: bool = True):
        self.gpio_pin = gpio_pin
        self.pull_up = pull_up
        self.initialized = False

    def initialize(self) -> None:
        GPIO.setmode(GPIO.BCM)

        if self.pull_up:
            GPIO.setup(self.gpio_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        else:
            GPIO.setup(self.gpio_pin, GPIO.IN)

        self.initialized = True

    def read(self) -> Optional[bool]:
        if not self.initialized:
            raise RuntimeError("DoorSensor not initialized")

        raw_value = GPIO.input(self.gpio_pin)

        # Current hardware logic:
        # low = door open, high = door closed
        return not bool(raw_value)

    def cleanup(self) -> None:
        GPIO.cleanup(self.gpio_pin)
