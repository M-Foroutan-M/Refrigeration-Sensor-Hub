# Refrigeration-Sensor-Hub

## Overview

Refrigeration-Sensor-Hub is a modular embedded IoT edge platform designed for deployment inside refrigerated transport vehicles.

The system continuously acquires environmental, mission, and positional telemetry from the vehicle, stores structured timestamped data locally, and synchronizes records to Google Drive over a 4G connection.

The architecture is designed for real-world field deployment, prioritizing:

* offline-first operation
* autonomous recovery
* modular extensibility
* mission-aware routing intelligence
* headless unattended execution
* future refrigeration energy optimization

This is not a prototype script collection. It is a structured deployable embedded monitoring platform.

---

# System Objectives

Current operational objectives:

* Monitor refrigerated compartment temperature and humidity
* Monitor additional internal temperature using a DS18B20 1-Wire probe
* Monitor external/weather temperature and humidity
* Monitor solar radiation using a pyranometer
* Track vehicle position and GPS fix status
* Detect door open/close state
* Estimate mission route progress and ETA when a destination is configured
* Log all telemetry locally in structured JSON Lines format
* Synchronize data to Google Drive every 30 seconds
* Operate autonomously after power-on using a systemd service
* Remain functional during internet outages

Future objectives:

* Battery monitoring
* Solar PV monitoring
* INA219-based power telemetry
* Refrigeration compressor telemetry
* Cloud-to-edge command/control
* Refrigeration load optimization
* Predictive energy-aware control
* Operator mission start/stop helper scripts

---

# Hardware Platform

## Core Platform

```text
Raspberry Pi 4 Model B
Raspberry Pi OS Lite
Headless operation
```

---

## Connectivity

```text
SIM7600 4G LTE USB modem
Tailscale remote access
Google Drive upload via rclone
Ethernet/Wi-Fi fallback support where available
```

---

## Active Sensors

### Internal Refrigeration Monitoring

```text
Inside SHT31
I2C address: 0x44
Temperature + humidity
```

```text
DS18B20 1-Wire temperature sensor
GPIO: 4
Current device ID: 28-0b2551cc5a63
Additional internal temperature probe
```

---

### Vehicle Positioning

```text
GPS module
UART/NMEA
Port: /dev/serial0
Baudrate: 9600
```

---

### Door State Monitoring

```text
Magnetic contact sensor
GPIO: 17
Door open/closed state
```

---

### External Weather Station

```text
External SHT31
I2C address: 0x45
External temperature + humidity
```

```text
PYR20 Pyranometer
USB / RS485 Modbus RTU
Solar radiation in W/m2
Stable port:
/dev/serial/by-id/usb-WCH.CN_USB_Quad_Serial_BCD9BFABCD-if00
```

---

## Planned Sensors

```text
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
└── utils/
    ├── config_utils.py
    ├── time_utils.py
    └── app_logging.py
```

---

# Repository Structure

```text
Refrigeration-Sensor-Hub/
├── config/
│   ├── app_config.json
│   ├── mission.json
│   └── sensors.json
│
├── data/
│   ├── raw/
│   ├── uploaded/
│   └── archive/
│
├── docs/
│   ├── data_schema.md
│   ├── deployment.md
│   ├── hardware_map.md
│   └── roadmap.md
│
├── logs/
├── scripts/
│   ├── install_service.sh
│   └── sync_drive.sh
│
├── services/
│   └── sensorhub.service
│
├── src/
├── requirements.txt
└── README.md
```

---

# Runtime Configuration

Configuration files:

```text
config/
├── app_config.json
├── mission.json
└── sensors.json
```

---

## app_config.json

Controls runtime behaviour:

* sensor sampling interval
* upload interval
* route interval
* storage paths
* logging paths
* Google Drive upload enable/disable flag
* rclone remote name
* config file locations

Current operational design:

```text
Sensor sampling: 5 seconds
Google Drive upload: 30 seconds
Route update interval: 180 seconds
```

Current upload remote:

```text
gdrive
```

Current upload target:

```text
gdrive:Refrigeration-Sensor-Hub
```

---

## mission.json

