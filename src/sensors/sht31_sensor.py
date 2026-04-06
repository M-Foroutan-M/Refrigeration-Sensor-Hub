from typing import Dict, Optional

import board
from adafruit_sht31d import SHT31D


class SHT31Sensor:
    def __init__(self):
        self.sensor = None

    def initialize(self) -> None:
        i2c = board.I2C()
        self.sensor = SHT31D(i2c)

    def read(self) -> Dict[str, Optional[float]]:
        if self.sensor is None:
            raise RuntimeError("SHT31Sensor not initialized")

        return {
            "temperature_c": round(self.sensor.temperature, 2),
            "humidity_percent": round(self.sensor.relative_humidity, 2),
        }
