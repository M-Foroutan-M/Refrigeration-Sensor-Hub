from typing import Dict, Optional
import board
import adafruit_sht31d


class SHT31Sensor:
    def __init__(self, i2c_address: int = 0x44):
        self.i2c_address = i2c_address
        self.sensor = None
        self.i2c = None

    def initialize(self) -> None:
        if self.i2c is None:
            self.i2c = board.I2C()

        self.sensor = adafruit_sht31d.SHT31D(self.i2c, address=self.i2c_address)

    def read(self) -> Dict[str, Optional[float]]:
        if self.sensor is None:
            raise RuntimeError("SHT31Sensor not initialized")

        return {
            "temperature_c": round(self.sensor.temperature, 2),
            "humidity_percent": round(self.sensor.relative_humidity, 2),
        }