Defines runtime mission state:

* mission ID
* van ID
* route enable flag
* destination list
* notes

Default state:

```json
{
  "mission_id": null,
  "van_id": "van_01",
  "route_enabled": true,
  "destinations": [],
  "notes": ""
}
```

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

If the destination list is empty, the system continues normal sensor logging and the `route` field remains `null`.

---

## sensors.json

Defines:

* enabled sensors
* GPIO assignments
* I2C addresses
* UART configuration
* 1-Wire device IDs
* USB/Modbus pyranometer settings
* future hardware expansion

Current active sensor configuration includes:

```text
door_sensor
inside_sht31
gps
onewire
weather_sht31
uv_sensor
```

`power_sensor` is currently disabled and reserved for future INA219 integration.

---

# Runtime Execution Flow

## Boot Chain

```text
Power on
↓
Raspberry Pi OS boots
↓
Network stack starts
↓
SIM7600 modem provides 4G connection
↓
systemd starts sensorhub.service
↓
main.py starts
↓
config files are loaded
↓
sensors are initialized
↓
main runtime loop begins
↓
records are logged locally
↓
records are uploaded to Google Drive
```

---

# Sampling Pipeline

Every 5 seconds:

* read internal SHT31
* read DS18B20 1-Wire temperature sensor
* read external/weather SHT31
* read pyranometer solar radiation
* read door sensor
* read GPS data
* check latest route state
* assemble unified JSON record
* write record to local storage
* upload to Google Drive when upload interval is reached

---

# Route Intelligence

Mission-aware route estimation is supported.

Route updates require:

* `route_enabled` set to `true`
* non-empty `destinations` list in `config/mission.json`
* valid GPS fix
* `ORS_API_KEY` stored locally in `.env`

Provider:

```text
OpenRouteService
```

Local environment file:

```text
.env
```

Example:

```text
ORS_API_KEY=your_key_here
```

The `.env` file is ignored by Git and must not be committed.

When a route is calculated, the JSON record includes:

