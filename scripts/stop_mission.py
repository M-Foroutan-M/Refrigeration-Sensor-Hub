#!/usr/bin/env python3

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
MISSION_FILE = REPO_ROOT / "config" / "mission.json"


def main():
    print("=== Stop Mission ===\n")

    mission_data = {
        "mission_id": None,
        "van_id": "van_01",
        "route_enabled": False,
        "destinations": [],
        "notes": ""
    }

    MISSION_FILE.parent.mkdir(parents=True, exist_ok=True)

    with MISSION_FILE.open("w", encoding="utf-8") as f:
        json.dump(mission_data, f, indent=2)

    print("Mission reset successfully.")
    print(f"Updated file: {MISSION_FILE}")


if __name__ == "__main__":
    main()
