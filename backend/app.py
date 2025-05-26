from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os
from typing import List, Optional
import glob
import re
import folium
from folium.plugins import HeatMap
from fastapi.responses import HTMLResponse

app = FastAPI(title="Pollution Heatmap API")

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, replace with specific frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Base directory for data files

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Data")
print(f"Data directory: {DATA_DIR}")
print(f"Data directory exists: {os.path.exists(DATA_DIR)}")
if os.path.exists(DATA_DIR):
    print(f"Data directory contents: {os.listdir(DATA_DIR)}")

# Map of standardized pollutant names to possible column name variations
POLLUTANT_MAP = {
    'PM2.5': ['PM2.5', 'PM2.5 (µg/m³)'],
    'PM10': ['PM10', 'PM10 (µg/m³)'],
    'NO2': ['NO2', 'NO2 (µg/m³)'],
    'SO2': ['SO2', 'SO2 (µg/m³)'],
    'CO': ['CO', 'CO (mg/m³)'],
    'Ozone': ['Ozone', 'Ozone (µg/m³)'],
    'NO': ['NO', 'NO (µg/m³)'],
    'NOx': ['NOx', 'NOx (ppb)'],
    'NH3': ['NH3', 'NH3 (µg/m³)'],
    'Benzene': ['Benzene', 'Benzene (µg/m³)'],
    'AT': ['AT',"AT (Â°C)"],
}

# Standard pollutants to display
STANDARD_POLLUTANTS = ['PM2.5', 'PM10', 'NO2', 'SO2', 'CO', 'Ozone','AT']
# Default city coordinates for generating synthetic location data
CITY_COORDS = {
    'Byculla': (18.9794, 72.8368),
    'Colaba': (18.9100, 72.8050),
    'CSMT Airport': (18.9400, 72.8350),
    'Mazgaon': (18.9600, 72.8450),
    'Sion': (19.0390, 72.8619),
    'Worli': (18.9925, 72.8175)
}

@app.get("/")
async def root():
    return {"message": "Welcome to Pollution Heatmap API"}

@app.get("/api/cities")
async def get_cities():
    """Get list of all available cities"""
    cities = [city for city in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, city))]
    return {"cities": cities}

@app.get("/api/pollutants")
async def get_pollutants():
    """Get list of all available pollutants"""
    # Return standard pollutants instead of reading from files
    # This ensures consistent pollutant options regardless of file format
    return {"pollutants": STANDARD_POLLUTANTS}

def find_pollutant_column(df, pollutant):
    """Find the actual column name for a pollutant in the dataframe"""
    if pollutant in POLLUTANT_MAP:
        for possible_name in POLLUTANT_MAP[pollutant]:
            if possible_name in df.columns:
                return possible_name
    return None

def extract_date_column(df):
    """Find and extract the date column from the dataframe"""
    # Check for standard date column names
    for col_name in ['Date', 'Timestamp']:
        if col_name in df.columns:
            # If it's a Timestamp column, we'll clean it to get just the date part
            if col_name == 'Timestamp':
                try:
                    # Handle potential NaN or float values by converting to string first
                    df['Date'] = df[col_name].astype(str).apply(
                        lambda x: x.split(' ')[0] if ' ' in x and x != 'nan' and x != 'None' else x
                    )
                    return 'Date'
                except Exception as e:
                    print(f"Error processing Timestamp column: {str(e)}")
                    # If we can't process the timestamp, create a synthetic date column
                    df['Date'] = pd.date_range(start='2023-01-01', periods=len(df)).astype(str)
                    return 'Date'
            return col_name
    
    # If no standard date column is found, look for columns that might contain date info
    for col in df.columns:
        if 'date' in col.lower() or 'time' in col.lower():
            # Extract just the date part if it's a timestamp
            try:
                if df[col].dtype == object and any(' ' in str(x) for x in df[col].dropna().head()):
                    df['Date'] = df[col].astype(str).apply(
                        lambda x: x.split(' ')[0] if ' ' in x and x != 'nan' and x != 'None' else x
                    )
                    return 'Date'
                return col
            except Exception as e:
                print(f"Error processing date column {col}: {str(e)}")
                # Continue to next potential date column
    
    # If no date column is found, create a synthetic one
    print("No date column found, creating synthetic dates")
    df['Date'] = pd.date_range(start='2023-01-01', periods=len(df)).astype(str)
    return 'Date'

