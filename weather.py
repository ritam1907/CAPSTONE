import requests

def get_current_weather(latitude: float = 18.62, longitude: float = 73.80):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": ["temperature_2m", "relative_humidity_2m", "weather_code", "is_day"],
        "timezone": "auto"
    }
    response = requests.get(url, params=params, timeout=10)
    if response.status_code != 200:
        raise RuntimeError(f"Failed to fetch weather: {response.status_code}")
    return response.json()["current"]

def weather_to_target_vector(weather_data: dict):
    code = weather_data["weather_code"]
    is_day = bool(weather_data["is_day"])
    temp = weather_data["temperature_2m"]

    # ["danceability", "energy", "speechiness", "acousticness", "instrumentalness", "liveness", "valence", "tempo", "loudness"]

    if code in [0, 1]: 
        condition = "Sunny / Clear Sky"
        vector = {
            "danceability": 0.70, "energy": 0.75, "speechiness": 0.05, 
            "acousticness": 0.15, "instrumentalness": 0.05, "liveness": 0.15, 
            "valence": 0.80, "tempo": 125.0, "loudness": -6.0
        }
    elif code in [2, 3]: 
        condition = "Cloudy / Overcast"
        vector = {
            "danceability": 0.50, "energy": 0.50, "speechiness": 0.04, 
            "acousticness": 0.40, "instrumentalness": 0.10, "liveness": 0.12, 
            "valence": 0.50, "tempo": 105.0, "loudness": -9.0
        }
    elif code in [51, 53, 55, 61, 63, 65, 80, 81, 82]:
        condition = "Rainy / Drizzle"
        vector = {
            "danceability": 0.35, "energy": 0.35, "speechiness": 0.04, 
            "acousticness": 0.70, "instrumentalness": 0.25, "liveness": 0.10, 
            "valence": 0.25, "tempo": 85.0, "loudness": -14.0
        }
    elif code in [95, 96, 99]: 
        condition = "Thunderstorm"
        vector = {
            "danceability": 0.45, "energy": 0.85, "speechiness": 0.08, 
            "acousticness": 0.10, "instrumentalness": 0.20, "liveness": 0.20, 
            "valence": 0.20, "tempo": 130.0, "loudness": -5.0
        }
    else:
        condition = "Misty / Foggy"
        vector = {
            "danceability": 0.40, "energy": 0.40, "speechiness": 0.04, 
            "acousticness": 0.60, "instrumentalness": 0.30, "liveness": 0.10, 
            "valence": 0.40, "tempo": 95.0, "loudness": -11.0
        }


    if not is_day:
        condition += " (Night)"
        vector["energy"] = max(0.10, vector["energy"] - 0.20)
        vector["valence"] = max(0.10, vector["valence"] - 0.10)
        vector["acousticness"] = min(0.95, vector["acousticness"] + 0.15)
        vector["tempo"] = max(70.0, vector["tempo"] - 15.0)

    return condition, vector