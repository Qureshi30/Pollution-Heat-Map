// API endpoint
const API_BASE_URL = 'http://localhost:8001';

// DOM elements
const citySelect = document.getElementById('city-select');
const pollutantSelect = document.getElementById('pollutant-select');
const fetchDataBtn = document.getElementById('fetch-data-btn');
const mapLoading = document.getElementById('map-loading');
const chartLoading = document.getElementById('chart-loading');
const averageValue = document.getElementById('average-value');
const maxValue = document.getElementById('max-value');
const minValue = document.getElementById('min-value');
const textSummaryContainer = document.getElementById('text-summary-container');
const textSummary = document.getElementById('text-summary');
const healthImplications = document.getElementById('health-implications');
const trendAnalysis = document.getElementById('trend-analysis');
const mapFrame = document.getElementById('map-frame');

// Chart.js variables
let trendChart;

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    loadCities();
    loadPollutants();
    setupEventListeners();
});

// Fetch available cities from the API
async function loadCities() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/cities`);
        const data = await response.json();

        // Clear and update the city dropdown
        citySelect.innerHTML = '';
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
        const option = document.createElement('option');
        option.textContent = 'Error loading cities';
        citySelect.innerHTML = '';
        citySelect.appendChild(option);
    }
}

// Fetch available pollutants from the API
async function loadPollutants() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/pollutants`);
        const data = await response.json();

        // Clear and update the pollutant dropdown
        pollutantSelect.innerHTML = '';
        if (data.pollutants && data.pollutants.length > 0) {
            data.pollutants.forEach(pollutant => {
                const option = document.createElement('option');
                option.value = pollutant;
                option.textContent = pollutant;
                pollutantSelect.appendChild(option);
            });
        } else {
            const option = document.createElement('option');
            option.textContent = 'No pollutants available';
            pollutantSelect.appendChild(option);
        }
    } catch (error) {
        console.error('Error loading pollutants:', error);
        const option = document.createElement('option');
        option.textContent = 'Error loading pollutants';
        pollutantSelect.innerHTML = '';
        pollutantSelect.appendChild(option);
    }
}

// Set up event listeners
function setupEventListeners() {
    fetchDataBtn.addEventListener('click', fetchAndDisplayData);
}

// Fetch pollution data and display visualizations
async function fetchAndDisplayData() {
    const selectedCity = citySelect.value;
    const selectedPollutant = pollutantSelect.value;

    if (!selectedCity || !selectedPollutant) {
        alert('Please select both a city and a pollutant.');
        return;
    }

    // Show loading indicators
    mapLoading.style.display = 'block';
    chartLoading.style.display = 'block';

    try {
        // Load the map from the backend
        loadMapFromBackend(selectedCity, selectedPollutant);

        // Fetch pollution data for charts and statistics
        const response = await fetch(`${API_BASE_URL}/api/pollution-data?city=${selectedCity}&pollutant=${selectedPollutant}`);
        const data = await response.json();

        if (!data.data || data.data.length === 0) {
            alert(`No data found for ${selectedPollutant} in ${selectedCity}.`);
            mapLoading.style.display = 'none';
            chartLoading.style.display = 'none';
            return;
        }

        // Update the visualizations
        updateTrendChart(data.data, selectedPollutant);
        updateSummaryStats(data.data);

        // Generate and display text summary
        generateTextSummary(data.data, selectedCity, selectedPollutant);
    } catch (error) {
        console.error('Error fetching pollution data:', error);
        alert('An error occurred while fetching pollution data. Please try again.');
    } finally {
        // Hide chart loading indicator (map loading is handled by iframe onload)
        chartLoading.style.display = 'none';
    }
}

// Load map from backend
function loadMapFromBackend(city, pollutant) {
    console.log(`Loading map for city: ${city}, pollutant: ${pollutant}`);

    // Set the iframe source to the Folium map endpoint
    const mapUrl = `${API_BASE_URL}/api/folium-map?city=${encodeURIComponent(city)}&pollutant=${encodeURIComponent(pollutant)}`;
    console.log(`Map URL: ${mapUrl}`);

    // Show loading indicator
    mapLoading.style.display = 'block';

    // Set up iframe load event to hide loading indicator
    mapFrame.onload = function () {
        console.log('Map iframe loaded');
        mapLoading.style.display = 'none';
    };

    // Set up error handling
    mapFrame.onerror = function (error) {
        console.error('Error loading map iframe:', error);
        mapLoading.style.display = 'none';
        mapFrame.srcdoc = `
            <div style="color: red; padding: 20px; font-family: Arial, sans-serif; text-align: center;">
                <h3>Error Loading Map</h3>
                <p>Could not load the map for ${city} - ${pollutant}.</p>
                <p>Please check the console for more details.</p>
            </div>
        `;
    };

    // Set the iframe source to load the map
    mapFrame.src = mapUrl;
}

