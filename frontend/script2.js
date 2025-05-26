// API endpoint
const API_BASE_URL = 'http://localhost:8001';

// DOM elements
const citySelect = document.getElementById('city-select');
const pollutantSelect = document.getElementById('pollutant-select');
const yearSelect = document.getElementById('year-select');
const modelSelect = document.getElementById('model-select');
const fetchDataBtn = document.getElementById('fetch-data-btn');
const chartLoading = document.getElementById('chart-loading');
const averageValue = document.getElementById('average-value');
const maxValue = document.getElementById('max-value');
const minValue = document.getElementById('min-value');
const textSummaryContainer = document.getElementById('text-summary-container');
const textSummary = document.getElementById('text-summary');
const healthImplications = document.getElementById('health-implications');
const trendAnalysis = document.getElementById('trend-analysis');
const modelInfoContainer = document.getElementById('model-info-container');
const modelDescription = document.getElementById('model-description');
const modelMetricsTable = document.getElementById('model-metrics');
const maeValue = document.getElementById('mae-value');
const r2Value = document.getElementById('r2-value');
const mapeValue = document.getElementById('mape-value');

// Chart.js variables
let trendChart;  // Chart.js chart instance

// Define a data object to store the model metrics
const modelMetricsData = {
    'Random Forest Regressor': {
        mae: '0.003532578888813489',
        r2: '99.82%',
        mape: '0.63%'
    },
    'LightGBM': {
        mae: '0.48604242590063407',
        r2: '98.95%',
        mape: '1.68%'
    },
    'LSTM': {
        mae: '0.0007495733083576547',
        r2: '100.00%',
        mape: '0.03%'
    },
    'Recurrent Neural Network': {
        mae: 'N/A',
        r2: 'N/A',
        mape: 'N/A'
    }
};

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    loadCities();
    loadModels();
    setupEventListeners();
});

// Load cities from API
async function loadCities() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/cities`);
        const data = await response.json();
        citySelect.innerHTML = '<option value="">Select a city</option>';  // Default option
        if (data.cities && data.cities.length > 0) {
            data.cities.forEach(city => {
                const option = document.createElement('option');
                option.value = city;
                option.textContent = city;
                citySelect.appendChild(option);
            });
        } else {
            const option = document.createElement('option');
            option.textContent = 'No cities available';
            citySelect.appendChild(option);
        }
    } catch (error) {
        console.error('Error loading cities:', error);
        citySelect.innerHTML = '<option value="">Error loading cities</option>';
    }
}

// Load models from API
async function loadModels() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/models`);
        const data = await response.json();
        modelSelect.innerHTML = '<option value="">Select a model</option>';  // Default option
        if (data.models && data.models.length > 0) {
            data.models.forEach(model => {
                const option = document.createElement('option');
                option.value = model;
                option.textContent = model;
                modelSelect.appendChild(option);
            });
        } else {
            const option = document.createElement('option');
            option.textContent = 'No models available';
            modelSelect.appendChild(option);
        }
    } catch (error) {
        console.error('Error loading models:', error);
        modelSelect.innerHTML = '<option value="">Error loading models</option>';
    }
}

// Fetch prediction data from API
async function fetchPredictionData() {
    const city = citySelect.value;  // Get selected city
    const model = modelSelect.value;  // Get selected model
    const year = yearSelect.value;  // Get selected year
    const emissionType = pollutantSelect.value;  // Get selected emission type

    if (!model || !year || !emissionType || !city) {  // Make sure all parameters are selected
        alert('Please select all fields');
        return;
    }

    chartLoading.style.display = 'block'; // Show loading spinner
    try {
        // Form the URL with query parameters
        const url = `${API_BASE_URL}/api/prediction-data?model=${model}&city=${city}&year=${year}&emission_type=${emissionType}`;
        console.log('Request URL:', url);  // Debug: Check if the URL is correct
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        console.log("API Response:", data);  // Log the response to see the structure

        if (data.data) {
            processPredictionData(data.data);  // Process and plot the data
        } else {
            alert('No data found for the selected criteria');
        }
    } catch (error) {
        console.error("Error fetching prediction data", error);
        alert(`Error fetching prediction data: ${error.message}`);
    } finally {
        chartLoading.style.display = 'none'; // Hide loading spinner
    }
}

// Process and plot the prediction data
function processPredictionData(data) {
    const labels = data.map(item => item.date);  // Using 'date' for the x-axis
    const values = data.map(item => item.prediction_value);  // Using 'prediction_value' for the y-axis

    // Update the chart or create a new one
    if (trendChart) {
        trendChart.data.labels = labels;
        trendChart.data.datasets[0].data = values;
        trendChart.update();
    } else {
        const ctx = document.getElementById('trend-chart').getContext('2d');
        trendChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Prediction Values',
                    data: values,
                    borderColor: 'rgba(75, 192, 192, 1)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    fill: true,
                }]
            },
            options: {
                responsive: true,
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Year',  // X-axis label is 'Year'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Prediction Value',  // Y-axis label is 'Prediction Value'
                        }
                    }
                }
            }
        });
    }
}

// Function to update the model info based on the selected model
function updateModelInfo(model) {
    modelInfoContainer.style.display = 'block'; // Show model info section

    // Hide the metrics table initially
    modelMetricsTable.style.display = 'none';
    
    // Set the description and metrics based on the selected model
    if (modelMetricsData[model]) {
        const metrics = modelMetricsData[model];
        
        // Update the model description and metrics
        switch (model) {
            case 'RFR':
                modelDescription.textContent = 'Random Forest Regressor is an ensemble learning method used for regression tasks. It works by constructing multiple decision trees and outputs the average prediction of all trees.';
                break;
            case 'LGBM':
                modelDescription.textContent = 'LightGBM (Light Gradient Boosting Machine) is a highly efficient gradient boosting framework that is used for classification and regression tasks.';
                break;
            case 'LSTM':
                modelDescription.textContent = 'Long Short-Term Memory (LSTM) is a type of Recurrent Neural Network (RNN) that is well-suited for sequential data and time-series prediction tasks.';
                break;
            case 'RNN':
                modelDescription.textContent = 'Recurrent Neural Networks (RNN) are a class of neural networks that are well-suited for sequence prediction tasks by maintaining hidden states across time steps.';
                break;
            default:
                modelDescription.textContent = 'No description available.';
        }

        // Update the MAE, R², and MAPE values
        maeValue.textContent = metrics.mae;
        r2Value.textContent = metrics.r2;
        mapeValue.textContent = metrics.mape;
    } else {
        // If no model is selected, hide model info
        modelInfoContainer.style.display = 'none';
    }

    // Display the metrics table
    modelMetricsTable.style.display = 'block';
}

// Event listener to update model info when model is selected
document.getElementById('model-select').addEventListener('change', function () {
    const modelSelect = document.getElementById('model-select');
    const selectedModel = modelSelect.value;

    // Update model info dynamically based on selection
    if (selectedModel) {
        updateModelInfo(selectedModel);
    } else {
        modelInfoContainer.style.display = 'none';
    }
});

// Event listener for fetching prediction data
fetchDataBtn.addEventListener('click', async () => {
    await fetchPredictionData();
});
