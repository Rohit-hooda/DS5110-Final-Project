import os
from flask import Flask, jsonify, request, send_file, render_template_string
from flask_cors import CORS
from matplotlib import pyplot as plt
import seaborn as sns
import pandas as pd
import openmeteo_requests
import requests_cache
from retry_requests import retry
from shapely import wkt
import geopandas as gpd
import random
import folium

# Initialize Flask app and enable CORS
app = Flask(__name__)
CORS(app)

# Load and preprocess weather data
data_frame = pd.read_csv('../dataset/cleaned_data/2022_2024_combined_weather_data.csv')
data_frame['Date'] = pd.to_datetime(data_frame['Date'])

# Configure request caching and retry logic
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

# List of coordinates for each MA county
ma_counties_coordinates = [
    {"county_name": "Barnstable", "latitude": 41.7003, "longitude": -70.3002},
    {"county_name": "Berkshire", "latitude": 42.3118, "longitude": -73.1822},
    {"county_name": "Bristol", "latitude": 41.7938, "longitude": -71.1350},
    {"county_name": "Dukes", "latitude": 41.4033, "longitude": -70.6693},
    {"county_name": "Essex", "latitude": 42.6334, "longitude": -70.7829},
    {"county_name": "Franklin", "latitude": 42.5795, "longitude": -72.6151},
    {"county_name": "Hampden", "latitude": 42.1175, "longitude": -72.6009},
    {"county_name": "Hampshire", "latitude": 42.3389, "longitude": -72.6417},
    {"county_name": "Middlesex", "latitude": 42.4672, "longitude": -71.2874},
    {"county_name": "Nantucket", "latitude": 41.2835, "longitude": -70.0995},
    {"county_name": "Norfolk", "latitude": 42.1621, "longitude": -71.1912},
    {"county_name": "Plymouth", "latitude": 41.9880, "longitude": -70.7528},
    {"county_name": "Suffolk", "latitude": 42.3601, "longitude": -71.0589},
    {"county_name": "Worcester", "latitude": 42.4002, "longitude": -71.9065}
]

county_weather_data = {}