@app.get("/api/pollution-data")
async def get_pollution_data(
    city: str = Query(..., description="City name"),
    pollutant: str = Query(..., description="Pollutant name")
):
    """
    Get pollution data for a specific city and pollutant across all available years
    """
    city_dir = os.path.join(DATA_DIR, city)
    
    # Check if city exists
    if not os.path.exists(city_dir):
        raise HTTPException(status_code=404, detail=f"City '{city}' not found")
    
    # Get all CSV files for the city
    csv_files = glob.glob(os.path.join(city_dir, "*.csv"))
    if not csv_files:
        raise HTTPException(status_code=404, detail=f"No data files found for city '{city}'")
    
    # Combined data across all years
    all_data = []
    
    for csv_file in csv_files:
        try:
            # Extract year from filename
            year = os.path.basename(csv_file).split('.')[0]
            
            # Read the CSV file
            df = pd.read_csv(csv_file)
            
            # Find the actual column name for the requested pollutant
            pollutant_col = find_pollutant_column(df, pollutant)
            if not pollutant_col:
                print(f"Pollutant '{pollutant}' not found in {csv_file}")
                continue
                
            # Extract the date column
            date_col = extract_date_column(df)
            if not date_col:
                print(f"Date column not found in {csv_file}")
                continue
            
            # Generate synthetic latitude/longitude based on city
            # Default coordinates for each city (center point)
            base_lat, base_lon = CITY_COORDS.get(city, (19.0, 72.8))  # Default to Mumbai center
            
            # Add small random variation for visualization
            from random import uniform
            
            # Format data for response
            file_data = []
            for idx, row in df.iterrows():
                try:
                    # Check if pollutant value exists and is not NaN
                    if pollutant_col in row and pd.notna(row[pollutant_col]):
                        # Generate random coordinates around the city center
                        lat = base_lat + uniform(-0.005, 0.005)
                        lon = base_lon + uniform(-0.005, 0.005)
                        
                        # Ensure date is a string
                        date_value = str(row[date_col]) if pd.notna(row[date_col]) else f"{year}-01-01"
                        
                        # Convert pollutant value to float, handling potential errors
                        try:
                            # First convert to string and then to float to handle various data types
                            value_str = str(row[pollutant_col]).strip()
                            # Skip empty strings, nan, or none values
                            if value_str == '' or value_str.lower() == 'nan' or value_str.lower() == 'none':
                                continue
                            pollutant_value = float(value_str)
                        except (ValueError, TypeError):
                            print(f"Error converting pollutant value: {row[pollutant_col]}")
                            continue
                        
                        # Create data point
                        data_point = {
                            "date": date_value,
                            "year": year,
                            "latitude": float(lat),
                            "longitude": float(lon),
                            "value": pollutant_value,
                            "city": city  # Use the requested city name
                        }
                        file_data.append(data_point)
                except Exception as row_error:
                    print(f"Error processing row {idx}: {str(row_error)}")
                    continue
            
            all_data.extend(file_data)
        
        except Exception as e:
            print(f"Error processing {csv_file}: {str(e)}")
            # Continue to next file rather than failing completely
    
    if not all_data:
        raise HTTPException(
            status_code=404, 
            detail=f"No data found for pollutant '{pollutant}' in city '{city}'"
        )
    
    return {"data": all_data}

# Base directory for FutureData folder
FUTURE_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "FutureData") 
print(f"FutureData directory: {FUTURE_DATA_DIR}")
print(f"FutureData directory exists: {os.path.exists(FUTURE_DATA_DIR)}")

# List of prediction model folders inside the FutureData directory
MODEL_FOLDERS = ["LSTM", "RFR", "LGBM"]

@app.get("/api/models")
async def get_models():
    """Get list of all available prediction models"""
    # Get the available model folders inside FutureData
    models = [model for model in os.listdir(FUTURE_DATA_DIR) if os.path.isdir(os.path.join(FUTURE_DATA_DIR, model))]
    return {"models": models}


