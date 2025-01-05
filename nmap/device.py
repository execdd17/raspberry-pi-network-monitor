from dataclasses import dataclass

@dataclass
class Device:
    device_name: str
    mac_address: str
    device_type: str
    hostname: str
    state: str
    known: bool