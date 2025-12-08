import ssl
import certifi
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

def get_coordinates(location_name: str):
    """
    Converts a location name (e.g., "Ames, Iowa") to latitude and longitude.
    Uses OpenStreetMap's Nominatim API.
    """
    # Create a custom SSL context to avoid certificate errors
    ctx = ssl.create_default_context(cafile=certifi.where())
    # OSM requires a specific User-Agent. Using a unique one to avoid 403.
    geolocator = Nominatim(user_agent="soil_climate_agent_v1_aditya_demo", ssl_context=ctx)
    
    try:
        location = geolocator.geocode(location_name)
        if location:
            return {
                "lat": location.latitude,
                "lon": location.longitude,
                "address": location.address
            }
        else:
            return None
    except (GeocoderTimedOut, GeocoderServiceError) as e:
        print(f"Geocoding Error: {e}")
        return None