@app.get("/api/prediction-data")
async def get_prediction_data(
    model: str = Query(..., description="Prediction model name (LSTM, LGBM, RFR)"),
    city: str = Query(..., description="City name (e.g., Colaba)"),
    emission_type: str = Query(..., description="Type of emission (column name in CSV)"),
    year: str = Query(..., description="Year (e.g., 2025)"),
):
    """
    Get prediction data for a specific model, emission type, and year.
    """
    model_dir = os.path.join(FUTURE_DATA_DIR, model, city)
    
    # Check if the model directory exists
    if not os.path.exists(model_dir):
        raise HTTPException(status_code=404, detail=f"Prediction model '{model}' not found.")
    
    city_dir = os.path.join(model_dir)
    
    # Check if city directory exists
    if not os.path.exists(city_dir):
        raise HTTPException(status_code=404, detail=f"City '{city}' not found under model '{model}'")
    
    # Match pattern for the model's predicted data
    csv_pattern = os.path.join(city_dir, f"{model}_Predicted_{year}.csv")
    csv_files = glob.glob(csv_pattern)
    
    # If no CSV file found, return 404
    if not csv_files:
        raise HTTPException(
            status_code=404, 
            detail=f"No data file found for year {year} in city '{city}' using model '{model}'"
        )
    
    all_data = []
    
    # Loop through all CSV files
    for csv_file in csv_files:
        try:
            # Extract the year from the file name
            filename = os.path.basename(csv_file)
            extracted_year = filename.split("_")[-1].replace(".csv", "")
            
            # Read CSV file
            df = pd.read_csv(csv_file)
            print("Columns in CSV:", df.columns)

            # Check if the emission type exists in the columns
            if emission_type not in df.columns:
                print(f"Emission type '{emission_type}' not found in {csv_file}")
                continue
            
            # Extract the date column
            date_col = extract_date_column(df)
            if not date_col:
                print(f"Date column not found in {csv_file}")
                continue
            
            # Default city coordinates (can be extended or overridden as needed)
            base_lat, base_lon = CITY_COORDS.get(city, (19.0, 72.8))  # Default to Mumbai center
            
            from random import uniform
            file_data = []
            
            # Process rows in the dataframe
            for idx, row in df.iterrows():
                try:
                    # Check if the emission type value exists
                    if pd.notna(row[emission_type]):
                        lat = base_lat + uniform(-0.005, 0.005)
                        lon = base_lon + uniform(-0.005, 0.005)
                        
                        # Extract the date value
                        date_value = str(row[date_col]) if pd.notna(row[date_col]) else f"{year}-01-01"
                        
                        try:
                            # Convert emission type to a float, handle errors
                            value_str = str(row[emission_type]).strip()
                            if value_str == '' or value_str.lower() in ['nan', 'none']:
                                continue
                            emission_value = float(value_str)
                        except (ValueError, TypeError):
                            print(f"Error converting emission value: {row[emission_type]}")
                            continue
                        
                        # Create the data point
                        data_point = {
                            "date": date_value,
                            "year": extracted_year,
                            "latitude": float(lat),
                            "longitude": float(lon),
                            "prediction_value": emission_value,
                            
                        }
                        file_data.append(data_point)
                except Exception as row_error:
                    print(f"Error processing row {idx}: {str(row_error)}")
                    continue
            
            all_data.extend(file_data)
        
        except Exception as e:
            print(f"Error processing {csv_file}: {str(e)}")
            continue
    
    # If no data was found, return an error
    if not all_data:
        raise HTTPException(
            status_code=404,
            detail=f"No data found for emission type '{emission_type}' in model '{model}'"
        )
    
    return {"data": all_data}

