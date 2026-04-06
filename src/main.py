import sys
import time
from pathlib import Path

from utils.config_utils import (
    load_app_config,
    load_mission_config,
    load_sensors_config,
)
from utils.time_utils import utc_now_iso
from services.logger_service import JsonLineLogger
from sensors.door_sensor import DoorSensor
from sensors.sht31_sensor import SHT31Sensor
from sensors.gps_sensor import GPSSensor


def build_record(mission_config, door_sensor, sht31_sensor, gps_sensor):
    door_open = door_sensor.read()
    env_data = sht31_sensor.read()
    gps_data = gps_sensor.read()

    record = {
        "timestamp": utc_now_iso(),
        "mission_id": mission_config.get("mission_id"),
        "van_id": mission_config.get("van_id"),
        "temperature_c": env_data["temperature_c"],
        "humidity_percent": env_data["humidity_percent"],
        "door_open": door_open,
        "gps": gps_data,
        "route": None,
        "weather": None,
        "power": None,
    }

    return record


def main():
    repo_root = Path(__file__).resolve().parent.parent
    app_config = load_app_config(str(repo_root / "config/app_config.json"))
    mission_config = load_mission_config(app_config["mission_file"])
    sensors_config = load_sensors_config(app_config["sensors_file"])

    sample_interval = app_config["sample_interval_sec"]
    data_dir = app_config["data_dir"]

    logger = JsonLineLogger(data_dir=data_dir)

    door_cfg = sensors_config["door_sensor"]
    sht31_cfg = sensors_config["inside_sht31"]
    gps_cfg = sensors_config["gps"]

    if not door_cfg["enabled"]:
        raise RuntimeError("Door sensor is disabled in config")
    if not sht31_cfg["enabled"]:
        raise RuntimeError("Inside SHT31 is disabled in config")
    if not gps_cfg["enabled"]:
        raise RuntimeError("GPS is disabled in config")

    door_sensor = DoorSensor(
        gpio_pin=door_cfg["gpio_pin"],
        pull_up=door_cfg.get("pull_up", True),
    )
    sht31_sensor = SHT31Sensor()
    gps_sensor = GPSSensor(
        port=gps_cfg["port"],
        baudrate=gps_cfg["baudrate"],
        timeout_sec=gps_cfg.get("timeout_sec", 1),
    )

    print("Initializing sensors...")
    door_sensor.initialize()
    sht31_sensor.initialize()
    gps_sensor.initialize()
    print("Sensors initialized. Starting main loop...")

    try:
        while True:
            record = build_record(
                mission_config=mission_config,
                door_sensor=door_sensor,
                sht31_sensor=sht31_sensor,
                gps_sensor=gps_sensor,
            )

            logger.write_record(record)
            print(record)

            time.sleep(sample_interval)

    except KeyboardInterrupt:
        print("\nStopping sensor hub...")

    finally:
        gps_sensor.stop()
        door_sensor.cleanup()


if __name__ == "__main__":
    main()
