# Refrigeration-Sensor-Hub

## Overview

Refrigeration-Sensor-Hub is a modular embedded IoT edge platform designed for deployment inside refrigerated transport vehicles.

The system continuously acquires environmental, mission, and positional telemetry from the vehicle, stores structured timestamped data locally, and synchronizes records to cloud storage over a resilient 4G connection.

The architecture is designed for real-world field deployment, prioritizing:

- offline-first operation
- autonomous recovery
- modular extensibility
- mission-aware routing intelligence
- headless unattended execution
- future refrigeration energy optimization

This is not a prototype script collection; it is a structured deployable embedded monitoring platform.

---

# System Objectives

Current operational objectives:

- Monitor refrigerated compartment conditions
- Monitor external weather conditions
- Track vehicle position and GPS fix status
- Detect door open/close state
- Estimate mission route progress and ETA
- Log all telemetry locally in structured JSON
- Synchronize data to cloud storage every 30 seconds
- Operate autonomously after power-on
- Remain functional during internet outages

Future objectives:

- Battery monitoring
- solar PV monitoring
- refrigeration compressor telemetry
- cloud-to-edge command/control
- refrigeration load optimization
- predictive energy-aware control

---

# Hardware Platform

## Core Platform

```text
Raspberry Pi 4 Model B
Raspberry Pi OS Lite (headless)
```

---

## Connectivity

```text
SIM7600G-H 4G LTE USB modem
giffgaff SIM
Ethernet fallback support
Wi-Fi management support
```

---

## Active Sensors

### Internal Refrigeration Monitoring

```text
SHT31
I2C
Temperature + Humidity
```

---

### Vehicle Positioning

```text
GPS module
UART / NMEA
```

---

### Door State Monitoring

```text
Magnetic contact sensor
GPIO
```

---

### External Weather Station

```text
External SHT31
I2C
Temperature + Humidity
```

```text
PYR20 Pyranometer
Solar / UV radiation
```

---

## Planned Sensors

```text
DS18B20 1-Wire temperature probes
INA219 power monitoring
Battery telemetry
Solar PV telemetry
Cooling compressor telemetry
```

---

# Software Architecture

```text
src/
├── main.py
│
├── sensors/
│   ├── door_sensor.py
│   ├── gps_sensor.py
│   ├── sht31_sensor.py
│   ├── weather_sht31_sensor.py
│   ├── uv_sensor.py
│   ├── onewire_sensor.py
│   └── power_sensor.py
│
├── services/
│   ├── logger_service.py
│   ├── uploader_service.py
│   ├── route_service.py
│   ├── mission_service.py
│   └── state_service.py
│
├── utils/
│   ├── config_utils.py
│   ├── file_utils.py
│   ├── time_utils.py
│   └── app_logging.py
```

---

# Repository Structure

```text
Refrigeration-Sensor-Hub/
├── config/
├── data/
│   ├── raw/
│   ├── uploaded/
│   └── archive/
├── docs/
├── logs/
├── scripts/
├── services/
├── src/
└── requirements.txt
```

---

# Runtime Configuration

Configuration files:

```text
config/
├── app_config.json
├── mission.json
├── sensors.json
```

---

## app_config.json

Controls runtime behaviour:

- sensor sampling interval
- upload interval
- route interval
- feature enable flags
- storage paths
- logging paths
- cloud backend settings

Default design:

```text
Sensor sampling: 5 sec
Cloud sync: 30 sec
Route update: 180 sec
```

---

## mission.json

Defines runtime mission state:

- mission ID
- van ID
- route enable flag
- destination list
- notes

Destination format:

```json
[
  "B4 7ET",
  "CV1 2WT",
  {
    "lat": 52.4068,
    "lon": -1.5197
  }
]
```

---

## sensors.json

Defines:

- enabled sensors
- GPIO assignments
- I2C addresses
- UART configuration
- future hardware expansion

---

# Runtime Execution Flow

## Boot Chain

```text
Power On
↓
Raspberry Pi OS boots
↓
Netplan initializes networking
↓
NetworkManager manages interfaces
↓
ModemManager initializes SIM7600
↓
4G connection established
↓
systemd starts sensorhub.service
↓
main.py starts
↓
config files loaded
↓
sensors initialized
↓
main runtime loop begins
```

---

# Sampling Pipeline

Every 5 seconds:

- read internal SHT31
- read weather station sensors
- read door sensor
- read latest GPS fix
- read latest route state
- assemble unified JSON record
- write to local storage

---

# Route Intelligence

Mission-aware route estimation:

- GPS-based
- destination-aware
- ETA estimation
- movement-triggered updates
- periodic refresh

Default:

```text
Every 180 seconds
```

Provider:

```text
OpenRouteService
```

Environment variable:

```bash
ORS_API_KEY
```

---

# Cloud Synchronization

Cloud sync runs every:

```text
30 seconds
```

Implementation:

```text
Python uploader service
+
rclone backend
+
Google Drive remote
```

Design:

- asynchronous-friendly
- fault tolerant
- non-blocking
- offline-first

If cloud sync fails:

```text
Local logging continues.
```

---

# Data Storage

Local storage:

```text
data/raw/log_YYYY-MM-DD.json
```

JSON lines format:

```json
{
  "timestamp": "...",
  "mission_id": "...",
  "van_id": "van_01",

  "inside": {
    "temperature_c": 4.6,
    "humidity_percent": 81.4
  },

  "weather_station": {
    "temperature_c": 12.1,
    "humidity_percent": 63.5,
    "uv_index": 2.4
  },

  "door_open": false,

  "gps": {
    "latitude": 52.4862,
    "longitude": -1.8904,
    "altitude_m": 110.2,
    "fix": true
  },

  "route": {
    "summary": {
      "total_distance_km": 62.1,
      "total_duration_min": 58.4
    }
  },

  "power": null
}
```

---

# Networking Architecture

Linux network stack:

```text
Netplan
   ↓
NetworkManager
   ↓
ModemManager
   ↓
SIM7600 USB modem
   ↓
4G network
```

Interfaces:

```text
eth0   → Ethernet
wlan0  → Wi-Fi
wwan0  → Mobile data
cdc-wdm0 → modem control
```

Characteristics:

- 4G primary uplink
- Ethernet fallback
- auto reconnect
- managed connection profiles
- production headless operation

---

# Mission Workflow

Start mission:

```bash
python scripts/start_mission.py
```

Stop mission:

```bash
python scripts/stop_mission.py
```

Mission startup allows:

- van selection
- route enable/disable
- destination entry
- mission ID generation

---

# Deployment

System service:

```text
services/sensorhub.service
```

Install:

```bash
sudo bash scripts/install_service.sh
```

Behaviour:

- auto start on boot
- restart on crash
- headless operation
- uses dedicated Python virtual environment

---

# Installation

Clone:

```bash
git clone https://github.com/M-Foroutan-M/Refrigeration-Sensor-Hub.git
cd Refrigeration-Sensor-Hub
git checkout refactor/unified-runtime
```

---

Create environment:

```bash
python3 -m venv ~/sensorhub-venv
source ~/sensorhub-venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# Manual Run

```bash
python src/main.py
```

---

# Reliability Design

The platform is intentionally resilient.

Failure behaviour:

- internet failure → continue logging
- route API failure → continue logging
- GPS fix unavailable → continue logging
- sensor read failure → null values only
- uploader failure → retry later
- application crash → systemd restart

---

# Author

Mohammad (Farhad) Foroutan
Aston University
