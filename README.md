# Refrigeration-Sensor-Hub

## Project Overview

This project implements a Raspberry Pi–based multi-sensor data acquisition system designed to collect environmental, positional, electrical, and state-based data in a structured and extensible manner. The system integrates multiple sensors using standard digital interfaces and logs synchronized data locally in JSON format for later analysis or transmission.

The architecture prioritizes modularity, reproducibility, and headless operation, making it suitable for embedded sensing platforms, mobile robots, and remote monitoring applications.

---

## System Features

* Concurrent acquisition of multiple sensor modalities
* Support for I2C, UART, GPIO, and USB interfaces
* Timestamped data logging in JSON format
* Modular software structure for easy extension
* Ethernet-based secure file transfer (SFTP)
* Prepared for future cellular (4G) connectivity

---

## Integrated Sensors and Modules

* **Temperature and Humidity Sensor (SHT31 – I2C)**
* **Magnetic Contact Door Sensor (GPIO)**
* **GPS Module (UART / NMEA)**
* **Current and Voltage Sensor (INA219 – I2C)**
* **External 3-Meter Temperature Probe (Digital)**
* **USB 4G LTE Modem (Connectivity readiness)**

---

## Hardware Platform

* Raspberry Pi 4 Model B
* Raspberry Pi OS Lite (64-bit, Debian-based)
* Headless configuration (SSH enabled)

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
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Running the System

To run the **full multi-sensor data acquisition system**:

```bash
python src/system_logger.py
```

JSON log files will be generated in the `data/` directory.

---

## Data Output Format

Each record is stored in JSON format and includes:

* UTC timestamp
* Temperature and humidity
* Door open/closed state
* GPS coordinates and fix status
* System current and voltage readings (# Will be generated according to the future harware setup)

---

## Version Control and Documentation

This repository serves as the **software backbone** of the project.
For detailed implementation history, configuration steps, and updates, refer to this GitHub repository.

---

## Author

Mohammad (Farhad) Foroutan
Aston University
