"""
Station Configuration - Configurable station information.
"""

# Station Information
STATION_CONFIG = {
    "station_name": "Central Railway Station",
    "station_code": "CRS",
    "total_platforms": 3,
    "platform_ids": ["P1", "P2", "P3"],
    "location": "City Center",
    "zone": "Central Zone"
}

# Station metadata that can be displayed
def get_station_info():
    """Get station information."""
    return STATION_CONFIG

def get_station_name():
    """Get station name."""
    return STATION_CONFIG["station_name"]

def get_total_platforms():
    """Get total number of platforms."""
    return STATION_CONFIG["total_platforms"]
