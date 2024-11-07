import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
import requests
import json
import os

## NOTE: Not being used currently
#Mateo
# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after=36000)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

# List of coordinates (latitude and longitude) for each county
coordinates_list = [
    {"latitude": 41.7003, "longitude": -70.3002, "county": "Barnstable"},
    {"latitude": 42.3118, "longitude": -73.1822, "county": "Berkshire"},
    {"latitude": 41.7938, "longitude": -71.1350, "county": "Bristol"},
    {"latitude": 41.4033, "longitude": -70.6693, "county": "Dukes"},
    {"latitude": 42.6334, "longitude": -70.7829, "county": "Essex"},
    {"latitude": 42.5795, "longitude": -72.6151, "county": "Franklin"},
    {"latitude": 42.1175, "longitude": -72.6009, "county": "Hampden"},
    {"latitude": 42.3389, "longitude": -72.6417, "county": "Hampshire"},
    {"latitude": 42.4672, "longitude": -71.2874, "county": "Middlesex"},
    {"latitude": 41.2835, "longitude": -70.0995, "county": "Nantucket"},
    {"latitude": 42.1621, "longitude": -71.1912, "county": "Norfolk"},
    {"latitude": 41.9880, "longitude": -70.7528, "county": "Plymouth"},
    {"latitude": 42.3601, "longitude": -71.0589, "county": "Suffolk"},
    {"latitude": 42.4002, "longitude": -71.9065, "county": "Worcester"}
]

# List to store each DataFrame for each location
all_dataframes = []

# Function to fetch and process weather data for a given set of coordinates
def fetch_weather_data(latitude, longitude, county_name):
    url = "https://historical-forecast-api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": "2022-01-01",
        "end_date": "2024-10-30",
        "daily": ["weather_code", "temperature_2m_max", "temperature_2m_min", "sunrise", "sunset",
                  "daylight_duration", "sunshine_duration", "uv_index_max", "uv_index_clear_sky_max",
                  "precipitation_sum", "rain_sum", "showers_sum", "snowfall_sum",
                  "precipitation_hours", "precipitation_probability_max", "wind_speed_10m_max", "wind_gusts_10m_max"],
        "timezone": "America/New_York"
    }
    responses = openmeteo.weather_api(url, params=params)

    # Process the response for the given coordinates
    response = responses[0]

    # Process daily data
    daily = response.Daily()
    daily_data = {
        "date": pd.date_range(
            start=pd.to_datetime(daily.Time(), unit="s", utc=True),
            end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=daily.Interval()),
            inclusive="left"
        ),
        "county": county_name,
        "latitude": latitude,
        "longitude": longitude,
        "weather_code": daily.Variables(0).ValuesAsNumpy(),
        "temperature_2m_max": daily.Variables(1).ValuesAsNumpy(),
        "temperature_2m_min": daily.Variables(2).ValuesAsNumpy(),
        "sunrise": daily.Variables(3).ValuesAsNumpy(),
        "sunset": daily.Variables(4).ValuesAsNumpy(),
        "daylight_duration": daily.Variables(5).ValuesAsNumpy(),
        "sunshine_duration": daily.Variables(6).ValuesAsNumpy(),
        "uv_index_max": daily.Variables(7).ValuesAsNumpy(),
        "uv_index_clear_sky_max": daily.Variables(8).ValuesAsNumpy(),
        "precipitation_sum": daily.Variables(9).ValuesAsNumpy(),
        "rain_sum": daily.Variables(10).ValuesAsNumpy(),
        "showers_sum": daily.Variables(11).ValuesAsNumpy(),
        "snowfall_sum": daily.Variables(12).ValuesAsNumpy(),
        "precipitation_hours": daily.Variables(13).ValuesAsNumpy(),
        "precipitation_probability_max": daily.Variables(14).ValuesAsNumpy(),
        "wind_speed_10m_max": daily.Variables(15).ValuesAsNumpy(),
        "wind_gusts_10m_max": daily.Variables(16).ValuesAsNumpy()
    }

    # Convert to DataFrame and add to list
    daily_dataframe = pd.DataFrame(data=daily_data)
    all_dataframes.append(daily_dataframe)

