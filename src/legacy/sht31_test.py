import time
import board
import adafruit_sht31d

i2c = board.I2C()
sensor = adafruit_sht31d.SHT31D(i2c)

while True:
    print(f"Temperature: {sensor.temperature:.2f} °C")
    print(f"Humidity: {sensor.relative_humidity:.2f} %")
    time.sleep(2)