# Function to fetch weather data for a given county
def fetch_weather_data(county_name, latitude, longitude):
    """
    Fetch weather data for a given county using Open-Meteo API.

    Args:
        county_name (str): Name of the county.
        latitude (float): Latitude of the county.
        longitude (float): Longitude of the county.

    Returns:
        None
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
	    "current": ["temperature_2m", "relative_humidity_2m", "apparent_temperature", "precipitation", "weather_code", "wind_speed_10m", "wind_direction_10m", "wind_gusts_10m"],
	    "daily": ["weather_code", "temperature_2m_max", "temperature_2m_min", "sunrise", "sunset", "uv_index_max", "precipitation_probability_max", "wind_speed_10m_max", "wind_gusts_10m_max"],
        "timezone": "America/New_York",
        "temperature_unit": "fahrenheit",
        "wind_speed_unit": "mph",
        "precipitation_unit": "inch",
        "forecast_days": 7
    }
    responses = openmeteo.weather_api(url, params=params)

    response = responses[0]

    current = response.Current()
    current_temperature_2m = current.Variables(0).Value()
    current_relative_humidity_2m = current.Variables(1).Value()
    current_apparent_temperature = current.Variables(2).Value()
    current_precipitation = current.Variables(3).Value()
    current_weather_code = current.Variables(4).Value()
    current_wind_speed_10m = current.Variables(5).Value()
    current_wind_direction_10m = current.Variables(6).Value()
    current_wind_gusts_10m = current.Variables(7).Value()

    # Create DataFrame for current weather data
    current_data = {
        "time": [pd.to_datetime(current.Time(), unit="s", utc=True)],
        "temperature_2m": [current_temperature_2m],
        "relative_humidity_2m": [current_relative_humidity_2m],
        "apparent_temperature": [current_apparent_temperature],
        "precipitation": [current_precipitation],
        "weather_code": [current_weather_code],
        "wind_speed_10m": [current_wind_speed_10m],
        "wind_direction_10m": [current_wind_direction_10m],
        "wind_gusts_10m": [current_wind_gusts_10m],
    }

    current_df = pd.DataFrame(data=current_data)

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
        "uv_index_max": daily.Variables(5).ValuesAsNumpy(),
        "precipitation_probability_max": daily.Variables(6).ValuesAsNumpy(),
        "wind_speed_10m_max": daily.Variables(7).ValuesAsNumpy(),
        "wind_gusts_10m_max": daily.Variables(8).ValuesAsNumpy()
    }
    daily_df = pd.DataFrame(daily_data)

    county_weather_data[county_name] = {
        "current": current_df,
        "daily": daily_df
    }
    # print(f"Processed weather data for {county_name}")

# Fetch weather data for all counties
for county in ma_counties_coordinates:
    fetch_weather_data(county["county_name"], county["latitude"], county["longitude"])

ma_counties_boundaries = pd.read_csv('../dataset/cleaned_data/ma_counties_boundaries.csv')

ma_counties_boundaries['geometry'] = ma_counties_boundaries['geometry'].apply(wkt.loads)

ma_counties_gdf = gpd.GeoDataFrame(ma_counties_boundaries, geometry='geometry')

 
# Function to plot a heatmap for a given feature
def plot_heatmap(feature):
    """
    Plot a heatmap for a given weather feature (e.g., temperature, wind speed, etc.).

    Args:
        feature (str): The weather feature to plot (e.g., "temperature_2m_max").

    Returns:
        None
    """
    feature_data = pd.DataFrame()
    for county, weather_data in county_weather_data.items():
        daily_data = weather_data["daily"]
        feature_data[county] = daily_data[feature]

    feature_data.index = daily_data["date"].dt.date

    if feature in ["temperature_2m_max", "temperature_2m_min"]:
        cmap = "coolwarm"
    else:
        cmap = "Purples"

    plt.figure(figsize=(12, 8))
    heatmap = sns.heatmap(feature_data.transpose(), cmap=cmap, annot=True, fmt=".1f", cbar=True)

    color_bar = heatmap.collections[0].colorbar
    if feature == "temperature_2m_max" or feature == "temperature_2m_min":
        color_bar.set_label('Temperature (°F)', rotation=270, labelpad=20)
    elif feature == "precipitation_probability_max":
        color_bar.set_label('Precipitation Probability (%)', rotation=270, labelpad=20)
    elif feature == "wind_speed_10m_max" or feature == "wind_gusts_10m_max":
        color_bar.set_label('Wind Speed (mph)', rotation=270, labelpad=20)
    else:
        color_bar.set_label(feature, rotation=270, labelpad=20)

    if feature == "uv_index_max":
        plt.title(f"7-Day UV Index Forecast by County", fontsize=16)
    else:
        plt.title(f"7-Day {feature.replace('_', ' ').title()} Forecast by County", fontsize=16)

    plt.xlabel("Date", fontsize=12)
    plt.ylabel("County", fontsize=12)
    plt.xticks(rotation=45)

    images_folder_path = os.path.join(os.path.dirname(__file__), '..', 'Frontend', 'static', 'images')

    os.makedirs(images_folder_path, exist_ok=True)
    plt.savefig(os.path.join(images_folder_path, f'{feature}_heatmap.png'), bbox_inches='tight')

plot_heatmap("temperature_2m_max")
plot_heatmap("temperature_2m_min")
plot_heatmap("precipitation_probability_max")
plot_heatmap("wind_speed_10m_max")
plot_heatmap("wind_gusts_10m_max")
plot_heatmap("uv_index_max")

# Function to plot a boxplot for a given feature
def plot_boxplot(feature):
    """
    Plot a boxplot for a given weather feature by county.

    Args:
        feature (str): The weather feature to plot (e.g., "temperature_2m_max").

    Returns:
        None
    """
    valid_features = [
        "temperature_2m_max",
        "temperature_2m_min",
        "sunrise",
        "sunset",
        "uv_index_max",
        "precipitation_probability_max",
        "wind_speed_10m_max",
        "wind_gusts_10m_max"
    ]
    
    if feature not in valid_features:
        raise ValueError(f"Invalid feature: {feature}. Please choose from {', '.join(valid_features)}.")
    
    feature_data = []
    county_names = []
    
    for county, weather_data in county_weather_data.items():
        daily_data = weather_data["daily"]
        
        if feature in daily_data:
            feature_data.append(daily_data[feature]) 
            county_names.append(county)
    
    df = pd.DataFrame(feature_data).transpose()
    df.columns = county_names

    plt.figure(figsize=(12, 8))
    boxplot = sns.boxplot(data=df, palette="Set2")

    boxplot.set_title(f"Distribution of {feature.replace('_', ' ').title()} by County", fontsize=16)
    boxplot.set_xlabel("County", fontsize=12)
    boxplot.set_xticklabels(county_names, rotation=45, ha="right")
    if feature == "temperature_2m_max" or feature == "temperature_2m_min":
        plt.ylabel("Temperature (°F)", fontsize=12)
    elif feature == "wind_speed_10m_max" or feature == "wind_gusts_10m_max":
        plt.ylabel("Speed (mph)", fontsize=12)
    else:
        plt.ylabel(feature.replace("_", " ").capitalize(), fontsize=12)
    
    plt.xticks(rotation=45)
    images_folder_path = os.path.join(os.path.dirname(__file__), '..', 'Frontend', 'static', 'images')
    os.makedirs(images_folder_path, exist_ok=True)
    plt.savefig(os.path.join(images_folder_path, f'{feature}_boxplot.png'), bbox_inches='tight')
    
plot_boxplot("temperature_2m_max")
plot_boxplot("temperature_2m_min")
plot_boxplot("precipitation_probability_max")
plot_boxplot("wind_speed_10m_max")
plot_boxplot("wind_gusts_10m_max")
plot_boxplot("uv_index_max")

# Flask index route to display the map
@app.route('/')
def index():
    """
    Render the main map with weather data for Massachusetts counties.

    Args:
        None

    Returns:
        str: Rendered HTML string with the map.
    """
    # Create a base Folium map centered around Massachusetts
    m = folium.Map(location=[42.4072, -71.3824], zoom_start=7, tiles="cartodbpositron")

    def random_color():
        return f'#{random.randint(0, 255):02x}{random.randint(0, 255):02x}{random.randint(0, 255):02x}'

    for _, row in ma_counties_gdf.iterrows():
        county_name = row['NAME']
        weather_info = county_weather_data[county_name]["current"]
        
        popup_text = (
            f"Temperature: {round(weather_info['temperature_2m'].values[0])}°F<br>"
            f"Humidity: {weather_info['relative_humidity_2m'].values[0]}%<br>"
            f"Precipitation: {round(weather_info['precipitation'].values[0], 2)} in<br>"
            f"Wind Speed: {round(weather_info['wind_speed_10m'].values[0], 2)} mph<br>"
            f"Wind Direction: {round(weather_info['wind_direction_10m'].values[0], 2)}°<br>"
            f"Wind Gusts: {round(weather_info['wind_gusts_10m'].values[0], 2)} mph"
        )

        folium.GeoJson(
            row['geometry'],
            style_function=lambda feature, color=random_color(): {
                'fillColor': color,
                'color': 'black',
                'weight': 0.5,
                'fillOpacity': 0.6,
            },
            tooltip=folium.Tooltip(county_name),
            popup=folium.Popup(popup_text, max_width=300)
        ).add_to(m)

    map_html = m.get_root().render()

    return render_template_string('''{{ map_html|safe }}''', map_html=map_html)


# Flask route for weather data
@app.route('/weather', methods=['GET'])
def weather():
    """
    Fetch weather data for a given county within a date range and for selected features.

    Args:
        county_name (str): Name of the county.
        info_types (list): List of weather features to retrieve (e.g., temperature, wind speed).
        from_date (str): Start date in the format YYYY-MM-DD.
        to_date (str): End date in the format YYYY-MM-DD.

    Returns:
        jsonify: A JSON response containing the requested data or error message.
    """
    county_name = request.args.get('countyName')
    info_types = request.args.get('typeOfInformation').split(',')
    from_date = request.args.get('fromDate')
    to_date = request.args.get('toDate')

    if not county_name or not info_types or not from_date or not to_date:
        return jsonify({"error": "Missing required parameters"}), 400

    filtered_data = data_frame[(data_frame['County'] == county_name) & 
                               (data_frame['Date'] >= from_date) & 
                               (data_frame['Date'] <= to_date)]
    
    if filtered_data.empty:
        return jsonify({"error": "No data found for the given criteria"}), 404

    result_data = []
    for info_type in info_types:
        if info_type not in data_frame.columns:
            continue
        series_data = filtered_data[['Date', info_type]].rename(columns={info_type: 'value'}).dropna()
        result_data.append({
            "info_type": info_type,
            "values": series_data.to_dict(orient='records')
        })
        
    return jsonify({
        "county_name": county_name,
        "data": result_data
    })

if __name__ == '__main__':
    app.run(debug=True)
