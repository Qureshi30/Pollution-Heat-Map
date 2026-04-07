# Deployment Fix Summary

## Problem
The frontend was failing with 404 errors when trying to access API endpoints like `/api/cities` and `/api/pollutants` because:
- You had **two separate FastAPI applications**: `app.py` and `carbon_calculator.py`
- Render was only deploying `carbon_calculator.py`
- The emission visualizer pages needed endpoints from `app.py`

## Solution
**Merged both APIs into a single `app.py` file**

### Changes Made:

1. **Updated `backend/app.py`**:
   - Added all imports needed for carbon calculator (Pydantic, ReportLab, etc.)
   - Added `EmissionInput` and `EmissionResult` Pydantic models
   - Added all carbon calculator functions (renamed with `_calc` suffix to avoid conflicts)
   - Added two new endpoints:
     - `POST /api/calculate-emissions` - Calculate carbon footprint
     - `POST /api/generate-report` - Generate PDF report

2. **Updated `render.yaml`**:
   - Changed start command from `uvicorn carbon_calculator:app` to `uvicorn app:app`

3. **Updated Frontend API URLs** (already done):
   - `frontend/script.js` - Changed to https://pollution-heat-map.onrender.com
   - `frontend/script2.js` - Changed to https://pollution-heat-map.onrender.com
   - `frontend/calculator.js` - Already using correct URL
   - `frontend/config.js` - Updated to production URL

## All API Endpoints Now Available:

### Pollution Visualizer Endpoints (from original app.py):
- `GET /` - Welcome message
- `GET /api/cities` - Get list of cities
- `GET /api/pollutants` - Get list of pollutants
- `GET /api/pollution-data` - Get pollution data for charts
- `GET /api/models` - Get ML model info
- `GET /api/prediction-data` - Get prediction data
- `GET /api/pollution-map` - Get heatmap data
- `GET /api/folium-map` - Get Folium heatmap HTML
- `GET /api/location-info` - Get location-specific pollution info
- `GET /api/leaflet-marker` - Add marker to map

### Carbon Calculator Endpoints (merged from carbon_calculator.py):
- `POST /api/calculate-emissions` - Calculate carbon footprint
- `POST /api/generate-report` - Generate PDF report

## Next Steps to Deploy:

1. **Commit and push changes**:
   ```bash
   git add .
   git commit -m "Merge APIs and fix deployment configuration"
   git push origin main
   ```

2. **Update Render Backend Service**:
   - Go to Render Dashboard → Your backend service
   - Go to Settings → Build & Deploy
   - Change **Start Command** to: `cd backend && uvicorn app:app --host 0.0.0.0 --port $PORT`
   - Click "Save Changes"
   - Click "Manual Deploy" → "Deploy latest commit"

3. **Wait for deployment** (5-10 minutes)

4. **Test your site**:
   - Emission Visualizer should now load cities and pollutants
   - Carbon Calculator should work
   - All features should be functional

## Files Modified:
- ✅ `backend/app.py` - Merged carbon calculator code
- ✅ `render.yaml` - Updated start command
- ✅ `frontend/script.js` - Production API URL
- ✅ `frontend/script2.js` - Production API URL
- ✅ `frontend/config.js` - Production API URL
- ✅ `frontend/calculator.js` - Already had production URL

## Backend Structure (New):
```
backend/
├── app.py                    ← MAIN API (all endpoints)
├── carbon_calculator.py      ← Old file (can be kept as backup)
├── requirements.txt
├── build.sh
└── Data/                     ← Pollution data files
```

All done! Your app should work perfectly once you redeploy! 🚀
