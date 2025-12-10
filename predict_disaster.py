import joblib
import os
import requests

# Load trained model
BASE_DIR = os.path.dirname (os.path.dirname (os.path.abspath (__file__)))
MODEL_PATH = os.path.join (BASE_DIR, 'ml', 'disaster_model.pkl')
model = joblib.load (MODEL_PATH)

# Tomorrow.io API setup
TOMORROW_API_KEY = "cQhFgEteYtT0ZYmniqDlywJQEm41t8cx"
TOMORROW_API_URL = "https://api.tomorrow.io/v4/weather/realtime"

def get_weather_features(location):
    # Step 1: Get lat/lon from OpenStreetMap
    geo_url = f"https://nominatim.openstreetmap.org/search?q={location}&format=json"
    headers = {"User-Agent": "DisasterPredictorApp/1.0 (contact@example.com)"}

    try:
        response = requests.get (geo_url, headers=headers, timeout=10)
        response.raise_for_status ()
        geo_response = response.json ()
    except Exception as e:
        raise ValueError (f"❌ Geolocation fetch error: {str (e)}")

    if not geo_response or 'lat' not in geo_response[0] or 'lon' not in geo_response[0]:
        raise ValueError ("❌ Location not found or geolocation response is invalid.")

    lat = geo_response[0]['lat']
    lon = geo_response[0]['lon']

    # ✅ Correct URL for real-time weather
    TOMORROW_API_URL = "https://api.tomorrow.io/v4/weather/realtime"

    # Step 2: Get real-time weather data
    params = {
        "location": f"{lat},{lon}",
        "apikey": TOMORROW_API_KEY,
        "units": "metric",
        "fields": ",".join ([
            "temperature", "humidity", "windSpeed", "precipitationProbability",
            "uvIndex", "sunriseTime", "sunsetTime"
        ])
    }

    try:
        response = requests.get (TOMORROW_API_URL, params=params, timeout=10)
        response.raise_for_status ()
        data = response.json ()
        print ("🌤️ Weather API response:", data)  # Optional: debug output
    except Exception as e:
        raise ValueError (f"❌ Weather API fetch error: {str (e)}")

    try:
        values = data['data']['values']
        temperature = values.get ('temperature')
        humidity = values.get ('humidity')
        rain_probability = values.get ('precipitationProbability')
        wind_speed = values.get ('windSpeed')

        # Optional: log the data
        print ("✅ Weather Values Extracted:")
        print (
            f"🌡️ Temp: {temperature}°C, 💧 Humidity: {humidity}%, 🌧️ Rain Prob: {rain_probability}%, 💨 Wind: {wind_speed} km/h")

        if None in [temperature, humidity, rain_probability, wind_speed]:
            raise ValueError ("⚠️ Missing required weather values.")

    except Exception as e:
        raise ValueError ("⚠️ Failed to parse weather data: " + str (e))

    return [temperature, humidity, rain_probability, wind_speed]


def predict_disaster(location):
    try:
        features = get_weather_features (location)
        prediction = model.predict ([features])[0]
        return f"🌪️ Disaster Risk Detected: {prediction}" if prediction != 'None' else "✅ No Disaster Risk"
    except Exception as e:
        return f"📍 Location: {location}\n{str (e)}"
