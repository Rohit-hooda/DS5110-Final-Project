import os
import pandas as pd
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

data_frame = pd.read_csv('../dataset/2022_massachusetts_counties_weather_data.csv')  

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/weather', methods=['GET'])
def weather():
    county_name = request.args.get('countyName')
    info_type = request.args.get('typeOfInformation')
    print(f"County Name: {county_name}, Info Type: {info_type}")

    if not county_name or not info_type:
        return jsonify({"error": "Missing required parameters"}), 400

    print("Available counties:", data_frame['county'].unique())
    print("Available max temperatures:", data_frame['temperature_2m_max'].unique())

    if info_type not in data_frame.columns:
        return jsonify({"error": f"Invalid information type '{info_type}' provided."}), 400

    filtered_data = data_frame[data_frame['county'] == county_name]

    if filtered_data.empty:
        print("No data found for the given county.")
        return jsonify({"error": "No data found for the given county"}), 404

    result_data = filtered_data[[info_type]]
    result = result_data.to_dict(orient='records')
    print(len(result))
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
