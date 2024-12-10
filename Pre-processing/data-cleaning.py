import pandas as pd

def preprocessing(startdate, enddate):
    # List of Massachusetts counties for which we will load and merge weather and AQI data
    massachusettsCounties = [
        "Barnstable",
        "Berkshire",
        "Bristol",
        "Dukes",
        "Essex",
        "Franklin",
        "Hampden",
        "Hampshire",
        "Middlesex",
        "Nantucket",
        "Norfolk",
        "Plymouth",
        "Suffolk",
        "Worcester"
    ]
    

    Mateo_df = pd.read_csv('../Dataset/raw_data/massachusetts_counties_weather_data.csv')

    raw_df = Mateo_df.copy()
   
    # Loop through each county and load its corresponding AQI data
    for county in massachusettsCounties:
        AQI_df = pd.read_csv(f'../Dataset/raw_data/AQI/{county}_air_pollution_history.csv')
        if 'aqi' in raw_df.columns:
            raw_df.update(AQI_df.set_index('dt'))
        else:
            raw_df = pd.merge(raw_df, AQI_df, left_on='date', right_on='dt', how='left')
    
    # Filter data based on the provided start date (if specified)
    if startdate:
        raw_df = raw_df[raw_df['date']>startdate]
    if enddate:
        raw_df = raw_df[raw_df['date']<enddate]
        
    filter_columns = ['date', 'county', 'latitude', 'longitude',
                    'weather_code', 
                    'daylight_duration', 'sunshine_duration', 
                    'temperature_2m_max', 'temperature_2m_min',
                    'uv_index_max',
                    'precipitation_probability_max', 
        'aqi']
    raw_df_filtered = raw_df[filter_columns]
    raw_df_filtered.head()
    
    raw_df_summary = raw_df_filtered.describe()
    raw_df_summary
    
    raw_df_filtered.isnull().sum()
    
    min_values = {
        'sunshine_duration': 0.0, 'uv_index_max': 0.1, 'precipitation_probability_max': 0.0, 'aqi': 1.0
        }

    # Loop through the columns and handle outliers and missing values
    for col, min_val in min_values.items():
        q1 = raw_df_summary.at['25%', col]
        q3 = raw_df_summary.at['75%', col]
        IQR = q3 - q1
        lower_bound = q1 - 1.5 * IQR
        upper_bound = q3 + 1.5 * IQR
        
        raw_df_filtered[col] = raw_df_filtered[col].clip(lower=lower_bound, upper=upper_bound).fillna(min_val)

    # Display the updated statistics after outlier handling and filling missing values
    raw_df_filtered.describe()
    
    raw_df_filtered.to_csv('../Dataset/cleaned_data/2022_2024_combined_weather_data.csv')

# Call the preprocessing function with the specified date range
preprocessing('2024-03-01', '2024-07-01')
    