from typing import Any, Dict, List


class MissionService:
    def __init__(self, mission_config: Dict[str, Any]):
        self.mission_config = mission_config

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
