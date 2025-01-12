#!/usr/bin/env python3

import os
import sys
import time
import logging
import argparse
import platform
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# External libraries
import nmap
from mac_vendor_lookup import MacLookup, VendorNotFoundError
import psycopg2
from psycopg2.extras import DictCursor
import json  # Added for JSON serialization

# ---------------------------------------------------------------------------
#  LOGGING SETUP
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
#  DATA MODEL
# ---------------------------------------------------------------------------
@dataclass
class Device:
    mac_address: str
    ip_address: str
    vendor: str
    description: Optional[str]
    known: bool = False
    state: str = "down"
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    open_ports: List[Dict[str, str]] = field(default_factory=list)  # Updated field

# ---------------------------------------------------------------------------
#  SCANNER INTERFACE
# ---------------------------------------------------------------------------
class Scanner:
    """A base class for any network scanner implementation."""
    def scan_network(self, network: str = "192.168.1.0/24", arguments: str = "-PR") -> Dict:
        raise NotImplementedError("scan_network must be overridden by subclasses.")

# ---------------------------------------------------------------------------
#  VENDOR DATABASE INTERFACE
# ---------------------------------------------------------------------------
class VendorDatabase:
    """A base class for a MAC vendor database."""
    def update_if_needed(self) -> None:
        raise NotImplementedError("update_if_needed must be overridden by subclasses.")

    def get_vendor(self, mac: str) -> str:
        raise NotImplementedError("get_vendor must be overridden by subclasses.")

# ---------------------------------------------------------------------------
#  CONCRETE IMPLEMENTATIONS
# ---------------------------------------------------------------------------
class NmapScanner(Scanner):
    """Concrete scanner using python-nmap."""
    def __init__(self) -> None:
        self.nm = nmap.PortScanner()

    def scan_network(self, network: str = "192.168.1.0/24", arguments: str = "-PR -F") -> Dict:
        logger.info(f"Starting network scan on {network} with arguments '{arguments}'")
        try:
            self.nm.scan(hosts=network, arguments=arguments)
            logger.info(f"Scan complete. {len(self.nm.all_hosts())} hosts found.")
            return self.nm
        except nmap.PortScannerError as e:
            logger.error(f"nmap scan error: {e}")
            return {}
        except Exception as e:
            logger.error(f"Unexpected error during network scan: {e}")
            return {}

class MacLookupVendorDatabase(VendorDatabase):
    """Concrete vendor database using mac_vendor_lookup."""
    def __init__(self, vendor_db_path: str) -> None:
        self.vendor_db_path = vendor_db_path
        self.mac_lookup = MacLookup()

    def update_if_needed(self) -> None:
        logger.info("Updating MAC vendor database...")
        self.mac_lookup.update_vendors()
        logger.info("MAC vendor database updated successfully.")

    def get_vendor(self, mac: str) -> str:
        try:
            return self.mac_lookup.lookup(mac)
        except VendorNotFoundError:
            return "Unknown"
        except Exception as e:
            logger.error(f"Error retrieving vendor for MAC {mac}: {e}")
            return "Unknown"

