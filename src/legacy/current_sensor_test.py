import time
import board
from adafruit_ina219 import INA219

i2c = board.I2C()
ina = INA219(i2c)

while True:
    print(f"Voltage: {ina.bus_voltage:.2f} V")
    print(f"Current: {ina.current:.2f} mA")
    time.sleep(2)
