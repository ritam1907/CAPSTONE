from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from weather import get_current_weather, weather_to_target_vector
from recommend import recommend_tracks

app = FastAPI(title="WeatherVane API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "online", "message": "WeatherVane API is running"}

@app.get("/api/recommend")
def get_recommendations(
    lat: float = Query(18.62, description="Latitude"),
    lon: float = Query(73.80, description="Longitude"),
    limit: int = Query(100, description="Number of track recommendations to return")
):
    try:
        weather_data = get_current_weather(lat, lon)
        condition_desc, target_vector = weather_to_target_vector(weather_data)
        
        # Pass the requested limit (100) into the recommendation engine
        recommendations = recommend_tracks(target_vector, top_n=limit)
        
        return {
            "weather": {
                "temperature": weather_data["temperature_2m"],
                "humidity": weather_data["relative_humidity_2m"],
                "condition": condition_desc,
                "is_day": bool(weather_data["is_day"])
            },
            "target_profile": target_vector,
            "songs": recommendations.to_dict(orient="records")
        }
    except Exception as e:
        return {"error": str(e)}