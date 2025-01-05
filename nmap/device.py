from dataclasses import dataclass
from typing import Optional

@dataclass
class Device:
    mac_address: str
    state: str
    known: bool
    vendor: Optional[str] = None