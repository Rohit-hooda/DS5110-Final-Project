from flask import Flask, jsonify, request, render_template
import pandas as pd
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Load the dataset
data_frame = pd.read_csv('../dataset/cleaned_data/2022_2024_combined_weather_data.csv')

# Ensure 'Date' is in datetime format
data_frame['Date'] = pd.to_datetime(data_frame['Date'])

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/weather', methods=['GET'])
def weather():
    county_name = request.args.get('countyName')
    info_type = request.args.get('typeOfInformation')
    print(f"County Name: {county_name}, Info Type: {info_type}")

    # Validate the parameters
    if not county_name or not info_type:
        return jsonify({"error": "Missing required parameters"}), 400

    # Check if the info_type is a valid column in the DataFrame
    if info_type not in data_frame.columns:
        return jsonify({"error": f"Invalid information type '{info_type}' provided."}), 400

    # Filter the data for the specific county
    filtered_data = data_frame[data_frame['County'] == county_name]

    if filtered_data.empty:
        print("No data found for the given county.")
        return jsonify({"error": "No data found for the given county"}), 404

    # Prepare data for the chart
    chart_data = filtered_data[['Date', info_type]].rename(columns={'Date': 'date', info_type: 'value'})
    chart_data['date'] = chart_data['date'].dt.strftime('%Y-%m-%d')  # Format date as string for JSON serialization
    chart_data = chart_data.to_dict(orient='records')

    return jsonify({"data": chart_data, "info_type": info_type, "county_name": county_name})

if __name__ == '__main__':
    app.run(debug=True)