```json
"route": {
  "provider": "openrouteservice",
  "updated": true,
  "legs": [
    {
      "leg_name": "leg_1",
      "from": {
        "lat": 52.487015,
        "lon": -1.890435
      },
      "to": {
        "lat": 52.486637,
        "lon": -1.890952
      },
      "distance_km": 0.19,
      "duration_min": 0.4
    }
  ],
  "summary": {
    "total_distance_km": 0.19,
    "total_duration_min": 0.4
  }
}
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

Current remote:

```text
gdrive
```

Current destination:

```text
gdrive:Refrigeration-Sensor-Hub
```

If cloud sync fails:

```text
Local logging continues.
The service keeps running.
Upload is retried later.
```

Manual upload helper:

```bash
./scripts/sync_drive.sh
```

This script is for manual testing/debugging only. Normal automatic upload is handled by `src/services/uploader_service.py`.

---

# Data Storage

Local storage:

```text
data/raw/log_YYYY-MM-DD.json
```

Format:

```text
JSON Lines
```

Each line is one full telemetry record.

Example:

```json
{
  "timestamp": "2026-06-02T18:32:04.287689+00:00",
  "mission_id": null,
  "van_id": "van_01",
  "inside": {
    "temperature_c": 22.31,
    "humidity_percent": 46.51,
    "onewire_temperatures": {
      "28-0b2551cc5a63": 22.94
    }
  },
  "door_open": false,
  "gps": {
    "latitude": 52.4862,
    "longitude": -1.8904,
    "altitude_m": 110.2,
    "fix": true
  },
  "route": null,
  "weather_station": {
    "temperature_c": 22.79,
    "humidity_percent": 46.9
  },
  "solar_radiation": {
    "solar_radiation_w_m2": 9,
    "unit": "W/m2",
    "status": "ok"
  },
  "power": null
}
```

Field notes:

```text
inside.temperature_c              Internal SHT31 temperature
inside.humidity_percent           Internal SHT31 humidity
inside.onewire_temperatures        DS18B20 readings by device ID
door_open                          Door state
gps                                GPS position and fix state
route                              Route/ETA snapshot or null
weather_station                    External SHT31 readings
solar_radiation                    Pyranometer reading in W/m2
power                              Reserved for future power monitoring
```

---

# Networking Architecture

Linux network stack:

```text
NetworkManager
↓
ModemManager
↓
SIM7600 USB modem
↓
4G network
```

Used for:

* Tailscale remote SSH access
* Google Drive upload through rclone
* OpenRouteService route/ETA requests

Remote access examples:

```bash
ssh pi@100.76.109.79
```

or when Tailscale DNS is healthy:

```bash
ssh pi@pi-sensorhub
```

---

# Mission Workflow

Current mission workflow is manual through:

```text
config/mission.json
```

Default non-route mode:

```json
{
  "mission_id": null,
  "van_id": "van_01",
  "route_enabled": true,
  "destinations": [],
  "notes": ""
}
```

Example route mission:

```json
{
  "mission_id": "mission_001",
  "van_id": "van_01",
  "route_enabled": true,
  "destinations": ["B4 7ET"],
  "notes": "Example mission"
}
```

After editing `mission.json`, restart the service:

```bash
sudo systemctl restart sensorhub.service
```

Future mission workflow may include:

* operator mission start script
* operator mission stop script
* destination postcode prompt
* automatic mission ID generation

---

# Deployment

System service:

```text
services/sensorhub.service
```

Installed systemd service:

```text
/etc/systemd/system/sensorhub.service
```

Install or update the service:

```bash
chmod +x scripts/install_service.sh
./scripts/install_service.sh
```

Check service status:

```bash
sudo systemctl status sensorhub.service --no-pager
```

Check if the service is active:

```bash
sudo systemctl is-active sensorhub.service
```

Expected:

```text
active
```

Check if the service is enabled on boot:

```bash
sudo systemctl is-enabled sensorhub.service
```

Expected:

```text
enabled
```

Restart service:

```bash
sudo systemctl restart sensorhub.service
```

View live logs:

```bash
sudo journalctl -u sensorhub.service -f
```

---

# Installation

Clone:

```bash
git clone https://github.com/M-Foroutan-M/Refrigeration-Sensor-Hub.git
cd Refrigeration-Sensor-Hub
git checkout refactor/unified-runtime
```

Create environment:

```bash
python3 -m venv ~/sensorhub-venv
source ~/sensorhub-venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Install service:

```bash
chmod +x scripts/install_service.sh
./scripts/install_service.sh
```

---

# Manual Run

Manual run is useful for debugging.

```bash
source ~/sensorhub-venv/bin/activate
cd ~/Refrigeration-Sensor-Hub
python3 src/main.py
```

For normal operation, use the systemd service instead.

---

# Useful Commands

Check Git state:

```bash
git status
```

Check latest commits:

```bash
git log --oneline --decorate -5
```

Check latest local records:

```bash
tail -n 5 data/raw/*.json
```

Check Google Drive upload:

```bash
rclone ls gdrive:Refrigeration-Sensor-Hub | tail -n 20
```

Check service logs:

```bash
sudo journalctl -u sensorhub.service -n 80 --no-pager
```

---

# Reliability Design

The platform is intentionally resilient.

Failure behaviour:

* internet failure → continue local logging
* route API failure → continue logging
* GPS fix unavailable → continue logging with `fix: false`
* sensor read failure → log `null` or error status for that sensor
* uploader failure → retry later
* application crash → systemd restarts service

---

# Current Project Status

Working:

```text
Door sensor
GPS
Inside SHT31
Weather SHT31
DS18B20 1-Wire temperature sensor
PYR20 pyranometer
Local JSON logging
Google Drive upload
systemd auto-start service
OpenRouteService route/ETA test
```

Not yet implemented:

```text
INA219 power monitoring
Battery telemetry
Solar PV telemetry
Cooling compressor telemetry
Cloud command receiver
Compressor/load control
Operator mission start/stop scripts
```

Current tested chain:

```text
boot/systemd
→ main.py
→ sensors
→ JSON log
→ Google Drive upload
```

---

# Author

Mohammad (Farhad) Foroutan
Aston University