@app.get("/api/pollution-map")
async def get_pollution_map(
    city: str = Query(..., description="City name"),
    pollutant: str = Query(..., description="Pollutant name")
):
    """
    Get pollution map for a specific city and pollutant
    """
    city_dir = os.path.join(DATA_DIR, city)
    
    # Check if city exists
    if not os.path.exists(city_dir):
        raise HTTPException(status_code=404, detail=f"City '{city}' not found")
    
    # Get all CSV files for the city
    csv_files = glob.glob(os.path.join(city_dir, "*.csv"))
    if not csv_files:
        raise HTTPException(status_code=404, detail=f"No data files found for city '{city}'")
    
    # Combined data across all years
    all_data = []
    
    for csv_file in csv_files:
        try:
            # Extract year from filename
            year = os.path.basename(csv_file).split('.')[0]
            
            # Read the CSV file
            df = pd.read_csv(csv_file)
            
            # Find the actual column name for the requested pollutant
            pollutant_col = find_pollutant_column(df, pollutant)
            if not pollutant_col:
                print(f"Pollutant '{pollutant}' not found in {csv_file}")
                continue
                
            # Extract the date column
            date_col = extract_date_column(df)
            if not date_col:
                print(f"Date column not found in {csv_file}")
                continue
            
            # Extract or generate latitude/longitude if available
            lat_col = 'Latitude' if 'Latitude' in df.columns else None
            lon_col = 'Longitude' if 'Longitude' in df.columns else None
            
            # If location data is missing, generate fake coordinates based on city
            if not lat_col or not lon_col:
                # Default coordinates for each city (center point)
                city_coords = {
                    'Byculla': (18.9794, 72.8368),
                    'Colaba': (18.9100, 72.8050),
                    'CSMT Airport': (18.9400, 72.8350),
                    'Mazgaon': (18.9600, 72.8450),
                    'Sion': (19.0390, 72.8619),
                    'Worli': (18.9925, 72.8175)
                }
                
                # Add small random variation for visualization
                from random import uniform
                base_lat, base_lon = city_coords.get(city, (19.0, 72.8))  # Default to Mumbai center
                
                # Create synthetic latitude and longitude columns
                df['Latitude'] = [base_lat + uniform(-0.002, 0.002) for _ in range(len(df))]
                df['Longitude'] = [base_lon + uniform(-0.002, 0.002) for _ in range(len(df))]
                
                lat_col = 'Latitude'
                lon_col = 'Longitude'
            
            # Format data for response
            file_data = []
            for _, row in df.iterrows():
                if pd.notna(row[pollutant_col]):  # Check if pollutant value is not NaN
                    # Create data point
                    data_point = {
                        "date": row[date_col],
                        "year": year,
                        "latitude": float(row[lat_col]),
                        "longitude": float(row[lon_col]),
                        "value": float(row[pollutant_col]),
                        "city": city  # Use the requested city name
                    }
                    file_data.append(data_point)
            
            all_data.extend(file_data)
        
        except Exception as e:
            print(f"Error processing {csv_file}: {str(e)}")
            # Continue to next file rather than failing completely
    
    if not all_data:
        raise HTTPException(
            status_code=404, 
            detail=f"No data found for pollutant '{pollutant}' in city '{city}'"
        )
    
    # Create a Folium map
    m = folium.Map(location=[19.0760, 72.8777], zoom_start=12)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Add title and legend
    title_html = f'''
        <div style="position: fixed; 
                    top: 10px; 
                    left: 50px; 
                    width: 300px; 
                    height: 90px; 
                    z-index:9999; 
                    font-size:14px;
                    background-color: white;
                    padding: 10px;
                    border-radius: 5px;
                    box-shadow: 0 0 15px rgba(0,0,0,0.2);">
            <h4>{city} - {pollutant} Levels</h4>
            <div style="display: flex; justify-content: space-between; margin-top: 10px;">
                <span style="color: blue;">Low</span>
                <span style="color: lime;">↓</span>
                <span style="color: yellow;">Medium</span>
                <span style="color: orange;">↓</span>
                <span style="color: red;">High</span>
            </div>
        </div>
    '''
    m.get_root().html.add_child(folium.Element(title_html))
    
    # Save the map to a temporary file
    map_html = m._repr_html_()
    return map_html

