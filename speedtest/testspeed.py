import os
import time
import speedtest
import influxdb_client
from influxdb_client import Point
from influxdb_client.client.write_api import SYNCHRONOUS
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Read environment variables
bucket = os.environ.get("INFLUXDB_BUCKET")
org = os.environ.get("INFLUXDB_ORG")
token = os.environ.get("INFLUXDB_TOKEN")
url = os.environ.get("INFLUXDB_URL", "http://influxdb:8086")
interval = int(os.environ.get("SPEEDTEST_INTERVAL", "300"))  # Default to 300 seconds (5 minutes)

# Initialize InfluxDB client
client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
write_api = client.write_api(write_options=SYNCHRONOUS)

def run_speedtest():
    try:
        st = speedtest.Speedtest()
        st.get_best_server()
        download = st.download() / 1_000_000  # Convert to Mbps
        upload = st.upload() / 1_000_000      # Convert to Mbps
        ping = st.results.ping

        # Create data point
        point = Point("speedtest") \
            .tag("source", "internet") \
            .field("download", download) \
            .field("upload", upload) \
            .field("ping", ping)

        logger.info(f"Download: {download:.2f} Mbps, Upload: {upload:.2f} Mbps, Ping: {ping} ms")

        # Write to InfluxDB
        write_api.write(bucket=bucket, org=org, record=point)

    except Exception as e:
        logger.error(f"Error running speedtest: {e}")

def main():
    while True:
        run_speedtest()
        time.sleep(interval)

if __name__ == "__main__":
    main()