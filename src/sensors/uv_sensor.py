from pymodbus.client import ModbusSerialClient


class UVSensor:
    """
    Modbus RTU pyranometer / solar radiation sensor.

    Current verified settings:
    - port: /dev/serial/by-id/usb-WCH.CN_USB_Quad_Serial_BCD9BFABCD-if00
    - baudrate: 9600
    - device_id: 1
    - register_address: 0
    - register_count: 1
    - unit: W/m2
    """

    def __init__(
        self,
        port,
        baudrate=9600,
        device_id=1,
        register_address=0,
        register_count=1,
        timeout_sec=1,
        unit="W/m2",
    ):
        self.port = port
        self.baudrate = baudrate
        self.device_id = device_id
        self.register_address = register_address
        self.register_count = register_count
        self.timeout_sec = timeout_sec
        self.unit = unit

        self.client = ModbusSerialClient(
            port=self.port,
            baudrate=self.baudrate,
            bytesize=8,
            parity="N",
            stopbits=1,
            timeout=self.timeout_sec,
        )

    def read(self):
        connected = self.client.connect()
        if not connected:
            return {
                "solar_radiation_w_m2": None,
                "unit": self.unit,
                "status": "connection_failed",
            }

        try:
            result = self.client.read_holding_registers(
                address=self.register_address,
                count=self.register_count,
                device_id=self.device_id,
            )

            if result.isError():
                return {
                    "solar_radiation_w_m2": None,
                    "unit": self.unit,
                    "status": "read_error",
                }

            value = result.registers[0]

            return {
                "solar_radiation_w_m2": value,
                "unit": self.unit,
                "status": "ok",
            }

        except Exception as exc:
            return {
                "solar_radiation_w_m2": None,
                "unit": self.unit,
                "status": f"exception: {exc}",
            }

        finally:
            self.client.close()
