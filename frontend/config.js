// Configuration file for API endpoints
// Update this file with your deployed backend URL after deployment

// For local development
// const API_BASE_URL = 'http://localhost:8002';

// For production (replace with your actual Render backend URL)
const API_BASE_URL = 'https://pollution-heat-map-backend.onrender.com';

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { API_BASE_URL };
}