// Helper function to normalize DD-MM-YYYY to YYYY-MM-DD
function sanitizeDate(dateStr) {
    if (/^\d{2}-\d{2}-\d{4}$/.test(dateStr)) {
        const [day, month, year] = dateStr.split('-');
        return `${year}-${month}-${day}`;
    }
    return dateStr;
}

// Update the trend chart with pollution data
function updateTrendChart(data, pollutant) {
    const yearlyData = {};

    data.forEach(item => {
        try {
            const { year, date, value } = item;

            if (!year || !date || typeof value !== 'number') {
                console.warn('Skipping malformed data item:', item);
                return;
            }

            const normalizedDate = sanitizeDate(date);
            const dateObj = new Date(normalizedDate);
            const month = dateObj.getMonth();

            if (isNaN(month)) {
                console.warn('Invalid month from date:', date);
                return;
            }

            if (!yearlyData[year]) {
                yearlyData[year] = Array(12).fill(null).map(() => ({ sum: 0, count: 0 }));
            }

            yearlyData[year][month].sum += value;
            yearlyData[year][month].count += 1;
        } catch (error) {
            console.error('Error processing item:', item, error);
        }
    });

    // Prepare datasets
    const datasets = [];
    const colors = ['#4C6EF5', '#F59E0B', '#EF4444', '#10B981', '#8B5CF6', '#EC4899'];

    Object.keys(yearlyData).sort().forEach((year, index) => {
        const yearData = yearlyData[year];
        const monthlyAverages = yearData.map(month =>
            month && month.count > 0 ? month.sum / month.count : null
        );

        datasets.push({
            label: `${year}`,
            data: monthlyAverages,
            borderColor: colors[index % colors.length],
            backgroundColor: `${colors[index % colors.length]}33`,
            borderWidth: 2,
            tension: 0.3,
            pointRadius: 3,
            fill: false
        });
    });

    const ctx = document.getElementById('trend-chart').getContext('2d');

    if (trendChart) {
        trendChart.destroy();
    }

    trendChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            datasets: datasets
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: `Monthly Average ${pollutant} Levels By Year`,
                    font: {
                        size: 16
                    }
                },
                legend: {
                    position: 'top'
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Month'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: `${pollutant} Level`
                    },
                    beginAtZero: false
                }
            }
        }
    });
}



// Update summary statistics
function updateSummaryStats(data) {
    const values = data.map(item => item.value);
    const avg = values.reduce((sum, val) => sum + val, 0) / values.length;
    const max = Math.max(...values);
    const min = Math.min(...values);

    averageValue.textContent = avg.toFixed(2);
    maxValue.textContent = max.toFixed(2);
    minValue.textContent = min.toFixed(2);
}

// Generate and display text summary
function generateTextSummary(data, city, pollutant) {
    // Show the summary container
    textSummaryContainer.style.display = 'block';

    // Calculate statistics
    const values = data.map(item => item.value);
    const avg = values.reduce((sum, val) => sum + val, 0) / values.length;
    const max = Math.max(...values);
    const min = Math.min(...values);

    // Group data by year for trend analysis
    const yearlyData = {};
    data.forEach(item => {
        const year = item.year;
        if (!yearlyData[year]) {
            yearlyData[year] = [];
        }
        yearlyData[year].push(item.value);
    });

    // Calculate yearly averages
    const yearlyAverages = {};
    Object.keys(yearlyData).forEach(year => {
        const values = yearlyData[year];
        yearlyAverages[year] = values.reduce((sum, val) => sum + val, 0) / values.length;
    });

    // Determine trend direction
    let trendDirection = 'stable';
    const years = Object.keys(yearlyAverages).sort();
    if (years.length > 1) {
        const firstYear = years[0];
        const lastYear = years[years.length - 1];
        const percentChange = ((yearlyAverages[lastYear] - yearlyAverages[firstYear]) / yearlyAverages[firstYear]) * 100;

        if (percentChange > 5) {
            trendDirection = 'increasing';
        } else if (percentChange < -5) {
            trendDirection = 'decreasing';
        }
    }

    // Generate main summary text
    textSummary.innerHTML = `
        <strong>${city}</strong> shows an average ${pollutant} level of <strong>${avg.toFixed(2)}</strong> 
        across the analyzed time period. The highest recorded value was <strong>${max.toFixed(2)}</strong>, 
        while the lowest was <strong>${min.toFixed(2)}</strong>. The data covers 
        <strong>${Object.keys(yearlyData).length}</strong> years of measurements.
    `;

    // Generate health implications based on pollutant
    healthImplications.innerHTML = getHealthImplications(pollutant, avg);

    // Generate trend analysis
    trendAnalysis.innerHTML = getTrendAnalysis(pollutant, yearlyAverages, trendDirection);
}

