# Pollution Heatmap - Deployment Guide

## Project Structure
- **Backend**: FastAPI (Python) - REST API for carbon emission calculations
- **Frontend**: Static HTML/CSS/JS - User interface

## Deployment on Render

### Prerequisites
1. GitHub account
2. Render account (sign up at https://render.com)
3. Git installed on your computer

### Step-by-Step Deployment

#### Step 1: Push to GitHub
```bash
# If not already a git repository
git init
git add .
git commit -m "Initial commit for Render deployment"

# Create a new repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

#### Step 2: Deploy Backend on Render

1. Go to https://dashboard.render.com
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure the service:
   - **Name**: `pollution-heatmap-api` (or your preferred name)
   - **Region**: Choose closest to your users
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn carbon_calculator:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: Free (or paid for better performance)

5. Add Environment Variables (Optional):
   - Click "Advanced" → "Add Environment Variable"
   - `PYTHON_VERSION`: `3.11.0`

6. Click "Create Web Service"
7. Wait for deployment (5-10 minutes)
8. **Copy your backend URL** (e.g., `https://pollution-heatmap-api.onrender.com`)

#### Step 3: Update Frontend to Use Deployed Backend

In your frontend JavaScript files, update the API endpoint:
```javascript
// Change from:
const API_URL = 'http://localhost:8002';

// To your Render backend URL:
const API_URL = 'https://pollution-heatmap-api.onrender.com';
```

#### Step 4: Deploy Frontend on Render

1. Go to https://dashboard.render.com
2. Click "New +" → "Static Site"
3. Connect the same GitHub repository
4. Configure:
   - **Name**: `pollution-heatmap-frontend`
   - **Branch**: `main`
   - **Root Directory**: `frontend`
   - **Build Command**: (leave empty)
   - **Publish Directory**: `.`

5. Click "Create Static Site"
6. Wait for deployment
7. **Your app is live!** Get the URL (e.g., `https://pollution-heatmap-frontend.onrender.com`)

### Important Notes

- **Free Tier Limitation**: Backend spins down after 15 minutes of inactivity. First request after inactivity may take 30-60 seconds.
- **CORS**: Already configured in your backend (`allow_origins=["*"]`)
- **Updates**: Push to GitHub → Render auto-deploys

### Alternative: Deploy Both with render.yaml

Use the `render.yaml` file in the root directory:
1. Push to GitHub
2. Go to Render Dashboard → "New" → "Blueprint"
3. Connect repository
4. Render will auto-detect `render.yaml` and deploy both services

## Troubleshooting

### Backend won't start
- Check build logs in Render dashboard
- Verify `requirements.txt` has all dependencies
- Ensure Python version is compatible

### Frontend can't connect to backend
- Check CORS settings in `carbon_calculator.py`
- Verify API_URL in frontend JavaScript
- Check browser console for errors

### Static files not loading
- Ensure all paths are relative (not absolute)
- Check Publish Directory setting

## Monitoring
- View logs: Render Dashboard → Your Service → Logs
- Check health: Visit `https://your-backend-url.onrender.com/docs` for API documentation
