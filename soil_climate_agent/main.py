from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .agent import analyze_and_recommend
from market_price_agent import predict_market
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Soil and Climate Agent")

from typing import Optional
from .geocoding_service import get_coordinates

class LocationRequest(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_name: Optional[str] = None

class MarketRequest(BaseModel):
    commodity: str

@app.get("/")
def read_root():
    return {"message": "Soil and Climate Agent API is running."}

@app.post("/recommend")
def get_recommendation(location: LocationRequest):
    lat = location.latitude
    lon = location.longitude
    
    # Resolve location name if provided
    if location.location_name:
        coords = get_coordinates(location.location_name)
        if coords:
            lat = coords["lat"]
            lon = coords["lon"]
        else:
            raise HTTPException(status_code=400, detail=f"Could not find coordinates for '{location.location_name}'")
            
    if lat is None or lon is None:
        raise HTTPException(status_code=400, detail="Please provide either 'latitude'/'longitude' or a 'location_name'.")

    result = analyze_and_recommend(lat, lon)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result

@app.post("/market_predict")
def get_market_prediction(request: MarketRequest):
    result = predict_market(request.commodity)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