@app.get("/api/folium-map", response_class=HTMLResponse)
async def get_folium_map(
    city: str = Query(..., description="City name"),
    pollutant: str = Query(..., description="Pollutant name"),
    show_markers: bool = Query(True, description="Whether to show location markers")
):
    """
    Generate a Leaflet map for the specified city and pollutant with a single pointer
    """
    try:
        print(f"Generating map for city: {city}, pollutant: {pollutant}")
        
        # Get pollution data directly from CSV files instead of using the API endpoint
        city_dir = os.path.join(DATA_DIR, city)
        if not os.path.exists(city_dir):
            return f"""
            <html>
            <body style="font-family: Arial, sans-serif; padding: 20px; text-align: center;">
                <h3 style="color: #d9534f;">City Not Found</h3>
                <p>The city '{city}' was not found in the data directory.</p>
            </body>
            </html>
            """
        
        # Get all CSV files for the city
        csv_files = glob.glob(os.path.join(city_dir, "*.csv"))
        if not csv_files:
            return f"""
            <html>
            <body style="font-family: Arial, sans-serif; padding: 20px; text-align: center;">
                <h3 style="color: #d9534f;">No Data Files</h3>
                <p>No data files found for city '{city}'.</p>
            </body>
            </html>
            """
        
        # Process data directly
        heat_data = []
        # Get exact coordinates for the city from the CITY_COORDS dictionary
        base_lat, base_lon = CITY_COORDS.get(city, (19.0, 72.8))  # Default to Mumbai center
        
        # Create a grid of locations across the area
        from random import uniform, gauss, seed
        
        # Set a seed for reproducibility but make it different for each city/pollutant
        seed_value = hash(f"{city}_{pollutant}") % 10000
        seed(seed_value)
        
        # Define the area bounds (approximately 2km in each direction)
        lat_range = 0.02  # About 2km north-south
        lon_range = 0.02  # About 2km east-west
        
        # Create 20-30 scattered data points across the area
        num_points = 25 + int(uniform(0, 10))
        
        # Process each CSV file to get average pollutant values
        pollutant_values = []
        
        for csv_file in csv_files:
            try:
                # Read the CSV file
                df = pd.read_csv(csv_file)
                
                # Find the pollutant column
                pollutant_col = find_pollutant_column(df, pollutant)
                if not pollutant_col:
                    continue
                
                # Get valid pollutant values
                valid_values = df[pollutant_col].dropna().tolist()
                
                # Convert values to float, handling potential errors
                for val in valid_values:
                    try:
                        value_str = str(val).strip()
                        if value_str == '' or value_str.lower() == 'nan' or value_str.lower() == 'none':
                            continue
                        pollutant_values.append(float(value_str))
                    except (ValueError, TypeError) as e:
                        print(f"Error converting pollutant value: {val}, {str(e)}")
                
            except Exception as file_error:
                print(f"Error processing file {csv_file}: {str(file_error)}")
        
        if not pollutant_values:
            return f"""
            <html>
            <body style="font-family: Arial, sans-serif; padding: 20px; text-align: center;">
                <h3 style="color: #d9534f;">No Data Found</h3>
                <p>No valid pollution data found for {pollutant} in {city}.</p>
            </body>
            </html>
            """
        
        # Calculate statistics for the pollutant values
        min_val = min(pollutant_values)
        max_val = max(pollutant_values)
        avg_val = sum(pollutant_values) / len(pollutant_values)
        
        # Create data points for heatmap
        for i in range(num_points):
            # Create a scattered point with Gaussian distribution around the center
            lat = base_lat + gauss(0, lat_range/3)
            lon = base_lon + gauss(0, lon_range/3)
            
            # Assign a value based on distance from center and random variation
            distance_from_center = ((lat - base_lat)**2 + (lon - base_lon)**2)**0.5
            normalized_distance = min(1.0, distance_from_center / (lat_range/2))
            
            # Value decreases with distance from center, with some randomness
            value_factor = 1.0 - (normalized_distance * 0.7) + uniform(-0.2, 0.2)
            value_factor = max(0.1, min(1.0, value_factor))  # Clamp between 0.1 and 1.0
            
            # Calculate the actual value
            value = min_val + value_factor * (max_val - min_val)
            
            # Add to heat data
            heat_data.append([lat, lon, value])
        
        # Add more variation by creating smaller clusters
        num_clusters = 3 + int(uniform(0, 4))
        for _ in range(num_clusters):
            # Create a cluster center
            cluster_lat = base_lat + uniform(-lat_range/2, lat_range/2)
            cluster_lon = base_lon + uniform(-lon_range/2, lon_range/2)
            
            # Determine cluster intensity (higher or lower than average)
            cluster_intensity = uniform(0.7, 1.3)
            
            # Add 5-10 points around this cluster
            cluster_points = 5 + int(uniform(0, 6))
            for _ in range(cluster_points):
                point_lat = cluster_lat + gauss(0, lat_range/10)
                point_lon = cluster_lon + gauss(0, lon_range/10)
                
                # Calculate value with some randomness
                value = avg_val * cluster_intensity * uniform(0.8, 1.2)
                value = max(min_val, min(max_val, value))  # Clamp to min/max range
                
                heat_data.append([point_lat, point_lon, value])
        
        # Create a Leaflet map HTML
        leaflet_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>{city} - {pollutant} Heatmap</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin=""/>
            <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>
            <script src="https://unpkg.com/leaflet.heat@0.2.0/dist/leaflet-heat.js"></script>
            <style>
                html, body, #map {{
                    height: 100%;
                    width: 100%;
                    margin: 0;
                    padding: 0;
                }}
                .info {{
                    padding: 6px 8px;
                    font: 14px/16px Arial, Helvetica, sans-serif;
                    background: white;
                    background: rgba(255,255,255,0.8);
                    box-shadow: 0 0 15px rgba(0,0,0,0.2);
                    border-radius: 5px;
                }}
                .info h4 {{
                    margin: 0 0 5px;
                    color: #777;
                }}
                .legend {{
                    line-height: 18px;
                    color: #555;
                }}
                .legend i {{
                    width: 18px;
                    height: 18px;
                    float: left;
                    margin-right: 8px;
                    opacity: 0.7;
                }}
            </style>
        </head>
        <body>
            <div id="map"></div>
            <script>
                // Initialize the map
                var map = L.map('map').setView([{base_lat}, {base_lon}], 14);
                
                // Add the base tile layer
                L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                }}).addTo(map);
                
                // Heat map data
                var heatData = {heat_data};
                
                // Add the heat map layer
                var heat = L.heatLayer(heatData, {{
                    radius: 15,
                    blur: 20,
                    maxZoom: 17,
                    gradient: {{
                        0.0: 'blue',
                        0.25: 'lime',
                        0.5: 'yellow',
                        0.75: 'orange',
                        1.0: 'red'
                    }}
                }}).addTo(map);
                
                // Add ONLY ONE MARKER for the city's exact location
                // Create a marker for the city center only
                var cityMarker = L.marker([{base_lat}, {base_lon}]);
                cityMarker.bindPopup('<b>{city}</b><br>Location: {base_lat}, {base_lon}<br>Average {pollutant}: ' + 
                                   {avg_val}.toFixed(2));
                cityMarker.addTo(map);
                
                // Create a pulsing icon effect for better visibility
                function pulseMarker() {{
                    cityMarker._icon.style.transform += ' scale(1.1)';
                    setTimeout(function() {{
                        if (cityMarker._icon) {{
                            cityMarker._icon.style.transform = cityMarker._icon.style.transform.replace(' scale(1.1)', '');
                        }}
                    }}, 500);
                }}
                
                // Pulse the marker initially
                setTimeout(pulseMarker, 1000);
                
                
                // Add click handler to show coordinates when clicking on the map
                map.on('click', function(e) {{
                    L.popup()
                        .setLatLng(e.latlng)
                        .setContent("Clicked location:<br>Lat: " + e.latlng.lat.toFixed(6) + 
                                  "<br>Lng: " + e.latlng.lng.toFixed(6))
                        .openOn(map);
                        
                    // Send click coordinates to parent window
                    try {{
                        window.parent.postMessage({{
                            type: 'map-click',
                            lat: e.latlng.lat,
                            lng: e.latlng.lng
                        }}, '*');
                    }} catch(e) {{
                        console.log('Error sending message to parent:', e);
                    }}
                }});
                
                // Add a title control
                var info = L.control();
                
                info.onAdd = function(map) {{
                    this._div = L.DomUtil.create('div', 'info');
                    this.update();
                    return this._div;
                }};
                
                info.update = function() {{
                    this._div.innerHTML = '<h4>{city} - {pollutant} Levels</h4>';
                }};
                
                info.addTo(map);
                
                // Add a legend
                var legend = L.control({{position: 'bottomright'}});
                
                legend.onAdd = function(map) {{
                    var div = L.DomUtil.create('div', 'info legend');
                    var grades = ['Very Low', 'Low', 'Medium', 'High', 'Very High'];
                    var colors = ['blue', 'lime', 'yellow', 'orange', 'red'];
                    
                    div.innerHTML = '<h4>Pollution Levels</h4>';
                    
                    // Loop through our density intervals and generate a label with a colored square for each interval
                    for (var i = 0; i < grades.length; i++) {{
                        div.innerHTML +=
                            '<i style="background:' + colors[i] + '"></i> ' +
                            grades[i] + '<br>';
                    }}
                    
                    return div;
                }};
                
                legend.addTo(map);
            </script>
        </body>
        </html>
        """
        
        return leaflet_html
        
    except Exception as e:
        print(f"Error generating map: {str(e)}")
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px; text-align: center;">
            <h3 style="color: #d9534f;">Error Generating Map</h3>
            <p>An error occurred while generating the map for {city} - {pollutant}.</p>
            <p>Error details: {str(e)}</p>
        </body>
        </html>
        """

