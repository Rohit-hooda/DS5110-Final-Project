from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import pandas as pd

app = Flask(__name__)
CORS(app)

# Load dataset
data_frame = pd.read_csv('../dataset/cleaned_data/2022_2024_combined_weather_data.csv')
data_frame['Date'] = pd.to_datetime(data_frame['Date'])

@app.route('/', methods=['GET'])
def serve_map():
    print("sending file")
    return send_file('../visualizations/chloropeth_map.html')

@app.route('/weather', methods=['GET'])
def weather():
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
