from dataclasses import dataclass

@dataclass
class Device:
    mac_address: str
    ip_address: str 
    state: str
    known: bool
    vendor: str = "Unknown" 
