# Hardware Map

This document records the current hardware connected to the Refrigeration Sensor Hub and how each component is used by the software.

## Raspberry Pi

Main controller:

```text
Raspberry Pi
Raspberry Pi OS Lite
Headless operation
```

Project path:

```text
/home/pi/Refrigeration-Sensor-Hub
```

Runtime service:

```text
sensorhub.service
```

Main runtime file:

```text
src/main.py
```

## Hardware Overview

| Hardware            | Interface        | Current Setting             | Software File                   | Status            |
| ------------------- | ---------------- | --------------------------- | ------------------------------- | ----------------- |
| Door sensor         | GPIO             | GPIO 17                     | `src/sensors/door_sensor.py`    | Working           |
| GPS module          | UART             | `/dev/serial0`, 9600 baud   | `src/sensors/gps_sensor.py`     | Working           |
| Inside SHT31        | I2C              | `0x44`                      | `src/sensors/sht31_sensor.py`   | Working           |
| Weather SHT31       | I2C              | `0x45`                      | `src/sensors/sht31_sensor.py`   | Working           |
| DS18B20             | 1-Wire           | GPIO 4                      | `src/sensors/onewire_sensor.py` | Working           |
| PYR20 pyranometer   | USB / Modbus RTU | WCH USB serial, device ID 1 | `src/sensors/uv_sensor.py`      | Working           |
| SIM7600 modem       | USB              | OS managed                  | Network/Tailscale/rclone        | Working           |
| INA219 power sensor | I2C              | `0x40` planned              | `src/sensors/power_sensor.py`   | Future / disabled |

## Door Sensor

Config file:

```text
config/sensors.json
```

Current config:

```json
"door_sensor": {
  "enabled": true,
  "gpio_pin": 17,
  "pull_up": true
}
```

JSON output field:

```json
"door_open": false
```

Meaning:

```text
true = door open
false = door closed
```

## GPS Sensor

Current config:

```json
"gps": {
  "enabled": true,
  "port": "/dev/serial0",
  "baudrate": 9600,
  "timeout_sec": 1
}
```

JSON output field:

```json
"gps": {
  "latitude": 52.4862,
  "longitude": -1.8904,
  "altitude_m": 110.2,
  "fix": true
}
```

If GPS has no fix:

```json
"gps": {
  "latitude": null,
  "longitude": null,
  "altitude_m": null,
  "fix": false
}
```

## Inside SHT31

Current config:

```json
"inside_sht31": {
  "enabled": true,
  "i2c_address": "0x44"
}
```

Purpose:

```text
Measures internal refrigerated compartment temperature and humidity.
```

JSON output location:

```json
"inside": {
  "temperature_c": 22.31,
  "humidity_percent": 46.51
}
```

## Weather SHT31

Current config:

```json
"weather_sht31": {
  "enabled": true,
  "i2c_address": "0x45"
}
```

Purpose:

```text
Measures external/weather station temperature and humidity.
```

JSON output location:

```json
"weather_station": {
  "temperature_c": 22.79,
  "humidity_percent": 46.9
}
```

## I2C Bus Check

Run:

```bash
sudo i2cdetect -y 1
```

Expected result includes:

```text
44
45
```

Meaning:

```text
0x44 = inside SHT31
0x45 = weather SHT31
```

## DS18B20 1-Wire Temperature Sensor

Current config:

```json
"onewire": {
  "enabled": true,
  "gpio_pin": 4,
  "device_ids": [
    "28-0b2551cc5a63"
  ]
}
```

Current detected device:

```text
28-0b2551cc5a63
```

Check device:

```bash
ls /sys/bus/w1/devices/
```

Manual read:

```bash
cat /sys/bus/w1/devices/28-0b2551cc5a63/w1_slave
```

JSON output location:

```json
"inside": {
  "onewire_temperatures": {
    "28-0b2551cc5a63": 22.94
  }
}
```

## PYR20 Pyranometer

The pyranometer is connected through a USB/RS485 Modbus adapter.

Current config:

```json
"uv_sensor": {
  "enabled": true,
  "type": "modbus_pyranometer",
  "port": "/dev/serial/by-id/usb-WCH.CN_USB_Quad_Serial_BCD9BFABCD-if00",
  "baudrate": 9600,
  "device_id": 1,
  "register_address": 0,
  "register_count": 1,
  "unit": "W/m2"
}
```

Stable port:

```text
/dev/serial/by-id/usb-WCH.CN_USB_Quad_Serial_BCD9BFABCD-if00
```

Do not rely on:

```text
/dev/ttyACM0
```

because it may change after reboot.

JSON output location:

```json
"solar_radiation": {
  "solar_radiation_w_m2": 9,
  "unit": "W/m2",
  "status": "ok"
}
```

## USB Devices

Useful commands:

```bash
lsusb
ls -l /dev/serial/by-id/
ls -l /dev/ttyACM*
ls -l /dev/ttyUSB*
```

The pyranometer adapter was identified as:

```text
WCH.CN USB Quad Serial
```

The SIM7600 modem may appear as multiple `ttyUSB` ports when active.

## SIM7600 Modem

Purpose:

```text
Provides 4G internet access for remote access and Google Drive upload.
```

Used for:

```text
Tailscale SSH access
rclone Google Drive upload
OpenRouteService route requests
```

Remote access examples:

```bash
ssh pi@100.76.109.79
```

or when name resolution works:

```bash
ssh pi@pi-sensorhub
```

## INA219 Power Sensor

Current config:

```json
"power_sensor": {
  "enabled": false,
  "type": "ina219",
  "i2c_address": "0x40"
}
```

Current status:

```text
Not implemented yet.
Reserved for future battery, solar PV, or power monitoring.
```

JSON output is currently:

```json
"power": null
```

## Current Working Hardware Chain

The current tested hardware chain is:

```text
Door sensor
GPS
Inside SHT31
Weather SHT31
DS18B20
Pyranometer
SIM7600 network
```

The current tested data chain is:

```text
hardware sensors -> src/main.py -> JSON record -> data/raw -> Google Drive upload
```

## Notes

* Keep `config/sensors.json` updated if a sensor address, device ID, or serial path changes.
* Prefer stable `/dev/serial/by-id/` paths for USB serial devices.
* If a sensor fails, the logger should continue running and record `null` or an error status for that sensor.
* The power monitoring field is present in the data schema but is not implemented yet.
