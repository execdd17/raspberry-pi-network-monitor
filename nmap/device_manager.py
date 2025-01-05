import logging
import json

from device import Device
from vender_database import VendorDatabase
from pathlib import Path
from typing import Dict
from typing import List, Tuple, Dict


logger = logging.getLogger(__name__)

class DeviceManager:
    """
    Responsible for loading and saving known devices, plus merging scan results.
    """
    def __init__(self, known_devices_path: Path):
        self.known_devices_path = known_devices_path
        self.known_devices = self.load_known_devices()

    def load_known_devices(self) -> List[Device]:
        """
        Load known devices from a JSON file and return a list of Device instances.
        """
        devices_list = []
        if not self.known_devices_path.exists():
            logger.warning(f"No known_devices.json found at {self.known_devices_path}, starting empty.")
            return devices_list

        try:
            with self.known_devices_path.open('r') as f:
                devices_json = json.load(f)
            for d in devices_json:
                devices_list.append(
                    Device(
                        mac_address=d["mac_address"].upper(),
                        ip_address=d.get("ip_address", "Unknown"),
                        vendor=d.get("vendor", "Unknown"),
                        known=True,
                        state="down"
                    )
                )
            logger.info(f"Loaded {len(devices_list)} known devices from {self.known_devices_path}.")
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from {self.known_devices_path}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error loading known devices: {e}")
        return devices_list

    def save_known_devices(self) -> None:
        """
        Save the current list of known devices to the JSON file.
        """
        try:
            data_to_save = [
                {
                    "mac_address": d.mac_address,
                    "ip_address": d.ip_address,
                    "vendor": d.vendor,
                }
                for d in self.known_devices
            ]
            with self.known_devices_path.open('w') as f:
                json.dump(data_to_save, f, indent=4)
            logger.info(f"Saved {len(data_to_save)} known devices to {self.known_devices_path}.")
        except Exception as e:
            logger.error(f"Error writing to {self.known_devices_path}: {e}")

    def merge_scan_results(
        self,
        nm_result: Dict,
        vendor_db: VendorDatabase
    ) -> Tuple[List[Device], List[Device]]:
        """
        Take nmap scan results, update known devices, and identify unknown devices.
        Returns (connected_known_devices, new_unknown_devices).
        """
        connected_devices = []
        unknown_devices = []

        # Map known MAC -> Device for quick lookup
        known_dict = {dev.mac_address: dev for dev in self.known_devices}

        all_hosts = nm_result.all_hosts() if hasattr(nm_result, "all_hosts") else []
        for host in all_hosts:
            state = nm_result[host].state() if hasattr(nm_result[host], "state") else "down"
            if state == "up":
                mac = nm_result[host]['addresses'].get('mac', 'UNKNOWN').upper()
                ip = nm_result[host]['addresses'].get('ipv4', 'Unknown')

                if mac == 'UNKNOWN':
                    continue  # skip if no MAC

                vendor = vendor_db.get_vendor(mac)

                if mac in known_dict:
                    # Update existing known device
                    known_dict[mac].state = "up"
                    known_dict[mac].ip_address = ip
                    known_dict[mac].vendor = vendor
                    connected_devices.append(known_dict[mac])
                else:
                    # A new device that isn't in known_devices
                    device = Device(
                        mac_address=mac,
                        ip_address=ip,
                        vendor=vendor,
                        known=False,
                        state="up",
                    )
                    unknown_devices.append(device)

        logger.info(
            f"Connected known devices: {len(connected_devices)} | Unknown devices: {len(unknown_devices)}"
        )
        return connected_devices, unknown_devices