# Loop through each set of coordinates and fetch weather data
for coords in coordinates_list:
    fetch_weather_data(coords["latitude"], coords["longitude"], coords["county"])

# Combine all dataframes into a single dataframe
final_dataframe = pd.concat(all_dataframes, ignore_index=True)

# Export to CSV
final_dataframe.to_csv("../Dataset/raw_data/massachusetts_counties_weather_data.csv", index=False)
print("Data has been saved to massachusetts_counties_weather_data.csv")



# AQI

# Define a list of latitude and longitude for Massachusetts counties
counties = {
    "Barnstable": (41.7504, -70.2020),
    "Berkshire": (42.4477, -73.2526),
    "Bristol": (41.7992, -71.1553),
    "Dukes": (41.3882, -70.6058),
    "Essex": (42.6403, -70.8290),
    "Franklin": (42.5876, -72.6022),
    "Hampden": (42.1015, -72.6462),
    "Hampshire": (42.2916, -72.6087),
    "Middlesex": (42.4375, -71.2425),
    "Nantucket": (41.2835, -70.0995),
    "Norfolk": (42.1331, -71.1975),
    "Plymouth": (41.9080, -70.3650),
    "Suffolk": (42.3601, -71.0589),
    "Worcester": (42.2626, -71.8023)
}

# API Key
api_key = 'KEY'  # Replace with your actual OpenWeatherMap API key

# Define start and end timestamps
start_timestamp = 1640995200  # January 1, 2022
end_timestamp = 1729939200    # October 30, 2024

# Create a directory to save JSON files
output_dir = 'ma_air_pollution_history'
os.makedirs(output_dir, exist_ok=True)

# Make requests for each county and save the response
for county, (lat, lon) in counties.items():
    # Construct the API request URL
    url = f'https://api.openweathermap.org/data/2.5/air_pollution/history?lat={lat}&lon={lon}&start={start_timestamp}&end={end_timestamp}&appid={api_key}'

    # Make the API request
    response = requests.get(url)

    if response.status_code == 200:
        # Save the response JSON to a file
        json_file_path = os.path.join(output_dir, f'{county}_air_pollution_history.json')
        with open(json_file_path, 'w') as json_file:
            json.dump(response.json(), json_file, indent=4)
        print(f'Successfully saved historical data for {county} to {json_file_path}.')
    else:
        print(f'Failed to retrieve data for {county}: {response.status_code} - {response.text}')


import pandas as pd
import json
import os

# Directory containing the JSON files
json_directory = 'ma_air_pollution_history'

# Loop through all JSON files in the directory
for json_file in os.listdir(json_directory):
    if json_file.endswith('.json'):
        json_file_path = os.path.join(json_directory, json_file)

        # Load the JSON file
        with open(json_file_path, 'r') as file:
            data = json.load(file)

        # Extract the list of air quality entries from the JSON data
        entries = data.get("list", [])

        # Create a DataFrame with the desired columns
        df = pd.DataFrame(columns=["dt", "aqi", "co", "no", "no2", "o3", "so2", "pm2_5", "pm10", "nh3"])

        # Populate the DataFrame
        rows = []  # List to collect row dictionaries

        for entry in entries:
            # Extract each required field
            row = {
                "dt": pd.to_datetime(entry["dt"], unit='s', utc=True),  # Convert to UTC datetime
                "aqi": entry["main"]["aqi"],
                "co": entry["components"].get("co", ""),
                "no": entry["components"].get("no", ""),
                "no2": entry["components"].get("no2", ""),
                "o3": entry["components"].get("o3", ""),
                "so2": entry["components"].get("so2", ""),
                "pm2_5": entry["components"].get("pm2_5", ""),
                "pm10": entry["components"].get("pm10", ""),
                "nh3": entry["components"].get("nh3", "")
            }
            rows.append(row)  # Collect each row dictionary

        # Create DataFrame from the collected rows
        df = pd.DataFrame(rows)

        # Generate CSV file name by replacing .json with .csv
        csv_file_name = json_file.replace('.json', '.csv')
        csv_file_path = os.path.join(json_directory, csv_file_name)

        # Save the DataFrame to a CSV file
        df.to_csv(csv_file_path, index=False)

        print(f"CSV file '{csv_file_name}' has been created successfully.")
