import requests

latitude = 48.85
longitude = 2.35

url = (
    "https://api.open-meteo.com/v1/forecast"
    f"?latitude={latitude}&longitude={longitude}"
    "&daily=temperature_2m_min,temperature_2m_max,precipitation_sum,windspeed_10m_max"
    "&timezone=auto"
)

response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    print("Ville : Paris")
    print("Dates :", data["daily"]["time"])
    print("Temp. max :", data["daily"]["temperature_2m_max"])
    print("Temp. min :", data["daily"]["temperature_2m_min"])
else:
    print("Erreur :", response.status_code)
