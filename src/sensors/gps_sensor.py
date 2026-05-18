import threading
from typing import Dict, Any

import serial
import pynmea2


class GPSSensor:
    def __init__(self, port: str, baudrate: int, timeout_sec: float = 1.0):
        self.port = port
        self.baudrate = baudrate
        self.timeout_sec = timeout_sec

        self.serial_conn = None
        self.lock = threading.Lock()
        self.running = False
        self.thread = None

        self.latest_gps: Dict[str, Any] = {
            "latitude": None,
            "longitude": None,
            "altitude_m": None,
            "fix": False
        }

    def initialize(self) -> None:
        self.serial_conn = serial.Serial(
            self.port,
            self.baudrate,
            timeout=self.timeout_sec
        )
        self.running = True
        self.thread = threading.Thread(target=self._reader_loop, daemon=True)
        self.thread.start()

    def _reader_loop(self) -> None:
        while self.running:
            try:
                line = self.serial_conn.readline().decode("ascii", errors="replace").strip()

                if line.startswith("$GPGGA") or line.startswith("$GNGGA"):
                    msg = pynmea2.parse(line)

                    with self.lock:
                        if int(msg.gps_qual) > 0:
                            self.latest_gps = {
                                "latitude": msg.latitude,
                                "longitude": msg.longitude,
                                "altitude_m": float(msg.altitude) if msg.altitude else None,
                                "fix": True
                            }
                        else:
                            self.latest_gps = {
                                "latitude": None,
                                "longitude": None,
                                "altitude_m": None,
                                "fix": False
                            }

            except Exception:
                # Keep loop alive even if a malformed sentence appears
                pass

    def read(self) -> Dict[str, Any]:
        with self.lock:
            return dict(self.latest_gps)

    def stop(self) -> None:
        self.running = False

        if self.serial_conn is not None:
            self.serial_conn.close()
