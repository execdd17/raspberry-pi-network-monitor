#!/usr/bin/env python3

import os
import sys
import time
import logging
import argparse
import platform
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# External libraries
import nmap
from mac_vendor_lookup import MacLookup, VendorNotFoundError
import psycopg2
from psycopg2.extras import DictCursor
# from dotenv import load_dotenv

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

# ---------------------------------------------------------------------------
#  SCANNER INTERFACE
# ---------------------------------------------------------------------------
class Scanner:
    """A base class for any network scanner implementation."""
    def scan_network(self, network: str = "192.168.1.0/24", arguments: str = "-sn -PR") -> Dict:
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

    def scan_network(self, network: str = "192.168.1.0/24", arguments: str = "-sn -PR") -> Dict:
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
      - load_known_devices() for existing known devices
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

    def load_known_devices(self) -> Dict[str, Device]:
        """
        Returns a dict of {mac_address: Device} for devices with known=True in the DB.
        """
        known_devices = {}
        try:
            with self._get_connection() as conn, conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute("""
                    SELECT mac_address, ip_address, vendor, description, known, state, first_seen, last_seen
                    FROM devices
                    WHERE known = TRUE;
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
                        last_seen=row["last_seen"]
                    )
                    known_devices[mac] = dev
        except Exception as e:
            logger.error(f"Error loading known devices from Postgres: {e}")

        logger.info(f"Loaded {len(known_devices)} known devices from Postgres.")
        return known_devices

    def upsert_device(self, device: Device) -> None:
        """
        Insert a new device or update if it already exists. 
        first_seen is set if new; last_seen is always updated.
        """
        now = datetime.utcnow()
        device_mac = device.mac_address.upper()

        try:
            with self._get_connection() as conn, conn.cursor() as cur:
                # If the device exists, update. Otherwise, insert a new row.
                # We'll check by MAC (the primary key).
                cur.execute("""
                    SELECT mac_address FROM devices
                    WHERE mac_address = %s;
                """, (device_mac,))
                existing = cur.fetchone()

                if existing:
                    # Update existing device
                    cur.execute("""
                        UPDATE devices
                        SET ip_address = %s,
                            vendor = %s,
                            known = %s,
                            state = %s,
                            last_seen = %s
                        WHERE mac_address = %s;
                    """, (
                        device.ip_address,
                        device.vendor,
                        device.known,
                        device.state,
                        now,
                        device_mac
                    ))
                else:
                    # Insert new device
                    cur.execute("""
                        INSERT INTO devices 
                            (mac_address, ip_address, vendor, known, state, first_seen, last_seen)
                        VALUES (%s, %s, %s, %s, %s, %s, %s);
                    """, (
                        device_mac,
                        device.ip_address,
                        device.vendor,
                        device.known,
                        device.state,
                        now,
                        now
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

        # Load known devices from DB
        known_dict = self.pg_manager.load_known_devices()

        # Process scan results
        all_hosts = nm_result.all_hosts() if hasattr(nm_result, "all_hosts") else []
        logger.info(f"Processing {len(all_hosts)} hosts...")

        # Set to keep track of found MAC addresses
        found_macs = set()

        for host in all_hosts:
            logger.debug(f"looking at host: {host}")

            if nm_result[host].state() == "up":
                mac = nm_result[host]['addresses'].get('mac', 'UNKNOWN').upper()
                ip = nm_result[host]['addresses'].get('ipv4', 'Unknown')

                if mac == "UNKNOWN":
                    # Skip hosts without MAC addresses
                    logger.warning(f"{nm_result[host]} did not have a MAC address")
                    continue

                # Add to found MACs
                logger.debug(f"Adding {mac} to found_macs")
                found_macs.add(mac)

                # Lookup vendor
                vendor = self.vendor_db.get_vendor(mac)

                # Check if device is known
                if mac in known_dict:
                    logger.debug(f"Found known host {mac} {ip}. Setting it to up.")
                    # Update existing device
                    dev = known_dict[mac]
                    dev.state = "up"
                    dev.ip_address = ip
                    dev.vendor = vendor
                    # dev.known remains True
                else:
                    # Brand new device -> not known yet
                    logger.debug(f"Found unknown host {mac} {ip}. Setting it to up.")
                    dev = Device(
                        mac_address=mac,
                        ip_address=ip,
                        vendor=vendor,
                        known=False,  # Mark as unknown until we classify it
                        state="up"
                    )

                # Upsert in Postgres
                self.pg_manager.upsert_device(dev)

        # Now, mark known devices not found in the current scan as "down"
        for mac, device in known_dict.items():
            if mac not in found_macs:
                if device.state != "down":  # Only update if state is not already "down"
                    logger.debug(f"Did not find known host {mac} {device.ip_address}. Setting it to down.")
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
