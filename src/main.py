import time
from pathlib import Path
from typing import Optional, Dict, Any

from utils.config_utils import (
    load_app_config,
    load_mission_config,
    load_sensors_config,
)
from utils.time_utils import utc_now_iso
from utils.app_logging import setup_app_logger
from services.logger_service import JsonLineLogger
from services.uploader_service import UploaderService
from services.mission_service import MissionService
from services.route_service import RouteService
from sensors.door_sensor import DoorSensor
from sensors.sht31_sensor import SHT31Sensor
from sensors.gps_sensor import GPSSensor


def hex_to_int(address_value):
    if isinstance(address_value, int):
        return address_value
    if isinstance(address_value, str):
        return int(address_value, 16)
    raise ValueError(f"Unsupported I2C address format: {address_value}")


def safe_read_door(door_sensor, logger) -> Optional[bool]:
    try:
        return door_sensor.read()
    except Exception as e:
        logger.warning(f"Door sensor read failed: {e}")
        return None


def safe_read_sht31(sensor, logger, label: str) -> Dict[str, Optional[float]]:
    try:
        return sensor.read()
    except Exception as e:
        logger.warning(f"{label} SHT31 read failed: {e}")
        return {
            "temperature_c": None,
            "humidity_percent": None,
        }


def safe_read_gps(gps_sensor, logger) -> Dict[str, Any]:
    try:
        return gps_sensor.read()
    except Exception as e:
        logger.warning(f"GPS read failed: {e}")
        return {
            "latitude": None,
            "longitude": None,
            "altitude_m": None,
            "fix": False,
        }


def build_record(
    mission_service,
    door_sensor,
    inside_sht31_sensor,
    gps_data,
    logger,
    latest_route,
    weather_sht31_sensor=None,
):
    door_open = safe_read_door(door_sensor, logger)
    inside_data = safe_read_sht31(inside_sht31_sensor, logger, "Inside")

    weather_data = None
    if weather_sht31_sensor is not None:
        weather_data = safe_read_sht31(weather_sht31_sensor, logger, "Weather station")

    record = {
        "timestamp": utc_now_iso(),
        "mission_id": mission_service.get_mission_id(),
        "van_id": mission_service.get_van_id(),
        "inside": {
            "temperature_c": inside_data["temperature_c"],
            "humidity_percent": inside_data["humidity_percent"],
        },
        "door_open": door_open,
        "gps": gps_data,
        "route": latest_route,
        "weather_station": weather_data,
        "power": None,
    }

    return record


def main():
    repo_root = Path(__file__).resolve().parent.parent
    app_config = load_app_config(str(repo_root / "config/app_config.json"))
    mission_config = load_mission_config(app_config["mission_file"])
    sensors_config = load_sensors_config(app_config["sensors_file"])

    logger = setup_app_logger(app_config["log_file"])
    logger.info("Starting Refrigeration Sensor Hub")

    sample_interval = app_config["sample_interval_sec"]

    json_logger = JsonLineLogger(data_dir=app_config["data_dir"])

    uploader = UploaderService(
        data_dir=app_config["data_dir"],
        remote_name=app_config.get("drive_remote_name", "gdrive_sensorhub"),
        upload_interval_sec=app_config["upload_interval_sec"],
        logger=logger,
        enabled=app_config.get("drive_upload_enabled", False),
    )

    mission_service = MissionService(mission_config)

    route_service = RouteService(
        logger=logger,
        route_interval_sec=app_config.get("route_interval_sec", 180),
        movement_threshold_meters=300.0,
    )

    door_cfg = sensors_config["door_sensor"]
    inside_sht31_cfg = sensors_config["inside_sht31"]
    gps_cfg = sensors_config["gps"]
    weather_sht31_cfg = sensors_config.get("weather_sht31", {"enabled": False})

    if not door_cfg["enabled"]:
        raise RuntimeError("Door sensor is disabled in config")
    if not inside_sht31_cfg["enabled"]:
        raise RuntimeError("Inside SHT31 is disabled in config")
    if not gps_cfg["enabled"]:
        raise RuntimeError("GPS is disabled in config")

    door_sensor = DoorSensor(
        gpio_pin=door_cfg["gpio_pin"],
        pull_up=door_cfg.get("pull_up", True),
    )

    inside_sht31_sensor = SHT31Sensor(
        i2c_address=hex_to_int(inside_sht31_cfg.get("i2c_address", "0x44"))
    )

    gps_sensor = GPSSensor(
        port=gps_cfg["port"],
        baudrate=gps_cfg["baudrate"],
        timeout_sec=gps_cfg.get("timeout_sec", 1),
    )

    weather_sht31_sensor = None
    if weather_sht31_cfg.get("enabled", False):
        weather_sht31_sensor = SHT31Sensor(
            i2c_address=hex_to_int(weather_sht31_cfg.get("i2c_address", "0x45"))
        )

    logger.info("Initializing sensors...")
    door_sensor.initialize()
    inside_sht31_sensor.initialize()
    gps_sensor.initialize()

    if weather_sht31_sensor is not None:
        weather_sht31_sensor.initialize()
        logger.info("Weather station SHT31 initialized")

    logger.info("Sensors initialized. Entering main loop.")

    try:
        while True:
            cycle_start = time.time()

            try:
                gps_data = safe_read_gps(gps_sensor, logger)

                if route_service.should_update(
                    gps_data=gps_data,
                    route_enabled=mission_service.route_enabled(),
                    destinations=mission_service.get_destinations(),
                ):
                    route_service.update_route(
                        gps_data=gps_data,
                        destinations=mission_service.get_destinations(),
                    )

                latest_route = route_service.get_latest_route()

                record = build_record(
                    mission_service=mission_service,
                    door_sensor=door_sensor,
                    inside_sht31_sensor=inside_sht31_sensor,
                    gps_data=gps_data,
                    logger=logger,
                    latest_route=latest_route,
                    weather_sht31_sensor=weather_sht31_sensor,
                )

                json_logger.write_record(record)
                logger.info(f"Record logged: {record}")

                if uploader.should_upload():
                    uploader.upload_once()

            except Exception as cycle_error:
                logger.exception(f"Unexpected error in acquisition cycle: {cycle_error}")

            elapsed = time.time() - cycle_start
            sleep_time = max(0, sample_interval - elapsed)
            time.sleep(sleep_time)

    except KeyboardInterrupt:
        logger.info("Stopping sensor hub due to keyboard interrupt")

    finally:
        try:
            gps_sensor.stop()
        except Exception:
            pass

        try:
            door_sensor.cleanup()
        except Exception:
            pass

        logger.info("Sensor hub stopped cleanly")


if __name__ == "__main__":
    main()
