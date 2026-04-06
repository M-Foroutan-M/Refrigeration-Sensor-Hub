import json
from pathlib import Path
from typing import Any, Dict


def load_json_file(path: str) -> Dict[str, Any]:
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with file_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_app_config(config_path: str = "config/app_config.json") -> Dict[str, Any]:
    return load_json_file(config_path)


def load_mission_config(config_path: str) -> Dict[str, Any]:
    return load_json_file(config_path)


def load_sensors_config(config_path: str) -> Dict[str, Any]:
    return load_json_file(config_path)
