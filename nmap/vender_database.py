import logging

from datetime import datetime, timedelta
from pathlib import Path
from mac_vendor_lookup import MacLookup, VendorNotFoundError

logger = logging.getLogger(__name__)

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
    

class MacLookupVendorDatabase(VendorDatabase):
    """
    A concrete vendor database implementation using mac_vendor_lookup.
    """
    def __init__(self, vendor_db_path: Path, update_interval_days: int = 7) -> None:
        self.vendor_db_path = vendor_db_path
        self.update_interval_days = update_interval_days
        self.mac_lookup = MacLookup()

    def update_if_needed(self) -> None:
        logger.info("Updating MAC vendor database...")
        self.mac_lookup.update_vendors()
        logger.info("MAC vendor database updated successfully.")

    def get_vendor(self, mac: str) -> str:
        """Lookup the MAC's vendor using mac_vendor_lookup."""
        try:
            return self.mac_lookup.lookup(mac)
        except VendorNotFoundError:
            return "Unknown"
        except Exception as e:
            logger.error(f"Error retrieving vendor for MAC {mac}: {e}")
            return "Unknown"
