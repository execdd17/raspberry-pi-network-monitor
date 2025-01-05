import os
import time
import json
import logging
from typing import List, Tuple, Optional

import nmap
import influxdb_client
from influxdb_client import Point
from influxdb_client.client.write_api import SYNCHRONOUS

# from dotenv import load_dotenv
from device import Device  # Import the simplified Device data class

from pathlib import Path
import platform
import sys

from mac_vendor_lookup import MacLookup, MacVendorLookupError

# Load environment variables from .env file
# load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Read environment variables with default values
bucket: str = os.environ.get("INFLUXDB_BUCKET", "network_monitor")
org: str = os.environ.get("INFLUXDB_ORG", "your_org")
token: str = os.environ.get("INFLUXDB_TOKEN", "your_influxdb_token")
url: str = os.environ.get("INFLUXDB_URL", "http://influxdb:8086")
interval: int = int(os.environ.get("NETWORK_SCAN_INTERVAL", "300"))  # Default to 300 seconds (5 minutes)
known_devices_file: str = os.environ.get("KNOWN_DEVICES_FILE", "known_devices.json")

# Determine the absolute path to known_devices.json based on the script's location
script_dir: Path = Path(__file__).parent.resolve()
known_devices_path: Path = script_dir / known_devices_file

# Initialize InfluxDB client
client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
write_api = client.write_api(write_options=SYNCHRONOUS)

def is_admin() -> bool:
    """Check if the script is running with administrative/root privileges."""
    try:
        if platform.system() == "Windows":
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin()
        else:
            return os.geteuid() == 0
    except Exception as e:
        logger.error(f"Error checking administrative privileges: {e}")
        return False

def load_known_devices(file_path: Path) -> List[Device]:
    """Load known devices from a JSON file and return a list of Device instances."""
    try:
        with file_path.open('r') as f:
            devices_json = json.load(f)
        logger.info(f"Loaded {len(devices_json)} known devices from {file_path}.")

        # Convert dictionaries to Device instances
        known_devices: List[Device] = [
            Device(
                mac_address=device["mac_address"].upper(),
                state="down",  # Initial state as down; will be updated during scan
                known=True
            )
            for device in devices_json
        ]

        return known_devices
    except FileNotFoundError:
        logger.error(f"Known devices file not found: {file_path}")
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from {file_path}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error loading known devices: {e}")
    return []

def scan_network(network: str = "192.168.1.0/24") -> Optional[nmap.PortScanner]:
    """Perform a network scan using nmap for host discovery."""
    nm = nmap.PortScanner()
    logger.info(f"Starting network scan on {network}")
    try:
        nm.scan(hosts=network, arguments='-sn')  # Ping scan
        logger.info(f"Scan complete. {len(nm.all_hosts())} hosts found.")
        return nm
    except nmap.PortScannerError as e:
        logger.error(f"nmap scan error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during network scan: {e}")
    return None

def get_vendor(mac: str) -> str:
    """Retrieve the vendor/manufacturer for a given MAC address."""
    try:
        return MacLookup().lookup(mac)
    except MacVendorLookupError:
        return "Unknown"
    except Exception as e:
        logger.error(f"Error retrieving vendor for MAC {mac}: {e}")
        return "Unknown"

def process_scan_results(nm: nmap.PortScanner, known_devices: List[Device]) -> Tuple[List[Device], List[Device]]:
    """Process scan results to identify connected and unknown devices."""
    connected_devices: List[Device] = []
    unknown_devices: List[Device] = []

    # Create a dictionary for quick MAC lookup
    known_mac_dict = {device.mac_address: device for device in known_devices}

    for host in nm.all_hosts():
        if nm[host].state() == "up":
            mac: str = nm[host]['addresses'].get('mac', 'UNKNOWN').upper()
            state = "up"

            if mac == 'UNKNOWN':
                logger.debug(f"Host {host} is up but MAC address is unknown.")
                continue  # Skip hosts without MAC addresses

            vendor: str = get_vendor(mac)

            if mac in known_mac_dict:
                device = known_mac_dict[mac]
                device.state = "up"
                device.vendor = vendor
                connected_devices.append(device)
                logger.debug(f"Known device detected: MAC={mac}, Vendor={vendor}")
            else:
                unknown_device = Device(
                    mac_address=mac,
                    state=state,
                    known=False,
                    vendor=vendor
                )
                unknown_devices.append(unknown_device)
                logger.debug(f"Unknown device detected: MAC={mac}, Vendor={vendor}")

    logger.info(f"Connected devices: {len(connected_devices)}, Unknown devices: {len(unknown_devices)}")
    return connected_devices, unknown_devices

def write_to_influxdb(connected: List[Device], unknown: List[Device]) -> None:
    """Write connected and unknown device data to InfluxDB."""
    points: List[Point] = []

    # Add known (connected) devices
    for device in connected:
        point = Point("network_device") \
            .tag("mac_address", device.mac_address) \
            .tag("known", str(device.known)) \
            .field("state", device.state) \
            .field("vendor", device.vendor if device.vendor else "Unknown")
        points.append(point)

    # Add unknown devices
    for device in unknown:
        point = Point("network_device") \
            .tag("mac_address", device.mac_address) \
            .tag("known", str(device.known)) \
            .field("state", device.state) \
            .field("vendor", device.vendor if device.vendor else "Unknown")
        points.append(point)

    try:
        write_api.write(bucket=bucket, org=org, record=points)
        logger.info(f"Wrote {len(points)} points to InfluxDB.")
    except Exception as e:
        logger.error(f"Error writing to InfluxDB: {e}")

def main() -> None:
    """Main loop to perform network scans and write data to InfluxDB."""
    if not is_admin():
        logger.error("This script requires administrative/root privileges to run correctly.")
        logger.error("Please rerun the script with elevated privileges (e.g., using sudo).")
        sys.exit(1)

    # Update the vendor database
    try:
        MacLookup().update_vendors()
        logger.info("Updated MAC vendor database successfully.")
    except Exception as e:
        logger.error(f"Error updating MAC vendor database: {e}")

    known_devices: List[Device] = load_known_devices(known_devices_path)
    if not known_devices:
        logger.error("No known devices loaded. Exiting.")
        return

    while True:
        nm: Optional[nmap.PortScanner] = scan_network()
        if nm:
            connected, unknown = process_scan_results(nm, known_devices)
            write_to_influxdb(connected, unknown)
        else:
            logger.error("Network scan failed. Skipping this interval.")

        time.sleep(interval)

if __name__ == "__main__":
    main()
