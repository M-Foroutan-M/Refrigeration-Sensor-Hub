import math
import os
import time
from typing import Any, Dict, List, Optional, Tuple

import requests


class RouteService:
    def __init__(
        self,
        logger,
        route_interval_sec: int = 180,
        movement_threshold_meters: float = 300.0,
        provider_name: str = "openrouteservice",
    ):
        self.logger = logger
        self.route_interval_sec = route_interval_sec
        self.movement_threshold_meters = movement_threshold_meters
        self.provider_name = provider_name

        self.last_route_time = 0.0
        self.last_lat = None
        self.last_lon = None
        self.latest_route = None

        self.ors_api_key = os.getenv("ORS_API_KEY")

    def get_latest_route(self) -> Optional[Dict[str, Any]]:
        return self.latest_route

    def should_update(self, gps_data: Dict[str, Any], route_enabled: bool, destinations: List[Any]) -> bool:
        if not route_enabled:
            return False

        if not destinations:
            return False

        if not gps_data.get("fix", False):
            return False

        now = time.time()

        if (now - self.last_route_time) < self.route_interval_sec:
            return False

        current_lat = gps_data.get("latitude")
        current_lon = gps_data.get("longitude")

        if current_lat is None or current_lon is None:
            return False

        if self.last_lat is None or self.last_lon is None:
            return True

        movement = self.distance_between(
            self.last_lat,
            self.last_lon,
            current_lat,
            current_lon,
        )

        return movement >= self.movement_threshold_meters

    def update_route(self, gps_data: Dict[str, Any], destinations: List[Any]) -> Optional[Dict[str, Any]]:
        if self.ors_api_key is None:
            self.logger.warning("Route update skipped: ORS_API_KEY is not set")
            return self.latest_route

        try:
            resolved_destinations = [self.resolve_destination(d) for d in destinations]

            if not resolved_destinations:
                self.logger.warning("Route update skipped: no valid destinations")
                return self.latest_route

            current_lat = gps_data["latitude"]
            current_lon = gps_data["longitude"]

            legs = []
            start_lat, start_lon = current_lat, current_lon

            for idx, (dest_lat, dest_lon) in enumerate(resolved_destinations, start=1):
                leg_info = self.get_route_info(start_lat, start_lon, dest_lat, dest_lon)
                legs.append({
                    "leg_name": f"leg_{idx}",
                    "from": {"lat": start_lat, "lon": start_lon},
                    "to": {"lat": dest_lat, "lon": dest_lon},
                    "distance_km": leg_info["distance_km"],
                    "duration_min": leg_info["duration_min"],
                })
                start_lat, start_lon = dest_lat, dest_lon

            total_distance_km = round(sum(leg["distance_km"] for leg in legs), 2)
            total_duration_min = round(sum(leg["duration_min"] for leg in legs), 1)

            route_snapshot = {
                "provider": self.provider_name,
                "updated": True,
                "legs": legs,
                "summary": {
                    "total_distance_km": total_distance_km,
                    "total_duration_min": total_duration_min,
                },
            }

            self.latest_route = route_snapshot
            self.last_route_time = time.time()
            self.last_lat = current_lat
            self.last_lon = current_lon

            self.logger.info(f"Route updated successfully: {route_snapshot}")
            return route_snapshot

        except Exception as e:
            self.logger.exception(f"Route update failed: {e}")
            return self.latest_route

    def resolve_destination(self, destination: Any) -> Tuple[float, float]:
        if isinstance(destination, str):
            return self.geocode_postcode(destination)

        if isinstance(destination, dict):
            lat = destination.get("lat")
            lon = destination.get("lon")
            if lat is None or lon is None:
                raise ValueError(f"Invalid coordinate destination: {destination}")
            return float(lat), float(lon)

        raise ValueError(f"Unsupported destination format: {destination}")

    def geocode_postcode(self, postcode: str) -> Tuple[float, float]:
        url = "https://api.openrouteservice.org/geocode/search"
        headers = {"Authorization": self.ors_api_key}
        params = {
            "text": postcode,
            "size": 1,
        }

        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()
        features = data.get("features", [])

        if not features:
            raise ValueError(f"No geocoding result for destination: {postcode}")

        coords = features[0]["geometry"]["coordinates"]
        return coords[1], coords[0]

    def get_route_info(self, lat1: float, lon1: float, lat2: float, lon2: float) -> Dict[str, float]:
        url = "https://api.openrouteservice.org/v2/directions/driving-car"

        headers = {
            "Authorization": self.ors_api_key,
            "Content-Type": "application/json",
        }

        body = {
            "coordinates": [
                [lon1, lat1],
                [lon2, lat2],
            ],
            "preference": "fastest",
        }

        response = requests.post(url, headers=headers, json=body, timeout=30)
        response.raise_for_status()

        data = response.json()
        summary = data["routes"][0]["summary"]

        return {
            "distance_km": round(summary["distance"] / 1000, 2),
            "duration_min": round(summary["duration"] / 60, 1),
        }

    @staticmethod
    def distance_between(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        r = 6371000.0
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)

        a = (
            math.sin(dphi / 2) ** 2
            + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
        )

        return 2 * r * math.atan2(math.sqrt(a), math.sqrt(1 - a))
