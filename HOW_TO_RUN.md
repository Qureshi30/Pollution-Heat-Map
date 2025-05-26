# How to Run the Carbon Footprint Tracker

## Starting the Backend Server

### Option 1: Using PowerShell
1. Open PowerShell
2. Navigate to the backend directory:
   ```
   cd pollution-heatmap/backend
   ```
3. Run the PowerShell script:
   ```
   .\start_server.ps1
   ```

### Option 2: Using Command Prompt
1. Open Command Prompt
2. Navigate to the backend directory:
   ```
   cd pollution-heatmap/backend
   ```
3. Run the batch file:
   ```
   start_server.bat
   ```

### Option 3: Manual Start
1. Open a terminal
2. Navigate to the backend directory:
   ```
   cd pollution-heatmap/backend
   ```
3. Run the following command:
   ```
   python -m uvicorn carbon_calculator:app --host 0.0.0.0 --port 8002
   ```

## Accessing the Application

1. Open your web browser
2. Navigate to:
   ```
   file:///path/to/pollution-heatmap/frontend/home.html
   ```
   Replace `path/to` with the actual path to your project directory.

## Important Notes

- The application will work even if the backend server is not running, as it has a client-side fallback for calculations.
- For the best experience, make sure the backend server is running before using the Carbon Emission Calculator.
- If you encounter any issues with Tailwind CSS not loading, the application has a fallback mechanism to load it from an alternative CDN.

## Troubleshooting

- If you get a "Failed to fetch" error, make sure the backend server is running.
- If the backend server fails to start, check that you have all the required Python packages installed:
  ```
  pip install fastapi uvicorn pydantic reportlab
  ```
- If the map doesn't display correctly, try refreshing the page or selecting a different region. 