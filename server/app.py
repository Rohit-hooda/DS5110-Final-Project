import os
import pandas as pd
from flask import Flask, jsonify, request, render_template, send_file
from flask_cors import CORS
import matplotlib.pyplot as plt
import io
import matplotlib

matplotlib.use('Agg')  # Use the 'Agg' backend for non-GUI rendering

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

    # Create a figure with responsive sizing based on screen resolution
    fig, ax = plt.subplots(figsize=(10, 6))  # Adjust this size for responsiveness
    ax.plot(filtered_data['Date'], filtered_data[info_type], label=info_type, color='tab:blue', linewidth=2)
    
    ax.set_xlabel('Date', fontsize=14)
    ax.set_ylabel(info_type, fontsize=14)
    ax.set_title(f'{info_type} over Time for {county_name}', fontsize=16)
    
    # Add gridlines for readability
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)

    # Customize tick parameters for readability
    ax.tick_params(axis='x', rotation=45, labelsize=12)
    ax.tick_params(axis='y', labelsize=12)

    # Add a legend
    ax.legend(loc='upper left', fontsize=12)

    # Adjust layout to ensure everything fits without overlapping
    plt.tight_layout()

    # Save the figure to a BytesIO object
    img_io = io.BytesIO()
    plt.savefig(img_io, format='PNG', dpi=800)  # Increased DPI for better quality
    img_io.seek(0)

    # Send the image as a response with correct headers
    return send_file(img_io, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)
