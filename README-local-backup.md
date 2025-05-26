# Pollution Heatmap Dashboard

A web application to visualize pollution data across different cities and analyze trends over multiple years.

## Features

- **Interactive UI:** Select different cities and pollutants to visualize and compare pollution trends
- **Folium Maps Integration:** View pollution intensity as a heatmap overlay on interactive maps
- **Multi-Year Trend Analysis:** Analyze how pollution levels have changed over different years using interactive charts
- **Data Summary:** View key statistics like average, maximum, and minimum pollution levels
- **Detailed Analysis:** Get health implications and trend analysis based on the selected data

## Project Structure

```
/pollution-heatmap
│── /Data
│   ├── /Byculla
│   │   ├── 2023.csv
│   │   ├── 2024.csv
│   ├── /Colaba
│   ├── /CSMT Airport
│   ├── /Mazgaon
│   ├── /Sion
│   ├── /Worli
│── /backend
│   ├── app.py (FastAPI API to fetch & aggregate CSV data)
│   ├── requirements.txt
│── /frontend
│   ├── index.html (Dropdowns & Display UI)
│   ├── script.js (Fetch & Display Data)
│── README.md
```

## Data Format

Each CSV file contains pollution data with the following structure:
- Date (YYYY-MM-DD)
- Latitude & Longitude
- Pollutant Levels (CO2, PM2.5, PM10, NO2, SO2, etc.)
- City Name

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
   ```
   cd pollution-heatmap/backend
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv env
   ```

3. Activate the virtual environment:
   - Windows: `env\Scripts\activate`
   - macOS/Linux: `source env/bin/activate`

4. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

5. Run the FastAPI server:
   ```
   uvicorn app:app --reload
   ```

The API server will be running at http://localhost:8000

### Frontend Setup

1. Update the Google Maps API key in `frontend/index.html` with your API key:
   ```html
   <script src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&libraries=visualization" defer></script>
   ```

2. Open `frontend/index.html` in a web browser, or serve it using a simple HTTP server:
   ```
   # Using Python
   cd pollution-heatmap
   python -m http.server 8080
   ```

   Then open http://localhost:8080/frontend in your browser.

## API Endpoints

- `/api/cities` - Get a list of all available cities
- `/api/pollutants` - Get a list of all available pollutants
- `/api/pollution-data?city=Byculla&pollutant=CO2` - Get pollution data for a specific city and pollutant across all available years

## Technologies Used

- **Frontend:** HTML, JavaScript, Tailwind CSS, Chart.js
- **Backend:** Python, FastAPI, Pandas, Folium
- **Data Storage:** CSV files

## Note for Production

For a production deployment:
1. Set up proper CORS settings in the backend
2. Use a production-ready server like Gunicorn or Uvicorn with workers
3. Consider moving data to a proper database for better performance
4. Set up proper error handling and logging

# Carbon Footprint Tracker

A comprehensive web application for visualizing and calculating carbon emissions.

## Features

- **Carbon Footprint Visualizer**: Interactive maps and charts showing carbon emission trends across different regions and time periods
- **Carbon Emission Calculator**: Personalized carbon footprint calculator with detailed breakdown and recommendations
- **PDF Report Generation**: Download detailed reports of your carbon footprint with personalized recommendations

## Project Structure

```
/pollution-heatmap
│── /Data
│   ├── /Byculla
│   │   ├── 2023.csv
│   │   ├── 2024.csv
│   ├── /Colaba
│   ├── /CSMT Airport
│   ├── /Mazgaon
│   ├── /Sion
│   ├── /Worli
│── /backend
│   ├── app.py (FastAPI API for pollution data visualization)
│   ├── carbon_calculator.py (FastAPI API for carbon footprint calculation)
│   ├── requirements.txt
│── /frontend
│   ├── home.html (Main landing page)
│   ├── carbon-footprint-visualizer.html (Visualization dashboard)
│   ├── carbon-emission-calculator.html (Carbon calculator form)
│   ├── script.js (Visualization JavaScript)
│   ├── calculator.js (Calculator JavaScript)
│── README.md
```

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
   ```
   cd pollution-heatmap/backend
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv env
   ```

3. Activate the virtual environment:
   - Windows: `env\Scripts\activate`
   - macOS/Linux: `source env/bin/activate`

4. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

5. Run the FastAPI servers:
   ```
   # For pollution visualization API
   python app.py
   
   # For carbon calculator API (in a separate terminal)
   python carbon_calculator.py
   ```

The visualization API will be running at http://localhost:8001 and the calculator API at http://localhost:8002

### Frontend Setup

1. Open the frontend files in a web browser, or serve them using a simple HTTP server:
   ```
   # Using Python
   cd pollution-heatmap
   python -m http.server 8080
   ```

2. Access the application at:
   - Home page: http://localhost:8080/frontend/home.html
   - Visualizer: http://localhost:8080/frontend/carbon-footprint-visualizer.html
   - Calculator: http://localhost:8080/frontend/carbon-emission-calculator.html

## Technologies Used

- **Frontend:** HTML, JavaScript, Tailwind CSS, Chart.js
- **Backend:** Python, FastAPI, Pandas, Folium, ReportLab
- **Data Storage:** CSV files

## Features in Detail

### Carbon Footprint Visualizer
- Interactive maps showing carbon emission intensity across regions
- Time-series charts for analyzing emission trends over years
- Detailed data summaries and environmental impact analysis

### Carbon Emission Calculator
- Comprehensive input form covering transportation, home energy, and lifestyle
- Detailed breakdown of emissions by category
- Personalized recommendations for reducing carbon footprint
- PDF report generation with comparison to national averages

## Note for Production

For a production deployment:
1. Set up proper CORS settings in the backend
2. Use a production-ready server like Gunicorn or Uvicorn with workers
3. Consider moving data to a proper database for better performance
4. Set up proper error handling and logging 