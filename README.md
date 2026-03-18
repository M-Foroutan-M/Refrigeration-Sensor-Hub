# Refrigeration-Sensor-Hub

## Project Overview

This project implements a modular, embedded IoT system designed for deployment inside a refrigerated transport van. The system continuously collects environmental, positional, and operational data, stores it locally, and synchronizes it with the cloud.

The architecture prioritizes modularity, reproducibility, and headless operation, making it suitable for embedded sensing platforms, mobile robots, and remote monitoring applications.

---

## System Features

```
Multi-sensor data acquisition (temperature, humidity, GPS, door state, weather condition)
Timestamped JSON logging with date-based file structure
Robust 4G connectivity using SIM7600 (with fallback logic)
Automated data upload to cloud (Google Drive)
Route estimation for mission-aware decision making
Modular software architecture (sensors / services / utils)
Headless operation with systemd auto-start
Designed for real-world deployment (vehicle, vibration, signal loss)
```
---

## Hardware Setup

Core Platform:
```
Raspberry Pi 4 (Raspberry Pi OS Lite, headless)
```

Connectivity:
```
SIM7600G-H 4G LTE USB modem (giffgaff SIM)
```

Sensors:
```
SHT31 (I2C) → internal temperature & humidity
GPS module (UART, NMEA)
Door sensor (GPIO, magnetic contact)
Sensors (Planned / Future)
DS18B20 (1-Wire temperature probes)
External SHT31 (weather station)
PYR20 Pyranometer (UV radiation, weather station)
INA219 (power monitoring)
```
---

## Software Architecture

The system follows a modular service-based architecture:
```
src/
├── main.py
├── sensors/
│   ├── sht31_sensor.py
│   ├── gps_sensor.py
│   ├── door_sensor.py
│   ├── onewire_sensor.py
│   ├── weather_sht31_sensor.py
│   ├── uv_sensor.py
│   └── power_sensor.py
├── services/
│   ├── logger_service.py
│   ├── uploader_service.py
│   ├── route_service.py
│   ├── mission_service.py
│   └── state_service.py
├── utils/
│   ├── file_utils.py
│   ├── time_utils.py
│   └── config_utils.py
```
---

## Configuration

Located in:

```
config/
├── app_config.json
├── mission.json
├── sensors.json
app_config.json
```

Controls:

* sampling interval
* upload interval
* route estimation interval
* feature toggles (route, weather, upload)
* file paths

mission.json:

* mission ID
* van ID
* route destinations
* runtime mission state

sensors.json:

* sensor enable/disable
* hardware configuration (GPIO, I2C, UART)










---

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/legionnnnn/Refrigeration-Sensor-Hub.git
cd Refrigeration-Sensor-Hub
```

### 2. Create Python virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
# For the current state run this code to activate virtual env:
source ~/sensorhub-venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```
---

## Author

Mohammad (Farhad) Foroutan
Aston University
