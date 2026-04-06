import json
from pathlib import Path
from typing import Any, Dict, List


class MissionService:
    def __init__(self, mission_config: Dict[str, Any], mission_file: str = None):
        self.mission_config = mission_config
        self.mission_file = mission_file

    def get_mission_id(self):
        return self.mission_config.get("mission_id")

    def get_van_id(self):
        return self.mission_config.get("van_id")

    def route_enabled(self) -> bool:
        return bool(self.mission_config.get("route_enabled", False))

    def get_destinations(self) -> List[Any]:
        destinations = self.mission_config.get("destinations", [])
        if not isinstance(destinations, list):
            return []
        return destinations

    def has_destinations(self) -> bool:
        return len(self.get_destinations()) > 0

    def save(self) -> None:
        if not self.mission_file:
            raise ValueError("Mission file path not set")

        mission_path = Path(self.mission_file)
        mission_path.parent.mkdir(parents=True, exist_ok=True)

        with mission_path.open("w", encoding="utf-8") as f:
            json.dump(self.mission_config, f, indent=2)

    def update(self, new_config: Dict[str, Any]) -> None:
        self.mission_config = new_config
