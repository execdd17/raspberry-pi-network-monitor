import influxdb_client
import logging

from device import Device
from typing import List
from influxdb_client import Point
from influxdb_client.client.write_api import SYNCHRONOUS

logger = logging.getLogger(__name__)

class InfluxDBWriter:
    """
    Responsible for writing device data to InfluxDB.
    """
    def __init__(self, url: str, token: str, org: str, bucket: str):
        self.client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        self.bucket = bucket
        self.org = org

    def write_devices(self, devices: List[Device]) -> None:
        """
        Write device data to InfluxDB, tagging known devices and fields like IP address and vendor.
        """
        points = []
        for d in devices:
            point = (
                Point("network_device")
                .tag("mac_address", d.mac_address)
                .tag("known", str(d.known))
                .field("state", d.state)
                .field("vendor", d.vendor if d.vendor else "Unknown")
                .field("ip_address", d.ip_address if d.ip_address else "Unknown")
            )
            points.append(point)

        try:
            self.write_api.write(bucket=self.bucket, org=self.org, record=points)
            logger.info(f"Wrote {len(points)} device entries to InfluxDB.")
        except Exception as e:
            logger.error(f"Error writing to InfluxDB: {e}")