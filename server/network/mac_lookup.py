from typing import Optional
import requests
import logging
from .manufacturer_mapping import ManufacturerMapping

logger = logging.getLogger(__name__)

class MacLookupService:
    """Service to lookup MAC address manufacturer information"""
    BASE_URL = "https://api.maclookup.app/v2/macs/"
    
    @staticmethod
    def get_manufacturer(mac: str) -> Optional[str]:
        """
        Lookup manufacturer information for a MAC address
        Returns standardized manufacturer name if found, None otherwise
        """
        try:
            response = requests.get(f"{MacLookupService.BASE_URL}{mac}")
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("found"):
                    company = data.get("company")
                    return ManufacturerMapping.get_standardized_manufacturer(company)
        except Exception as e:
            logger.debug(f"MAC lookup failed for {mac}: {str(e)}")
        return None 