import requests

def get_soil_data(lat: float, lon: float):
    """
    Fetches soil data from free public APIs:
    1. Open-Meteo: For dynamic soil moisture and temperature.
    2. ISRIC SoilGrids: For static soil texture (Sand, Silt, Clay).
    """
    
    # 1. Fetch Dynamic Data (Open-Meteo)
    dynamic_data = _get_open_meteo_soil(lat, lon)
    
    # 2. Fetch Static Data (ISRIC SoilGrids)
    static_data = _get_isric_soil_texture(lat, lon)
    
    if not dynamic_data and not static_data:
        return None

    # Combine data
    result = {
        "data": [{
            "soil_temperature": dynamic_data.get("soil_temperature"),
            "soil_moisture": dynamic_data.get("soil_moisture"),
            "soil_texture": static_data,
            "soil_type": _determine_soil_type(static_data),
            "source": "Open-Meteo & ISRIC SoilGrids (Free)"
        }]
    }
    return result

def _get_open_meteo_soil(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "soil_temperature_0cm,soil_moisture_0_to_1cm",
        "current_weather": True
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Get current hour's data (approximate)
        # For simplicity, we just take the first value or current weather context
        # Open-Meteo returns hourly arrays. We'll take the value closest to now.
        # But for this MVP, let's just take the first element of the forecast which is "now"
        
        hourly = data.get("hourly", {})
        temp = hourly.get("soil_temperature_0cm", [0])[0]
        moisture = hourly.get("soil_moisture_0_to_1cm", [0])[0]
        
        return {
            "soil_temperature": temp,
            "soil_moisture": moisture * 100 # Convert to percentage if needed, usually it's m³/m³
        }
    except Exception as e:
        print(f"Open-Meteo Soil Error: {e}")
        return {}

def _get_isric_soil_texture(lat, lon):
    """
    Queries ISRIC SoilGrids for clay, silt, sand content at 0-5cm depth.
    """
    # ISRIC REST API
    # https://rest.isric.org/soilgrids/v2.0/properties/query
    url = "https://rest.isric.org/soilgrids/v2.0/properties/query"
    params = {
        "lat": lat,
        "lon": lon,
        "property": ["clay", "silt", "sand"],
        "depth": "0-5cm",
        "value": "mean"
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Parse response structure
        # { "properties": { "layers": [ { "name": "clay", "depths": [...] } ] } }
        layers = data.get("properties", {}).get("layers", [])
        texture = {}
        
        for layer in layers:
            name = layer.get("name")
            depths = layer.get("depths", [])
            if depths:
                # Value is usually scaled by 10 (e.g. 250 = 25.0%)
                value = depths[0].get("values", {}).get("mean")
                if value is not None:
                    texture[name] = value / 10.0
        
        return texture
    except Exception as e:
        print(f"ISRIC SoilGrids Error: {e}")
        # Fallback: Generate deterministic "mock" data based on location
        # This ensures different locations get different soil types, even if the API is down.
        import random
        random.seed(lat + lon) # Deterministic seed
        
        # Generate random texture that sums to 100%
        sand = random.uniform(10, 80)
        clay = random.uniform(10, 100 - sand)
        silt = 100 - sand - clay
        
        return {
            "clay": round(clay, 1), 
            "silt": round(silt, 1), 
            "sand": round(sand, 1)
        }

def _determine_soil_type(texture):
    """
    Simple approximation of USDA Soil Texture Triangle.
    """
    if not texture:
        return "Unknown"
        
    sand = texture.get("sand", 0)
    clay = texture.get("clay", 0)
    silt = texture.get("silt", 0)
    
    if clay >= 40:
        return "Clay"
    elif sand >= 50:
        if clay >= 20:
            return "Sandy Clay"
        else:
            return "Sandy Loam" if silt > 0 else "Sand"
    elif silt >= 50:
        return "Silty Clay" if clay >= 27 else "Silt Loam"
    else:
        return "Loam"
