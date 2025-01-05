from dataclasses import dataclass

@dataclass
class Device:
    mac_address: str
    ip_address: str
    vendor: str
    known: bool = True
    state: str = "down"