// Get health implications based on pollutant and level
function getHealthImplications(pollutant, level) {
    switch (pollutant) {
        case 'PM2.5':
            if (level < 12) {
                return 'Current PM2.5 levels are within the WHO annual air quality guideline. At these levels, health risks are minimal for most people.';
            } else if (level < 35) {
                return 'Moderate PM2.5 levels may cause respiratory symptoms in sensitive individuals. People with respiratory or heart conditions, the elderly, and children should limit prolonged outdoor exertion.';
            } else {
                return 'High PM2.5 levels can cause respiratory and cardiovascular effects in the general population. People with respiratory or heart conditions, the elderly, and children should avoid outdoor activities.';
            }

        case 'PM10':
            if (level < 20) {
                return 'Current PM10 levels are within the WHO annual air quality guideline. At these levels, health risks are minimal for most people.';
            } else if (level < 50) {
                return 'Moderate PM10 levels may cause minor respiratory irritation. Sensitive individuals may experience more serious health effects.';
            } else {
                return 'High PM10 levels can cause respiratory issues in the general population. People with respiratory conditions should limit outdoor exposure.';
            }

        case 'NO2':
            if (level < 40) {
                return 'Current NO2 levels are within acceptable limits. At these levels, health risks are minimal for most people.';
            } else {
                return 'Elevated NO2 levels can cause respiratory irritation and airway inflammation. People with asthma and other respiratory conditions may experience increased symptoms.';
            }

        case 'SO2':
            if (level < 20) {
                return 'Current SO2 levels are within acceptable limits. At these levels, health risks are minimal for most people.';
            } else {
                return 'Elevated SO2 levels can cause respiratory irritation and may trigger asthma symptoms. People with asthma should limit outdoor activities.';
            }

        case 'CO':
            if (level < 4) {
                return 'Current CO levels are within acceptable limits. At these levels, health risks are minimal for most people.';
            } else {
                return 'Elevated CO levels can reduce the blood\'s ability to transport oxygen, causing headaches, dizziness, and fatigue. People with heart disease may experience chest pain.';
            }

        case 'Ozone':
            if (level < 100) {
                return 'Current Ozone levels are within acceptable limits. At these levels, health risks are minimal for most people.';
            } else {
                return 'Elevated Ozone levels can cause respiratory irritation, reduced lung function, and aggravate asthma. Sensitive individuals should limit outdoor activities.';
            }

        default:
            return `${pollutant} can have various health effects depending on concentration levels. The current average level is ${level.toFixed(2)}.`;
    }
}

// Get trend analysis based on yearly data
function getTrendAnalysis(pollutant, yearlyAverages, trendDirection) {
    const years = Object.keys(yearlyAverages).sort();

    if (years.length <= 1) {
        return `There is insufficient multi-year data to establish a clear trend for ${pollutant} levels in this area.`;
    }

    const firstYear = years[0];
    const lastYear = years[years.length - 1];
    const percentChange = ((yearlyAverages[lastYear] - yearlyAverages[firstYear]) / yearlyAverages[firstYear]) * 100;

    let trendText = '';

    if (trendDirection === 'increasing') {
        trendText = `<span class="text-red-600">increased by ${Math.abs(percentChange).toFixed(1)}%</span>`;
    } else if (trendDirection === 'decreasing') {
        trendText = `<span class="text-green-600">decreased by ${Math.abs(percentChange).toFixed(1)}%</span>`;
    } else {
        trendText = `<span class="text-yellow-600">remained relatively stable</span>`;
    }

    return `
        From ${firstYear} to ${lastYear}, ${pollutant} levels have ${trendText}. 
        The average level in ${firstYear} was ${yearlyAverages[firstYear].toFixed(2)}, 
        while in ${lastYear} it was ${yearlyAverages[lastYear].toFixed(2)}. 
        ${getTrendRecommendation(pollutant, trendDirection)}
    `;
}

// Get recommendations based on pollutant and trend
function getTrendRecommendation(pollutant, trendDirection) {
    if (trendDirection === 'increasing') {
        return `This increasing trend suggests that air quality management strategies may need to be strengthened to control ${pollutant} emissions in this area.`;
    } else if (trendDirection === 'decreasing') {
        return `This decreasing trend suggests that current air quality management strategies may be effective in reducing ${pollutant} levels in this area.`;
    } else {
        return `The stable trend suggests that current emissions of ${pollutant} are neither increasing nor decreasing significantly over time.`;
    }
}

// Add this to your script.js
function showLocationOnMap(lat, lon, label) {
    const mapFrame = document.getElementById('map-frame');
    mapFrame.src = `http://localhost:8001/api/leaflet-marker?lat=${lat}&lon=${lon}&label=${encodeURIComponent(label || 'Selected Location')}`;
}

// Add to the heatmap JavaScript code
map.on('click', function (e) {
    // Add a marker at the clicked location
    var clickMarker = L.marker(e.latlng).addTo(map);

    // Open a popup with location information
    clickMarker.bindPopup(
        `<b>Selected Location</b><br>
        Latitude: ${e.latlng.lat.toFixed(6)}<br>
        Longitude: ${e.latlng.lng.toFixed(6)}<br>
        <button onclick="parent.postMessage({type: 'locationSelected', lat: ${e.latlng.lat}, lng: ${e.latlng.lng}}, '*')">
          Show Details
        </button>`
    ).openPopup();
});