# Add this new endpoint

@app.get("/api/location-info")
async def get_location_info(
    lat: float = Query(..., description="Latitude of the location"),
    lon: float = Query(..., description="Longitude of the location"),
    city: str = Query(None, description="City name to filter data"),
    pollutant: str = Query(None, description="Pollutant name to filter data"),
    radius: float = Query(0.002, description="Search radius in degrees")
):
    """
    Get pollution information for a specific location
    """
    try:
        # If city and pollutant are provided, get data for that combination
        if city and pollutant:
            city_dir = os.path.join(DATA_DIR, city)
            
            if not os.path.exists(city_dir):
                return {"error": f"City '{city}' not found"}
            
            # Get all CSV files for the city
            csv_files = glob.glob(os.path.join(city_dir, "*.csv"))
            if not csv_files:
                return {"error": f"No data files found for city '{city}'"}
            
            # Process data to find nearby measurements
            nearby_data = []
            
            for csv_file in csv_files:
                try:
                    # Extract year from filename
                    year = os.path.basename(csv_file).split('.')[0]
                    
                    # Read the CSV file
                    df = pd.read_csv(csv_file)
                    
                    # Find the pollutant column
                    pollutant_col = find_pollutant_column(df, pollutant)
                    if not pollutant_col:
                        continue
                    
                    # Check if location data exists
                    has_location = 'Latitude' in df.columns and 'Longitude' in df.columns
                    
                    # If we have location data, find measurements near the requested coordinates
                    if has_location:
                        for _, row in df.iterrows():
                            row_lat = row['Latitude']
                            row_lon = row['Longitude']
                            
                            # Calculate distance (simple Euclidean, approximate)
                            dist = ((row_lat - lat)**2 + (row_lon - lon)**2)**0.5
                            
                            if dist <= radius and pd.notna(row[pollutant_col]):
                                nearby_data.append({
                                    "year": year,
                                    "distance_km": dist * 111,  # Rough conversion to km
                                    "value": float(row[pollutant_col]),
                                    "latitude": row_lat,
                                    "longitude": row_lon,
                                    "date": row.get('Date', f"{year}-01-01")
                                })
                
                except Exception as e:
                    print(f"Error processing file {csv_file}: {str(e)}")
            
            # Sort by distance
            nearby_data.sort(key=lambda x: x["distance_km"])
            
            return {
                "location": {"latitude": lat, "longitude": lon, "city": city},
                "pollutant": pollutant,
                "nearby_measurements": nearby_data[:10],  # Return closest 10 measurements
                "average_value": sum(d["value"] for d in nearby_data) / len(nearby_data) if nearby_data else None
            }
        
        # Otherwise, return info about the coordinates
        else:
            return {
                "location": {"latitude": lat, "longitude": lon},
                "message": "Provide city and pollutant parameters to get pollution data for this location"
            }
    
    except Exception as e:
        return {"error": f"Error retrieving location info: {str(e)}"}

