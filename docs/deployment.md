# Deployment Guide

This document explains how the Refrigeration Sensor Hub is deployed and run on the Raspberry Pi.

## Project Location

The project is stored on the Raspberry Pi at:

```text
/home/pi/Refrigeration-Sensor-Hub
```

Main branch currently used:

```text
refactor/unified-runtime
```

Main runtime file:

```text
src/main.py
```

## Python Environment

The project runs inside this Python virtual environment:

```text
/home/pi/sensorhub-venv
```

To activate it manually:

```bash
source ~/sensorhub-venv/bin/activate
```

Install dependencies:

```bash
cd ~/Refrigeration-Sensor-Hub
pip install -r requirements.txt
```

Current important dependencies include:

```text
adafruit-circuitpython-sht31d
adafruit-circuitpython-ina219
pyserial
RPi.GPIO
pynmea2
pymodbus
```

## Configuration Files

Main configuration files:

```text
config/app_config.json
config/sensors.json
config/mission.json
```

`app_config.json` controls runtime intervals, data paths, log paths, upload settings, and config file locations.

`sensors.json` controls enabled sensors and sensor addresses/ports.

`mission.json` controls mission ID, van ID, route enable state, and destination list.

## Local Secrets

Route calculation uses OpenRouteService.

The API key is stored locally in:

```text
.env
```

Example:

```text
ORS_API_KEY=your_key_here
```

The `.env` file must not be committed to GitHub.

It is loaded by the systemd service using:

```text
EnvironmentFile=-/home/pi/Refrigeration-Sensor-Hub/.env
```

## Systemd Service

The project runs automatically using systemd.

Service file in the repository:

```text
services/sensorhub.service
```

Installed service location:

```text
/etc/systemd/system/sensorhub.service
```

The service runs:

```text
/home/pi/sensorhub-venv/bin/python /home/pi/Refrigeration-Sensor-Hub/src/main.py
```

## Install or Update the Service

From the project folder:

```bash
cd ~/Refrigeration-Sensor-Hub
chmod +x scripts/install_service.sh
./scripts/install_service.sh
```

The installer copies the service file, reloads systemd, enables the service, and restarts it.

## Service Commands

Check service status:

```bash
sudo systemctl status sensorhub.service --no-pager
```

Check if service is active:

```bash
sudo systemctl is-active sensorhub.service
```

Expected:

```text
active
```

Check if service starts on boot:

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

Stop service:

```bash
sudo systemctl stop sensorhub.service
```

Start service:

```bash
sudo systemctl start sensorhub.service
```

View live service logs:

```bash
sudo journalctl -u sensorhub.service -f
```

View recent service logs:

```bash
sudo journalctl -u sensorhub.service -n 80 --no-pager
```

## Data Storage

Local data is saved in:

```text
data/raw/
```

Example file:

```text
data/raw/log_2026-06-02.json
```

Each line is one JSON record.

Check recent records:

```bash
tail -n 5 data/raw/*.json
```

## Application Logs

Application logs are stored in:

```text
logs/sensorhub.log
```

Check recent application logs:

```bash
tail -n 50 logs/sensorhub.log
```

## Google Drive Upload

The system uses `rclone` to upload data to Google Drive.

Current rclone remote name:

```text
gdrive
```

Upload target:

```text
gdrive:Refrigeration-Sensor-Hub
```

Check rclone remotes:

```bash
rclone listremotes
```

Check Google Drive folder:

```bash
rclone ls gdrive:Refrigeration-Sensor-Hub | tail -n 20
```

Manual upload test:

```bash
rclone copy data/raw gdrive:Refrigeration-Sensor-Hub/test-upload --progress
```

The automatic upload is controlled by:

```json
"drive_upload_enabled": true
```

in:

```text
config/app_config.json
```

The upload interval is currently:

```json
"upload_interval_sec": 30
```

## Normal Deployment Flow

For normal deployment:

1. Power on the Raspberry Pi.
2. Wait for the modem/network to come online.
3. `sensorhub.service` starts automatically.
4. Sensors are read every 5 seconds.
5. JSON records are saved locally.
6. Data is uploaded to Google Drive every 30 seconds.

Basic checks after startup:

```bash
sudo systemctl is-active sensorhub.service
tail -n 5 data/raw/*.json
rclone ls gdrive:Refrigeration-Sensor-Hub | tail -n 20
```

## GitHub Workflow

Check repository state:

```bash
git status
```

Check latest commits:

```bash
git log --oneline --decorate -5
```

Push committed changes:

```bash
git push
```

Runtime files should not be committed:

```text
data/raw/
logs/
__pycache__/
.env
```

These are ignored by `.gitignore`.

## Current Deployment Status

The current deployment has been tested with:

```text
systemd auto-start
sensor reading
local JSON logging
Google Drive upload
route/ETA calculation
service restart
service running continuously
```

Current working chain:

```text
boot/systemd -> main.py -> sensors -> JSON log -> Google Drive upload
```

## Future Deployment Work

Future deployment improvements may include:

```text
mission start/stop helper script
operator postcode prompt
power monitoring service
cloud command receiver
compressor/load control
long-duration van field test
```
