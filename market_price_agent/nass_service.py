import requests
import os
import json
from datetime import datetime

def get_historical_prices(commodity: str, year_start: int, year_end: int):
    """
    Fetches historical price data from USDA NASS Quick Stats.
    If NASS_API_KEY is missing, returns realistic mock data.
    """
    api_key = os.getenv("NASS_API_KEY")
    
    if not api_key:
        print("⚠️ No NASS_API_KEY found. Using MOCK data.")
        return _get_mock_data(commodity, year_start, year_end)

    url = "https://quickstats.nass.usda.gov/api/api_GET"
    
    # NASS Query Parameters for "Price Received"
    params = {
        "key": api_key,
        "commodity_desc": commodity.upper(),
        "statisticcat_desc": "PRICE RECEIVED",
        #"unit_desc": "BU", # Removing strict unit check to avoid 400 errors
        "freq_desc": "MONTHLY",
        "year__GE": year_start,
        "year__LE": year_end,
        "format": "JSON"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return _process_nass_response(data)
    except Exception as e:
        print(f"NASS API Error: {e}")
        return _get_mock_data(commodity, year_start, year_end)

def _process_nass_response(data):
    """
    Simplifies the complex NASS JSON into a list of {date, price}.
    """
    results = []
    if "data" not in data:
        return results
        
    for item in data["data"]:
        try:
            year = item["year"]
            # NASS uses "JAN", "FEB" or "YEAR"
            period = item["reference_period_desc"]
            if period == "YEAR":
                continue # Skip yearly averages, we want monthly
                
            # Convert "JAN" to 1, etc.
            try:
                month = datetime.strptime(period, "%b").month
            except:
                continue
                
            price = float(item["Value"].replace(",", ""))
            
            results.append({
                "date": f"{year}-{month:02d}-01",
                "price": price
            })
        except:
            continue
            
    # Sort by date
    results.sort(key=lambda x: x["date"])
    return results

def _get_mock_data(commodity, start, end):
    """
    Returns realistic mock price data for testing.
    """
    results = []
    base_price = 4.50 if commodity.upper() == "CORN" else 12.00 # Soybeans are more expensive
    
    import random
    random.seed(42) # Consistent mock data
    
    for year in range(start, end + 1):
        for month in range(1, 13):
            # Add some seasonality and random noise
            seasonality = 0.5 if month in [10, 11] else 0 # Harvest dip
            noise = random.uniform(-0.5, 0.5)
            price = base_price + noise - seasonality
            
            results.append({
                "date": f"{year}-{month:02d}-01",
                "price": round(price, 2)
            })
            
    return results
