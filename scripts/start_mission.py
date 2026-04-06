#!/usr/bin/env python3

import json
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
MISSION_FILE = REPO_ROOT / "config" / "mission.json"


def generate_mission_id() -> str:
    now = datetime.now(timezone.utc)
    return now.strftime("mission_%Y%m%dT%H%M%SZ")


def prompt_nonempty(prompt_text: str) -> str:
    while True:
        value = input(prompt_text).strip()
        if value:
            return value
        print("Value cannot be empty.")


def prompt_yes_no(prompt_text: str, default: bool = True) -> bool:
    suffix = " [Y/n]: " if default else " [y/N]: "

    while True:
        value = input(prompt_text + suffix).strip().lower()

        if not value:
            return default
        if value in ("y", "yes"):
            return True
        if value in ("n", "no"):
            return False

        print("Please enter yes or no.")


def prompt_destinations():
    print("\nEnter destinations one by one.")
    print("You can enter either:")
    print("- a postcode (example: B4 7ET)")
    print("- coordinates as lat,lon (example: 52.4862,-1.8904)")
    print("Press Enter on an empty line when finished.\n")

    destinations = []

    while True:
        value = input(f"Destination {len(destinations) + 1}: ").strip()

        if not value:
            break

        if "," in value:
            parts = value.split(",")
            if len(parts) == 2:
                try:
                    lat = float(parts[0].strip())
                    lon = float(parts[1].strip())
                    destinations.append({"lat": lat, "lon": lon})
                    continue
                except ValueError:
                    print("Invalid coordinate format. Use lat,lon")
                    continue

        destinations.append(value)

    return destinations


def main():
    print("=== Start Mission ===\n")

    van_id = prompt_nonempty("Enter van ID [example: van_01]: ")
    route_enabled = prompt_yes_no("Enable route estimation?", default=True)
    destinations = prompt_destinations()
    notes = input("Enter mission notes (optional): ").strip()

    mission_data = {
        "mission_id": generate_mission_id(),
        "van_id": van_id,
        "route_enabled": route_enabled,
        "destinations": destinations,
        "notes": notes
    }

    MISSION_FILE.parent.mkdir(parents=True, exist_ok=True)

    with MISSION_FILE.open("w", encoding="utf-8") as f:
        json.dump(mission_data, f, indent=2)

    print("\nMission file written successfully:")
    print(MISSION_FILE)
    print("\nMission contents:")
    print(json.dumps(mission_data, indent=2))


if __name__ == "__main__":
    main()
