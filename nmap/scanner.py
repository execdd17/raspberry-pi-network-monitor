import logging
import nmap
from typing import Dict

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Scanner:
    """
    A base class that defines how a network scanner should behave.
    Concrete implementations should override `scan_network`.
    """
    def scan_network(self, network: str = "192.168.1.0/24", arguments: str = "-sn") -> Dict:
        """Perform a network scan and return a dict-like result."""
        raise NotImplementedError("scan_network must be overridden by subclasses.")

class VendorDatabase:
    """
    A base class that defines how a MAC vendor database should behave.
    Concrete implementations should override `update_if_needed` and `get_vendor`.
    """
    def update_if_needed(self) -> None:
        """Update the vendor database if it is outdated or doesn't exist."""
        raise NotImplementedError("update_if_needed must be overridden by subclasses.")

    def get_vendor(self, mac: str) -> str:
        """Lookup a MAC's vendor/manufacturer."""
        raise NotImplementedError("get_vendor must be overridden by subclasses.")


class NmapScanner(Scanner):
    """
    A concrete network scanner using python-nmap.
    """
    def __init__(self) -> None:
        self.nm = nmap.PortScanner()

    def scan_network(self, network: str = "192.168.1.0/24", arguments: str = "-sn") -> Dict:
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
