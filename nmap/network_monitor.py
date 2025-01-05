import os
import time
import json
import logging
from typing import List, Tuple, Optional

import nmap
import influxdb_client
from influxdb_client import Point
from influxdb_client.client.write_api import SYNCHRONOUS

from dotenv import load_dotenv
from device import Device  # Import the Device data class

from pathlib import Path
import subprocess
import platform
import re
import sys
import ctypes

# Load environment variables from .env file
load_dotenv()

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
    system = platform.system()
    try:
        if system == "Windows":
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
                device_name=device["device_name"],
                mac_address=device["mac_address"].upper(),
                device_type=device["device_type"],
                hostname="Unknown",  # Initial hostname as Unknown; will be updated during scan
                state="down",        # Initial state as down; will be updated during scan
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
    """Perform a network scan using nmap."""
    nm = nmap.PortScanner()
    logger.info(f"Starting network scan on {network}")
    try:
        nm.scan(hosts=network, arguments='-sn')  # Ping scan
        hosts: List[str] = nm.all_hosts()
        logger.info(f"Scan complete. {len(hosts)} hosts found.")
        return nm
    except nmap.PortScannerError as e:
        logger.error(f"nmap scan error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during network scan: {e}")
    return None

def get_mac_from_arp(ip: str) -> Optional[str]:
    """Retrieve the MAC address for a given IP from the ARP table."""
    system = platform.system()
    try:
        if system == "Windows":
            # Run 'arp -a <ip>' and parse the output
            output = subprocess.check_output(["arp", "-a", ip], text=True)
            match = re.search(r"([\da-fA-F]{2}[:-]){5}[\da-fA-F]{2}", output)
            if match:
                return match.group(0).upper()
        elif system in ("Linux", "Darwin"):
            # Run 'arp -n <ip>' and parse the output
            output = subprocess.check_output(["arp", "-n", ip], text=True)
            match = re.search(r"([\da-fA-F]{2}[:-]){5}[\da-fA-F]{2}", output)
            if match:
                return match.group(0).upper()
        else:
            logger.warning(f"Unsupported OS for ARP parsing: {system}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error retrieving ARP entry for {ip}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error retrieving ARP entry for {ip}: {e}")
    return None

def process_scan_results(nm: nmap.PortScanner, known_devices: List[Device]) -> Tuple[List[Device], List[Device]]:
    """Process scan results to identify connected and unknown devices."""
    connected_devices: List[Device] = []
    unknown_devices: List[Device] = []

    for host in nm.all_hosts():
        if nm[host].state() == "up":
            mac: str = nm[host]['addresses'].get('mac', 'UNKNOWN').upper()
            hostname: str = nm[host]['hostnames'][0]['name'] if nm[host]['hostnames'] else 'Unknown'
            vendor: Optional[str] = None

            if mac == 'UNKNOWN':
                # Attempt to retrieve MAC address from ARP table as a fallback
                mac = get_mac_from_arp(host)
                if not mac:
                    mac = 'UNKNOWN'

            if mac != 'UNKNOWN':
                # Attempt to get the vendor/manufacturer information from nmap's scan
                vendor = nm[host]['vendor'].get(mac, 'Unknown')

            if mac == 'UNKNOWN':
                # Devices without a MAC address are flagged as unknown
                unknown_device = Device(
                    device_name="Unknown",
                    mac_address="UNKNOWN",
                    device_type="Unknown",
                    hostname=hostname,
                    state="up",
                    known=False,
                    vendor=vendor
                )
                unknown_devices.append(unknown_device)
                continue

            # Check if the MAC address is in the known devices list
            known_device = next((device for device in known_devices if device.mac_address == mac), None)

            if known_device:
                # Update known device's hostname and state
                known_device.hostname = hostname
                known_device.state = "up"
                known_device.vendor = vendor
                connected_devices.append(known_device)
            else:
                # Device is not in known devices list
                unknown_device = Device(
                    device_name="Unknown",
                    mac_address=mac,
                    device_type="Unknown",
                    hostname=hostname,
                    state="up",
                    known=False,
                    vendor=vendor
                )
                logger.info(f"Unknown device: {unknown_device}")
                unknown_devices.append(unknown_device)

    logger.info(f"Connected devices: {len(connected_devices)}, Unknown devices: {len(unknown_devices)}")
    return connected_devices, unknown_devices

def write_to_influxdb(connected: List[Device], unknown: List[Device]) -> None:
    """Write connected and unknown device data to InfluxDB."""
    points: List[Point] = []

    # Add known (connected) devices
    for device in connected:
        point = Point("network_device") \
            .tag("device_name", device.device_name) \
            .tag("device_type", device.device_type) \
            .tag("state", device.state) \
            .field("hostname", device.hostname) \
            .field("mac_address", device.mac_address) \
            .field("known", device.known) \
            .field("vendor", device.vendor if device.vendor else "Unknown")
        points.append(point)

    # Add unknown devices
    for device in unknown:
        point = Point("network_device") \
            .tag("device_name", device.device_name) \
            .tag("device_type", device.device_type) \
            .tag("state", device.state) \
            .field("hostname", device.hostname) \
            .field("mac_address", device.mac_address) \
            .field("known", device.known) \
            .field("vendor", device.vendor if device.vendor else "Unknown")
        points.append(point)

    try:
        write_api.write(bucket=bucket, org=org, record=points)
        logger.info(f"Wrote {len(points)} points to InfluxDB.")
    except Exception as e:
        logger.error(f"Error writing to InfluxDB: {e}")

def ping_sweep(network: str = "192.168.1.0/24") -> None:
    """Ping all IP addresses in the specified subnet to populate the ARP table."""
    logger.info(f"Starting ping sweep on {network}")
    try:
        # Use nmap to perform a ping sweep
        subprocess.run(["nmap", "-sn", network], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        logger.info("Ping sweep complete.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error during ping sweep: {e}")

def main() -> None:
    """Main loop to perform network scans and write data to InfluxDB."""
    if not is_admin():
        logger.error("This script requires administrative/root privileges to run correctly.")
        logger.error("Please rerun the script with elevated privileges (e.g., using sudo).")
        sys.exit(1)

    known_devices: List[Device] = load_known_devices(known_devices_path)
    if not known_devices:
        logger.error("No known devices loaded. Exiting.")
        return

    while True:
        # Perform ping sweep to ensure ARP table is populated
        #ping_sweep(network="192.168.1.0/24")

        nm: Optional[nmap.PortScanner] = scan_network()
        if nm:
            connected, unknown = process_scan_results(nm, known_devices)
            write_to_influxdb(connected, unknown)
        else:
            logger.error("Network scan failed. Skipping this interval.")

        time.sleep(interval)

if __name__ == "__main__":
    main()