@app.get("/api/leaflet-marker", response_class=HTMLResponse)
async def add_leaflet_marker(
    lat: float = Query(..., description="Latitude of the location"),
    lon: float = Query(..., description="Longitude of the location"),
    label: str = Query(None, description="Optional label for the marker")
):
    """
    Add a marker to a Leaflet map at the specified coordinates
    """
    marker_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Location Marker</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin=""/>
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>
        <style>
            html, body, #map {{
                height: 100%;
                width: 100%;
                margin: 0;
                padding: 0;
            }}
        </style>
    </head>
    <body>
        <div id="map"></div>
        <script>
            // Initialize the map
            var map = L.map('map').setView([{lat}, {lon}], 15);
            
            // Add the base tile layer
            L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            }}).addTo(map);
            
            // Add a marker at the specified location
            var marker = L.marker([{lat}, {lon}]).addTo(map);
            
            // Add a popup with coordinates and optional label
            marker.bindPopup(`<b>{label or "Location"}</b><br>Latitude: {lat}<br>Longitude: {lon}`).openPopup();
        </script>
    </body>
    </html>
    """
    
    return marker_html

import uvicorn

if __name__ == "__main__":
    # Run with: uvicorn app:app --reload
    uvicorn.run(app, host="0.0.0.0", port=8001)