# ---------------------------------------------------------------------------
#  POSTGRES DEVICE MANAGER
# ---------------------------------------------------------------------------
class PostgresDeviceManager:
    """
    Manages device records in PostgreSQL:
      - load_all_devices() for existing devices
      - upsert_device() for inserting/updating a device record
    """
    def __init__(self,
                 db_host: str,
                 db_port: int,
                 db_name: str,
                 db_user: str,
                 db_password: str):
        self.db_host = db_host
        self.db_port = db_port
        self.db_name = db_name
        self.db_user = db_user
        self.db_password = db_password

    def _get_connection(self):
        return psycopg2.connect(
            host=self.db_host,
            port=self.db_port,
            dbname=self.db_name,
            user=self.db_user,
            password=self.db_password
        )
    
    def load_all_devices(self) -> Dict[str, Device]:
        """
        Returns a dict of {mac_address: Device} for all devices in the DB.
        """
        all_devices = {}
        try:
            with self._get_connection() as conn, conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute("""
                    SELECT mac_address, ip_address, vendor, description, known, state, first_seen, last_seen, open_ports
                    FROM devices;
                """)
                rows = cur.fetchall()
                for row in rows:
                    mac = row["mac_address"].upper()
                    dev = Device(
                        mac_address=mac,
                        ip_address=row["ip_address"],
                        vendor=row["vendor"],
                        description=row["description"],
                        known=row["known"],
                        state=row["state"],
                        first_seen=row["first_seen"],
                        last_seen=row["last_seen"],
                        open_ports=row["open_ports"] if row["open_ports"] else []
                    )
                    all_devices[mac] = dev
        except Exception as e:
            logger.error(f"Error loading all devices from Postgres: {e}")

        logger.info(f"Loaded {len(all_devices)} devices from Postgres.")
        return all_devices

    def upsert_device(self, device: Device) -> None:
        """
        Insert a new device or update if it already exists. 
        first_seen is set if new; last_seen is always updated.
        """
        now = datetime.utcnow()
        device_mac = device.mac_address.upper()

        try:
            with self._get_connection() as conn, conn.cursor() as cur:
                # Check if the device exists
                cur.execute("""
                    SELECT mac_address FROM devices
                    WHERE mac_address = %s;
                """, (device_mac,))
                existing = cur.fetchone()

                # Serialize open_ports to JSON
                open_ports_json = json.dumps(device.open_ports)

                if existing:
                    # Update existing device and set first_seen if it is NULL
                    cur.execute("""
                        UPDATE devices
                        SET ip_address = %s,
                            state = %s,
                            last_seen = %s,
                            open_ports = %s,
                            first_seen = COALESCE(first_seen, %s)
                        WHERE mac_address = %s;
                    """, (
                        device.ip_address,
                        device.state,
                        now,
                        open_ports_json,  # Serialized JSON
                        now,  # Set first_seen to now if it is NULL
                        device_mac
                    ))
                else:
                    # Insert new device with 'description'
                    cur.execute("""
                        INSERT INTO devices 
                            (mac_address, ip_address, vendor, description, known, state, first_seen, last_seen, open_ports)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
                    """, (
                        device_mac,
                        device.ip_address,
                        device.vendor,
                        device.description,
                        device.known,
                        device.state,
                        now,
                        now,
                        open_ports_json  # Serialized JSON
                    ))
        except Exception as e:
            logger.error(f"Error upserting device {device_mac} in Postgres: {e}")

