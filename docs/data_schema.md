# Data Schema

The Refrigeration Sensor Hub stores sensor readings as JSON Lines files.

Each line in the file is one complete sensor record.

Local data folder:

```text
data/raw/
```

Example file name:

```text
log_2026-06-02.json
```

## Current JSON Record

```json
{
  "timestamp": "2026-06-02T18:32:04.287689+00:00",
  "mission_id": null,
  "van_id": "van_01",
  "inside": {
    "temperature_c": 22.31,
    "humidity_percent": 46.51,
    "onewire_temperatures": {
      "28-0b2551cc5a63": 22.94
    }
  },
  "door_open": false,
  "gps": {
    "latitude": 52.4862,
    "longitude": -1.8904,
    "altitude_m": 110.2,
    "fix": true
  },
  "route": null,
  "weather_station": {
    "temperature_c": 22.79,
    "humidity_percent": 46.9
  },
  "solar_radiation": {
    "solar_radiation_w_m2": 9,
    "unit": "W/m2",
    "status": "ok"
  },
  "power": null
}
```

## Field Description

| Field                                  | Description                                                                             |
| -------------------------------------- | --------------------------------------------------------------------------------------- |
| `timestamp`                            | UTC timestamp for the record.                                                           |
| `mission_id`                           | Current mission ID from `config/mission.json`. Can be `null` when no mission is active. |
| `van_id`                               | Vehicle identifier. Current value is `van_01`.                                          |
| `inside.temperature_c`                 | Inside van temperature from the internal SHT31 sensor.                                  |
| `inside.humidity_percent`              | Inside van humidity from the internal SHT31 sensor.                                     |
| `inside.onewire_temperatures`          | DS18B20 1-Wire temperature readings. Each sensor is stored using its device ID.         |
| `door_open`                            | Door state. `true` means open, `false` means closed.                                    |
| `gps.latitude`                         | GPS latitude. Can be `null` if GPS has no fix.                                          |
| `gps.longitude`                        | GPS longitude. Can be `null` if GPS has no fix.                                         |
| `gps.altitude_m`                       | GPS altitude in metres. Can be `null` if unavailable.                                   |
| `gps.fix`                              | GPS fix status. `true` means valid GPS position is available.                           |
| `route`                                | Route and ETA information. This is `null` when no destination is set.                   |
| `weather_station.temperature_c`        | External/weather SHT31 temperature reading.                                             |
| `weather_station.humidity_percent`     | External/weather SHT31 humidity reading.                                                |
| `solar_radiation.solar_radiation_w_m2` | Pyranometer solar radiation reading in watts per square metre.                          |
| `solar_radiation.unit`                 | Unit for solar radiation. Current value is `W/m2`.                                      |
| `solar_radiation.status`               | Pyranometer read status. `ok` means the read was successful.                            |
| `power`                                | Reserved for future INA219 power monitoring. Currently `null`.                          |

## Route Object

When a destination is set in `config/mission.json` and GPS has a fix, the `route` field contains route information.

Example:

```json
"route": {
  "provider": "openrouteservice",
  "updated": true,
  "legs": [
    {
      "leg_name": "leg_1",
      "from": {
        "lat": 52.487015,
        "lon": -1.890435
      },
      "to": {
        "lat": 52.486637,
        "lon": -1.890952
      },
      "distance_km": 0.19,
      "duration_min": 0.4
    }
  ],
  "summary": {
    "total_distance_km": 0.19,
    "total_duration_min": 0.4
  }
}
```

## Notes

* The file format is JSON Lines, not one large JSON array.
* Each line is independent and can be parsed separately.
* `null` means the value was unavailable, disabled, or not applicable for that record.
* Sensor failures should not stop the whole logger. The system should continue logging available fields.
* The `power` field is kept for future battery, solar PV, or INA219 data.
