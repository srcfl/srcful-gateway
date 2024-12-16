from typing import Optional
from server.devices.supported_devices.profiles import ModbusDeviceProfiles
from server.devices.profile_keys import ProfileKey

class ManufacturerMapping:
    """Maps MAC manufacturers to standardized inverter manufacturers"""
    
    @staticmethod
    def get_standardized_manufacturer(company: Optional[str]) -> Optional[str]:
        """
        Get standardized manufacturer name by looking for keywords in company name
        Returns standardized name if found, None otherwise
        """
        if not company:
            return None
            
        company = company.lower()
        profiles = ModbusDeviceProfiles().get_supported_devices()
        
        # Check each profile's keywords, name and display name
        for profile in profiles:
            keywords = [profile.name.lower(), profile.display_name.lower()]
            
            # Add any additional keywords from profile
            if hasattr(profile, ProfileKey.KEYWORDS):
                keywords.extend([k.lower() for k in profile.keywords])
                
            if any(keyword in company for keyword in keywords):
                return profile.name.lower()
                
        return None 