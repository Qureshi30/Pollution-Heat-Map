# Render Deployment - Quick Start Guide

## 🚀 Quick Deployment Steps

### 1️⃣ Prepare Your Repository

```bash
# Navigate to project directory
cd c:\Users\hassan\Desktop\Pollutionheatmap\python\pollution-heatmap

# If not already initialized
git init
git add .
git commit -m "Ready for Render deployment"
```

### 2️⃣ Push to GitHub

1. Create a new repository on GitHub: https://github.com/new
2. Name it something like `pollution-heatmap`
3. Run these commands:

```bash
git remote add origin https://github.com/YOUR_USERNAME/pollution-heatmap.git
git branch -M main
git push -u origin main
```

### 3️⃣ Deploy Backend API

1. **Go to Render**: https://dashboard.render.com
2. **Click "New +"** → **"Web Service"**
3. **Connect GitHub** repository
4. **Fill in these settings**:
   
   ```
   Name:               pollution-heatmap-api
   Region:             Oregon (or closest to you)
   Branch:             main
   Root Directory:     backend
   Runtime:            Python 3
   Build Command:      pip install -r requirements.txt
   Start Command:      uvicorn carbon_calculator:app --host 0.0.0.0 --port $PORT
   Instance Type:      Free
   ```

5. **Click "Create Web Service"**
6. **Wait 5-10 minutes** for deployment
7. **Copy the URL** (looks like: `https://pollution-heatmap-api.onrender.com`)

### 4️⃣ Update Frontend Configuration

Open `frontend/calculator.js` and update line 4:

```javascript
// Change from:
const API_BASE_URL = 'http://localhost:8002';

// To your Render backend URL (paste the URL from step 3):
const API_BASE_URL = 'https://pollution-heatmap-api.onrender.com';
```

Do the same for `frontend/script.js` and `frontend/script2.js` if they have API calls.

Then commit and push:

```bash
git add .
git commit -m "Update API URL for production"
git push
```

### 5️⃣ Deploy Frontend

1. **Go back to Render Dashboard**: https://dashboard.render.com
2. **Click "New +"** → **"Static Site"**
3. **Connect the same GitHub repository**
4. **Fill in these settings**:
   
   ```
   Name:               pollution-heatmap-frontend
   Branch:             main
   Root Directory:     frontend
   Build Command:      (leave empty)
   Publish Directory:  .
   ```

5. **Click "Create Static Site"**
6. **Wait 2-3 minutes**
7. **Your app is LIVE!** 🎉

You'll get a URL like: `https://pollution-heatmap-frontend.onrender.com`

---

## ✅ Verify Deployment

1. **Backend API**: Visit `https://YOUR-BACKEND-URL.onrender.com/docs`
   - You should see the FastAPI documentation
   
2. **Frontend**: Visit `https://YOUR-FRONTEND-URL.onrender.com`
   - Your website should load
   - Try using the calculator to ensure it connects to the backend

---

## 🔄 Making Updates

After deployment, any changes you make:

```bash
git add .
git commit -m "Your update message"
git push
```

Render will **automatically redeploy** both services! 🚀

---

## ⚠️ Important Notes

- **Free Tier Sleep**: Backend sleeps after 15 min of inactivity. First request may take 30-60 seconds.
- **Custom Domain**: You can add your own domain in Render settings
- **Environment Variables**: Add in Render Dashboard → Service → Environment

---

## 🆘 Troubleshooting

**Backend fails to build?**
- Check Render logs in Dashboard → Service → Logs
- Verify `requirements.txt` is correct

**Frontend can't reach backend?**
- Make sure API_BASE_URL is updated in all JS files
- Check browser console (F12) for errors
- Verify CORS is enabled (it is in your code)

**Need help?**
- Check deployment logs in Render dashboard
- Visit Render docs: https://render.com/docs
