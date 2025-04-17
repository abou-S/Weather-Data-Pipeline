import requests

cities = [
    {"name": "Paris", "latitude": 48.85, "longitude": 2.35},
    {"name": "Nouakchott", "latitude": 18.08, "longitude": -15.98},
    {"name": "Tokyo", "latitude": 35.68, "longitude": 139.69}
]

def fetch_weather(city):
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={city['latitude']}&longitude={city['longitude']}"
        "&daily=temperature_2m_min,temperature_2m_max,precipitation_sum,windspeed_10m_max"
        "&timezone=auto"
    )
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return {
            "city": city["name"],
            "dates": data["daily"]["time"],
            "temp_max": data["daily"]["temperature_2m_max"],
            "temp_min": data["daily"]["temperature_2m_min"],
            "precipitation": data["daily"]["precipitation_sum"],
            "windspeed": data["daily"]["windspeed_10m_max"]
        }
    else:
        print(f"Erreur pour {city['name']} : {response.status_code}")
        return None

def main():
    for city in cities:
        weather_data = fetch_weather(city)
        if weather_data:
            print(f"\n🌆 Ville : {weather_data['city']}")
            for i in range(len(weather_data["dates"])):
                print(f"{weather_data['dates'][i]} ➤ "
                      f"T°max: {weather_data['temp_max'][i]}°C | "
                      f"T°min: {weather_data['temp_min'][i]}°C | "
                      f"Pluie: {weather_data['precipitation'][i]}mm | "
                      f"Vent: {weather_data['windspeed'][i]} km/h")

if __name__ == "__main__":
    main()
