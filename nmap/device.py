from dataclasses import dataclass
from typing import Optional

@dataclass
class Device:
    device_name: str
    mac_address: str
    device_type: str
    hostname: str
    state: str
    known: bool
    vendor: Optional[str] = None
