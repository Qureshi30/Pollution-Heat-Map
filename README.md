# 🌍 Pollution Heat Map & Carbon Footprint Calculator

A comprehensive web-based tool for visualizing historical air pollution data, analyzing trends, and predicting future pollution levels using machine learning models. This project also features a Carbon Footprint Calculator to help users estimate their personal environmental impact.

---

## 📌 Overview

This project uses historical air quality data sourced from the [CPCB (Central Pollution Control Board)](https://cpcb.nic.in/) — India's official pollution monitoring body — to provide insights into urban air pollution in Mumbai. The application includes:
- An **interactive pollution heatmap**
- **Trend analysis** of pollutants over past years
- **Future pollution prediction** using ML models
- A **carbon footprint calculator**

---

## 📍 Covered Locations

- Byculla `(18.9794, 72.8368)`
- Colaba `(18.9100, 72.8050)`
- CSMT Airport `(18.9400, 72.8350)`
- Mazgaon `(18.9600, 72.8450)`
- Sion `(19.0390, 72.8619)`
- Worli `(18.9925, 72.8175)`

---

## ✨ Features

### 🔥 Pollution Heatmap
- Visualizes intensity of pollution levels across Mumbai locations using a heatmap.
- Based on **filtered historical data** from the CPCB.

### 📊 Trend Analysis
- Graphical visualization of pollution trends (e.g., PM2.5, NO₂, CO) over previous years.
- Helps users understand temporal changes in air quality.

### 🤖 Future Pollution Prediction
- Uses machine learning models:
  - **LSTM (Long Short-Term Memory)**
  - **RFR (Random Forest Regressor)**
  - **LGBM (Light Gradient Boosting Machine)**
- Predicts future pollutant levels for selected cities.

### 🧮 Carbon Footprint Calculator
- Estimates user’s carbon footprint based on lifestyle inputs (travel, energy usage, etc.)
- Encourages sustainable behavior through awareness.

---

## 🛠️ Tech Stack

### 🌐 Frontend:
- HTML
- CSS
- Tailwind CSS
- JavaScript

### ⚙️ Backend:
- Python (Flask/Django)

### 📈 Machine Learning & Data Analysis:
- Pandas, NumPy
- Matplotlib, Seaborn
- Scikit-learn
- TensorFlow / Keras
- LightGBM, XGBoost

### 🗺 Visualization Tools:
- Leaflet.js / Google Maps API
- Chart.js / Plotly

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/your-username/pollution-heatmap.git
cd pollution-heatmap