# ---------------------------------------------------------------------------
#  MAIN APPLICATION
# ---------------------------------------------------------------------------
class NetworkMonitorApp:
    """
    Coordinates argument parsing, scanning, vendor DB updates, and storing results in PostgreSQL.
    """
    def __init__(self) -> None:
        # Load environment variables
        # load_dotenv()

        # DB connection info (example env vars: DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS)
        self.db_host = os.environ.get("DB_HOST", "postgres")
        self.db_port = int(os.environ.get("DB_PORT", "5432"))
        self.db_name = os.environ.get("DB_NAME", "networkdb")
        self.db_user = os.environ.get("DB_USER", "admin")
        self.db_password = os.environ.get("DB_PASSWORD", "secret")

        self.interval = int(os.environ.get("NETWORK_SCAN_INTERVAL", "300"))  # Default: 5 min
        self.vendor_db_path = os.environ.get("MAC_VENDOR_DB_PATH", "/app/mac_vendors.db")

        # Initialize services
        self.scanner = NmapScanner()
        self.vendor_db = MacLookupVendorDatabase(self.vendor_db_path)
        self.pg_manager = PostgresDeviceManager(
            db_host=self.db_host,
            db_port=self.db_port,
            db_name=self.db_name,
            db_user=self.db_user,
            db_password=self.db_password
        )

    def check_admin_privileges(self) -> bool:
        """Check if script runs with admin/root privileges."""
        if platform.system() == "Windows":
            import ctypes
            return bool(ctypes.windll.shell32.IsUserAnAdmin())
        else:
            return os.geteuid() == 0

    def scan_and_process(self, network: str) -> None:
        """Perform a scan and update Postgres with known/unknown device info."""
        logger.info(f"Scanning network {network}...")
        nm_result = self.scanner.scan_network(network)
        if not nm_result:
            logger.error("No scan results returned.")
            return

        # Load all devices from DB (both known and unknown)
        all_devices = self.pg_manager.load_all_devices()

        # Process scan results
        all_hosts = nm_result.all_hosts() if hasattr(nm_result, "all_hosts") else []
        logger.info(f"Processing {len(all_hosts)} hosts...")

        # Set to keep track of found MAC addresses
        found_macs = set()

        for host in all_hosts:
            logger.debug(f"Looking at host: {host}")

            if nm_result[host].state() == "up":
                mac = nm_result[host]['addresses'].get('mac', 'UNKNOWN').upper()
                ip = nm_result[host]['addresses'].get('ipv4', 'Unknown')

                if mac == "UNKNOWN":
                    # Skip hosts without MAC addresses
                    logger.warning(f"{host} did not have a MAC address")
                    continue

                # Add to found MACs
                logger.debug(f"Adding {mac} ({ip}) to found_macs")
                found_macs.add(mac)

                # Extract open ports with service names
                open_ports = []

                # Check for TCP ports
                if 'tcp' in nm_result[host]:
                    for port, port_data in nm_result[host]['tcp'].items():
                        if port_data['state'] == 'open':
                            service = port_data.get('name', 'unknown')
                            open_ports.append({"port": port, "service": service})

                # Check for UDP ports
                if 'udp' in nm_result[host]:
                    for port, port_data in nm_result[host]['udp'].items():
                        if port_data['state'] == 'open':
                            service = port_data.get('name', 'unknown')
                            open_ports.append({"port": port, "service": service})

                logger.debug(f"Open ports for {mac} ({ip}): {open_ports}")

                if mac in all_devices:
                    logger.debug(f"Found existing host {mac} {ip}. Setting it to up.")
                    # Update existing device
                    dev = all_devices[mac]
                    dev.state = "up"
                    dev.ip_address = ip     # IP address could have changed; overwrite
                    dev.open_ports = open_ports  # Update open_ports
                else:
                    # Brand new device -> not known yet
                    logger.debug(f"Found unknown host {mac} {ip}. Setting it to up.")

                    # Lookup vendor
                    vendor = self.vendor_db.get_vendor(mac)

                    dev = Device(
                        mac_address=mac,
                        ip_address=ip,
                        vendor=vendor,
                        description=None,  # No description for unknown devices
                        known=False,      # Mark as unknown until we classify it
                        state="up",
                        open_ports=open_ports    # Assign open_ports
                    )

                # Upsert in Postgres
                self.pg_manager.upsert_device(dev)

        # Now, mark all devices not found in the current scan as "down"
        for mac, device in all_devices.items():
            if mac not in found_macs:
                if device.state != "down":  # Only update if state is not already "down"
                    logger.debug(f"Did not find host {mac} {device.ip_address}. Setting it to down.")
                    device.state = "down"
                    self.pg_manager.upsert_device(device)

        logger.info("Scan processing complete.")

    def main(self) -> None:
        """Main entry point for the script."""
        parser = argparse.ArgumentParser(description="Network Monitoring Script (Postgres-based)")
        parser.add_argument(
            "--network",
            default="192.168.1.0/24",
            help="Network CIDR to scan (default: 192.168.1.0/24)"
        )
        args = parser.parse_args()

        # Check privileges
        if not self.check_admin_privileges():
            logger.error("This script requires administrative/root privileges.")
            sys.exit(1)

        # Update vendor database if needed
        self.vendor_db.update_if_needed()

        # Continuous monitoring loop
        while True:
            self.scan_and_process(args.network)
            time.sleep(self.interval)

# ---------------------------------------------------------------------------
#  ENTRY POINT
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app = NetworkMonitorApp()
    app.main()
