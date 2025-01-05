import logging
import json
import os
import platform
import time
import sys
import argparse

from pathlib import Path
from scanner import NmapScanner
from vender_database import MacLookupVendorDatabase
from device_manager import DeviceManager
from influxdb_writer import InfluxDBWriter

logger = logging.getLogger(__name__)

class NetworkMonitorApp:
    """
    Coordinates argument parsing, user commands, and the main monitoring loop.
    """
    def __init__(self) -> None:
        # Load environment variables
        # load_dotenv()

        # Read environment variables with default values
        self.bucket = os.environ.get("INFLUXDB_BUCKET", "network_monitor")
        self.org = os.environ.get("INFLUXDB_ORG", "your_org")
        self.token = os.environ.get("INFLUXDB_TOKEN", "your_influxdb_token")
        self.url = os.environ.get("INFLUXDB_URL", "http://influxdb:8086")
        self.interval = int(os.environ.get("NETWORK_SCAN_INTERVAL", "300"))  # Default 5 minutes
        self.known_devices_file = os.environ.get("KNOWN_DEVICES_FILE", "known_devices.json")

        script_dir = Path(__file__).parent.resolve()
        self.known_devices_path = script_dir / self.known_devices_file
        self.vendor_db_path = script_dir / "mac_vendors.db"

        # Initialize concrete implementations
        self.scanner = NmapScanner()
        self.vendor_db = MacLookupVendorDatabase(self.vendor_db_path, update_interval_days=7)
        self.device_manager = DeviceManager(self.known_devices_path)
        self.influx_writer = InfluxDBWriter(self.url, self.token, self.org, self.bucket)

    def check_admin_privileges(self) -> bool:
        """Check if the script is running with administrative/root privileges."""
        if platform.system() == "Windows":
            import ctypes
            return bool(ctypes.windll.shell32.IsUserAnAdmin())
        else:
            return os.geteuid() == 0

    def initialize_known_devices(self, network: str) -> None:
        """
        Perform a scan and overwrite known_devices.json with all up devices found in that scan.
        """
        logger.info("Initializing known_devices.json with current scan results...")
        scan_result = self.scanner.scan_network(network=network)
        if not scan_result:
            logger.error("Scan failed. Cannot initialize known_devices.json.")
            return

        new_known_devices = []
        hosts = scan_result.all_hosts() if hasattr(scan_result, "all_hosts") else []
        for host in hosts:
            if scan_result[host].state() == "up":
                mac = scan_result[host]['addresses'].get('mac', 'UNKNOWN').upper()
                ip = scan_result[host]['addresses'].get('ipv4', 'Unknown')
                if mac == 'UNKNOWN':
                    continue
                vendor = self.vendor_db.get_vendor(mac)
                new_known_devices.append({
                    "mac_address": mac,
                    "ip_address": ip,
                    "vendor": vendor
                })

        if not new_known_devices:
            logger.warning("No devices found during the scan. Exiting initialization.")
            return

        try:
            with self.known_devices_path.open('w') as f:
                json.dump(new_known_devices, f, indent=4)
            logger.info(f"Initialized known_devices.json with {len(new_known_devices)} devices.")
        except Exception as e:
            logger.error(f"Error writing {self.known_devices_path}: {e}")

    def run_monitoring_loop(self, network: str) -> None:
        """
        Continuously scan, merge results with known devices, identify unknowns, and write to InfluxDB.
        """
        while True:
            scan_result = self.scanner.scan_network(network=network)
            if scan_result:
                connected, unknown = self.device_manager.merge_scan_results(scan_result, self.vendor_db)
                
                # Write all devices (connected known + unknown) to Influx
                self.influx_writer.write_devices(connected + unknown)

                # Optionally, make unknown devices "known" automatically:
                # for dev in unknown:
                #     dev.known = True
                #     self.device_manager.known_devices.append(dev)
                # self.device_manager.save_known_devices()

            else:
                logger.error("Network scan failed. Skipping this interval.")

            time.sleep(self.interval)

    def main(self) -> None:
        """Entry point: parse args, handle initialization, or run monitoring."""
        parser = argparse.ArgumentParser(description="Network Monitoring Script")
        parser.add_argument(
            "--initialize",
            action="store_true",
            help="Initialize known_devices.json with scan results, then exit."
        )
        parser.add_argument(
            "--network",
            default="192.168.1.0/24",
            help="Network CIDR to scan (default: 192.168.1.0/24)"
        )
        args = parser.parse_args()

        # Check admin privileges
        if not self.check_admin_privileges():
            logger.error("This script requires administrative/root privileges.")
            sys.exit(1)

        # Update the vendor database if needed
        self.vendor_db.update_if_needed()

        # If we only want to initialize known_devices.json, do that and exit
        if args.initialize:
            self.initialize_known_devices(args.network)
            return

        # If not initializing, we run the monitoring loop
        # (Warn if we have zero known devices loaded)
        if not self.device_manager.known_devices:
            logger.warning("No known devices loaded. You may want to run --initialize first.")

        self.run_monitoring_loop(args.network)

# ---------------------------------------------------------------------------
#  SCRIPT ENTRY POINT
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app = NetworkMonitorApp()
    app.main()