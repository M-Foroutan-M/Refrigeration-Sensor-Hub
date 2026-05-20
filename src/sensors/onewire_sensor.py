from pathlib import Path
from typing import Dict, List, Optional


class OneWireTemperatureSensor:
    """
    DS18B20 / 1-Wire temperature sensor reader.

    Linux exposes DS18B20 sensors at:
    /sys/bus/w1/devices/<device_id>/w1_slave
    """

    def __init__(self, device_ids: Optional[List[str]] = None):
        self.device_ids = device_ids or []
        self.base_path = Path("/sys/bus/w1/devices")

    def initialize(self) -> None:
        # 1-Wire is initialized by the Linux kernel.
        # Nothing is required here if dtoverlay=w1-gpio,gpiopin=4 is enabled.
        pass

    def read_sensor(self, device_id: str) -> Optional[float]:
        sensor_file = self.base_path / device_id / "w1_slave"

        if not sensor_file.exists():
            return None

        try:
            lines = sensor_file.read_text(errors="replace").splitlines()
        except OSError:
            return None

        if len(lines) < 2:
            return None

        if "YES" not in lines[0]:
            return None

        if "t=" not in lines[1]:
            return None

        try:
            temp_raw = lines[1].split("t=")[-1]
            return round(float(temp_raw) / 1000.0, 2)
        except ValueError:
            return None

    def read(self) -> Dict[str, Optional[float]]:
        readings = {}

        for device_id in self.device_ids:
            readings[device_id] = self.read_sensor(device_id)

        return readings
