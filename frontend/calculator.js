// Carbon Emission Calculator JavaScript

// API endpoint
const API_BASE_URL = 'http://localhost:8002';

document.addEventListener('DOMContentLoaded', function () {
    // Get form and result elements
    const calculatorForm = document.getElementById('emission-calculator-form');
    const resultsSection = document.getElementById('results-section');
    const downloadReportBtn = document.getElementById('download-report-btn');

    // Add event listener for form submission
    calculatorForm.addEventListener('submit', function (e) {
        e.preventDefault();
        calculateEmissions();
    });

    // Add event listener for download report button
    downloadReportBtn.addEventListener('click', function () {
        generateReport();
    });

    // Add Petrol option to fuel type dropdown
    const fuelTypeSelect = document.getElementById('fuel-type');
    if (fuelTypeSelect) {
        // Check if Petrol option already exists
        let petrolExists = false;
        for (let i = 0; i < fuelTypeSelect.options.length; i++) {
            if (fuelTypeSelect.options[i].value === 'petrol') {
                petrolExists = true;
                break;
            }
        }

        // Add Petrol option if it doesn't exist
        if (!petrolExists) {
            const petrolOption = document.createElement('option');
            petrolOption.value = 'petrol';
            petrolOption.textContent = 'Petrol';
            // Insert after gasoline option
            const gasolineOption = Array.from(fuelTypeSelect.options).find(opt => opt.value === 'gasoline');
            if (gasolineOption) {
                fuelTypeSelect.insertBefore(petrolOption, gasolineOption.nextSibling);
            } else {
                fuelTypeSelect.appendChild(petrolOption);
            }
        }
    }
});

// Function to calculate emissions based on form inputs
async function calculateEmissions() {
    // Show loading state
    document.getElementById('calculate-btn').textContent = 'Calculating...';
    document.getElementById('calculate-btn').disabled = true;

    // Get form values
    const vehicleType = document.getElementById('vehicle-type').value;
    const fuelType = document.getElementById('fuel-type').value;
    const kilometersPerDay = parseFloat(document.getElementById('miles-per-day').value) || 0;
    const publicTransport = parseFloat(document.getElementById('public-transport').value) || 0;
    const flightsPerYear = parseFloat(document.getElementById('flights-per-year').value) || 0;
    const flightHours = parseFloat(document.getElementById('flight-hours').value) || 0;

    const electricityKwh = parseFloat(document.getElementById('electricity-kwh').value) || 0;
    const gasUsage = parseFloat(document.getElementById('gas-usage').value) || 0;
    const waterUsageLiters = parseFloat(document.getElementById('water-usage').value) || 0;
    const renewableEnergy = document.getElementById('renewable-energy').value;

    const dietType = document.getElementById('diet-type').value;
    const localFood = document.getElementById('local-food').value;
    const foodWaste = document.getElementById('food-waste').value;
    const recyclingLevel = document.getElementById('recycling-level').value;

    // First calculate locally to ensure we always have a result
    const transportationEmissions = calculateTransportationEmissions(
        vehicleType, fuelType, kilometersPerDay, publicTransport, flightsPerYear, flightHours
    );

    const energyEmissions = calculateEnergyEmissions(
        electricityKwh, gasUsage, waterUsageLiters, renewableEnergy
    );

    const dietEmissions = calculateDietEmissions(
        dietType, localFood, foodWaste, recyclingLevel
    );

    const totalEmissions = transportationEmissions + energyEmissions + dietEmissions;

    // Generate basic recommendations
    const recommendations = [
        "Consider using public transportation more frequently to reduce emissions.",
        "Reducing meat consumption can significantly lower your carbon footprint.",
        "Installing energy-efficient appliances can help reduce your home energy emissions."
    ];

    // Try to use the backend API if available
    let useBackendResult = false;
    let backendResult = null;

    try {
        // Check if backend is accessible
        let backendAvailable = false;
        try {
            const pingResponse = await fetch(`${API_BASE_URL}/`, {
                method: 'GET',
                mode: 'cors',
                headers: {
                    'Accept': 'application/json'
                },
                timeout: 3000 // 3 second timeout
            });
            backendAvailable = pingResponse.ok;
        } catch (pingError) {
            console.warn('Backend not accessible:', pingError);
            backendAvailable = false;
        }

        if (backendAvailable) {
            // Convert kilometers to miles for API (if the backend still expects miles)
            const milesPerDay = kilometersPerDay * 0.621371;

            // Convert liters to gallons for API (if the backend still expects gallons)
            const waterUsageGallons = waterUsageLiters * 0.264172;

            // Prepare data for API
            const data = {
                vehicle_type: vehicleType,
                fuel_type: fuelType,
                miles_per_day: kilometersPerDay, // We're now sending kilometers directly
                public_transport: publicTransport,
                flights_per_year: flightsPerYear,
                flight_hours: flightHours,
                electricity_kwh: electricityKwh,
                gas_usage: gasUsage,
                water_usage: waterUsageLiters, // We're now sending liters directly
                renewable_energy: renewableEnergy,
                diet_type: dietType,
                local_food: localFood,
                food_waste: foodWaste,
                recycling_level: recyclingLevel
            };

            // Call the backend API
            const response = await fetch(`${API_BASE_URL}/api/calculate-emissions`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            if (response.ok) {
                backendResult = await response.json();
                useBackendResult = true;
            } else {
                throw new Error(`API error: ${response.status}`);
            }
        }
    } catch (error) {
        console.error('Error calculating emissions from backend:', error);
        // We'll use the local calculation results
    }

    // Update the UI with results (either from backend or local calculation)
    if (useBackendResult && backendResult) {
        updateResults(
            backendResult.total_emissions,
            backendResult.transportation_emissions,
            backendResult.energy_emissions,
            backendResult.diet_emissions
        );

        // Update recommendations
        updateRecommendations(backendResult.recommendations);
    } else {
        // Use local calculation results
        updateResults(
            totalEmissions,
            transportationEmissions,
            energyEmissions,
            dietEmissions
        );

        // Use basic recommendations
        updateRecommendations(recommendations);
    }

    // Show results section and enable download button
    document.getElementById('results-section').classList.remove('hidden');
    document.getElementById('download-report-btn').disabled = false;

    // Scroll to results
    document.getElementById('results-section').scrollIntoView({ behavior: 'smooth' });

    // Reset button state
    document.getElementById('calculate-btn').textContent = 'Calculate Emissions';
    document.getElementById('calculate-btn').disabled = false;
}

// Calculate transportation emissions
function calculateTransportationEmissions(vehicleType, fuelType, kilometersPerDay, publicTransport, flightsPerYear, flightHours) {
    let emissions = 0;

    // Vehicle emissions (tons CO2 per year)
    if (vehicleType !== 'none' && kilometersPerDay > 0) {
        const kilometersPerYear = kilometersPerDay * 365;

        // Emission factors in kg CO2 per kilometer
        let emissionFactor = 0;

        if (vehicleType === 'small-car') {
            if (fuelType === 'gasoline' || fuelType === 'petrol') emissionFactor = 0.2;
            else if (fuelType === 'diesel') emissionFactor = 0.17;
            else if (fuelType === 'hybrid') emissionFactor = 0.12;
            else if (fuelType === 'electric') emissionFactor = 0.06;
        } else if (vehicleType === 'medium-car') {
            if (fuelType === 'gasoline' || fuelType === 'petrol') emissionFactor = 0.26;
            else if (fuelType === 'diesel') emissionFactor = 0.23;
            else if (fuelType === 'hybrid') emissionFactor = 0.14;
            else if (fuelType === 'electric') emissionFactor = 0.06;
        } else if (vehicleType === 'large-car') {
            if (fuelType === 'gasoline' || fuelType === 'petrol') emissionFactor = 0.36;
            else if (fuelType === 'diesel') emissionFactor = 0.32;
            else if (fuelType === 'hybrid') emissionFactor = 0.19;
            else if (fuelType === 'electric') emissionFactor = 0.06;
        } else if (vehicleType === 'motorcycle') {
            emissionFactor = 0.11;
        }

        // Convert kg to metric tons (1000 kg = 1 metric ton)
        emissions += (kilometersPerYear * emissionFactor) / 1000;
    }

    // Public transport emissions (tons CO2 per year)
    if (publicTransport > 0) {
        // Average emission factor for public transport (kg CO2 per hour)
        const publicTransportFactor = 2.5;
        emissions += (publicTransport * 52 * publicTransportFactor) / 1000;
    }

    // Flight emissions (tons CO2 per year)
    if (flightsPerYear > 0 && flightHours > 0) {
        // Average emission factor for flights (kg CO2 per hour)
        const flightFactor = 90;
        emissions += (flightsPerYear * flightHours * flightFactor) / 1000;
    }

    return emissions;
}

// Calculate home energy emissions
function calculateEnergyEmissions(electricityKwh, gasUsage, waterUsageLiters, renewableEnergy) {
    let emissions = 0;

    // Electricity emissions (tons CO2 per year)
    if (electricityKwh > 0) {
        // Average emission factor for electricity (kg CO2 per kWh)
        let electricityFactor = 0.42;

        // Apply reduction for renewable energy
        if (renewableEnergy === 'partial') electricityFactor *= 0.7;
        else if (renewableEnergy === 'significant') electricityFactor *= 0.3;
        else if (renewableEnergy === 'complete') electricityFactor = 0;

        emissions += (electricityKwh * 12 * electricityFactor) / 1000;
    }

    // Natural gas emissions (tons CO2 per year)
    if (gasUsage > 0) {
        // Emission factor for natural gas (kg CO2 per therm)
        const gasFactor = 5.3;
        emissions += (gasUsage * 12 * gasFactor) / 1000;
    }

    // Water usage emissions (tons CO2 per year)
    if (waterUsageLiters > 0) {
        // Emission factor for water (kg CO2 per 1000 liters)
        const waterFactor = 1.2; // Adjusted for liters instead of gallons
        emissions += (waterUsageLiters * 365 * waterFactor) / (1000 * 1000);
    }

    return emissions;
}

// Calculate diet and lifestyle emissions
function calculateDietEmissions(dietType, localFood, foodWaste, recyclingLevel) {
    let emissions = 0;

    // Diet emissions (tons CO2 per year)
    // Base emissions by diet type (tons CO2 per year)
    if (dietType === 'meat-heavy') emissions += 3.3;
    else if (dietType === 'meat-medium') emissions += 2.5;
    else if (dietType === 'pescatarian') emissions += 1.9;
    else if (dietType === 'vegetarian') emissions += 1.7;
    else if (dietType === 'vegan') emissions += 1.5;

    // Adjust for local food consumption
    let localFoodFactor = 1.0;
    if (localFood === 'mostly') localFoodFactor = 0.9;
    else if (localFood === 'half') localFoodFactor = 0.95;
    else if (localFood === 'some') localFoodFactor = 0.98;
    else if (localFood === 'very-little') localFoodFactor = 1.0;

    emissions *= localFoodFactor;

    // Adjust for food waste
    let foodWasteFactor = 1.0;
    if (foodWaste === 'minimal') foodWasteFactor = 1.0;
    else if (foodWaste === 'low') foodWasteFactor = 1.05;
    else if (foodWaste === 'average') foodWasteFactor = 1.1;
    else if (foodWaste === 'high') foodWasteFactor = 1.2;
    else if (foodWaste === 'very-high') foodWasteFactor = 1.3;

    emissions *= foodWasteFactor;

    // Adjust for recycling level
    let recyclingReduction = 0;
    if (recyclingLevel === 'minimal') recyclingReduction = 0.1;
    else if (recyclingLevel === 'moderate') recyclingReduction = 0.3;
    else if (recyclingLevel === 'extensive') recyclingReduction = 0.5;
    else if (recyclingLevel === 'zero-waste') recyclingReduction = 0.8;

    // Add waste & consumption emissions and apply recycling reduction
    const wasteEmissions = 1.5 * (1 - recyclingReduction);
    emissions += wasteEmissions;

    return emissions;
}

// Update the results UI
function updateResults(totalEmissions, transportationEmissions, energyEmissions, dietEmissions) {
    // Round to 2 decimal places
    totalEmissions = Math.round(totalEmissions * 100) / 100;
    transportationEmissions = Math.round(transportationEmissions * 100) / 100;
    energyEmissions = Math.round(energyEmissions * 100) / 100;
    dietEmissions = Math.round(dietEmissions * 100) / 100;

    // Update total emissions
    document.getElementById('total-emissions').textContent = totalEmissions;

    // Update comparison bar (US average is 16 tons)
    const percentOfAverage = Math.min(100, (totalEmissions / 16) * 100);
    document.getElementById('footprint-bar').style.width = `${percentOfAverage}%`;

    // Update category emissions
    document.getElementById('transportation-emissions').textContent = `${transportationEmissions} tons`;
    document.getElementById('energy-emissions').textContent = `${energyEmissions} tons`;
    document.getElementById('diet-emissions').textContent = `${dietEmissions} tons`;

    // Update category bars
    const total = transportationEmissions + energyEmissions + dietEmissions;
    document.getElementById('transportation-bar').style.width = `${(transportationEmissions / total) * 100}%`;
    document.getElementById('energy-bar').style.width = `${(energyEmissions / total) * 100}%`;
    document.getElementById('diet-bar').style.width = `${(dietEmissions / total) * 100}%`;
}

// Update recommendations list
function updateRecommendations(recommendations) {
    const recommendationsList = document.getElementById('recommendations-list');
    recommendationsList.innerHTML = '';

    recommendations.forEach(recommendation => {
        const li = document.createElement('li');
        li.textContent = recommendation;
        recommendationsList.appendChild(li);
    });
}

// Generate and download PDF report
async function generateReport() {
    // Show loading state
    document.getElementById('download-report-btn').textContent = 'Generating...';
    document.getElementById('download-report-btn').disabled = true;

    // Get form values (same as calculateEmissions)
    const vehicleType = document.getElementById('vehicle-type').value;
    const fuelType = document.getElementById('fuel-type').value;
    const kilometersPerDay = parseFloat(document.getElementById('miles-per-day').value) || 0;
    const publicTransport = parseFloat(document.getElementById('public-transport').value) || 0;
    const flightsPerYear = parseFloat(document.getElementById('flights-per-year').value) || 0;
    const flightHours = parseFloat(document.getElementById('flight-hours').value) || 0;

    const electricityKwh = parseFloat(document.getElementById('electricity-kwh').value) || 0;
    const gasUsage = parseFloat(document.getElementById('gas-usage').value) || 0;
    const waterUsageLiters = parseFloat(document.getElementById('water-usage').value) || 0;
    const renewableEnergy = document.getElementById('renewable-energy').value;

    const dietType = document.getElementById('diet-type').value;
    const localFood = document.getElementById('local-food').value;
    const foodWaste = document.getElementById('food-waste').value;
    const recyclingLevel = document.getElementById('recycling-level').value;

    // Prepare data for API
    const data = {
        vehicle_type: vehicleType,
        fuel_type: fuelType,
        miles_per_day: kilometersPerDay,
        public_transport: publicTransport,
        flights_per_year: flightsPerYear,
        flight_hours: flightHours,
        electricity_kwh: electricityKwh,
        gas_usage: gasUsage,
        water_usage: waterUsageLiters,
        renewable_energy: renewableEnergy,
        diet_type: dietType,
        local_food: localFood,
        food_waste: foodWaste,
        recycling_level: recyclingLevel
    };

    try {
        // Check if backend is accessible first
        let backendAvailable = false;
        try {
            const pingResponse = await fetch(`${API_BASE_URL}/`, {
                method: 'GET',
                mode: 'cors',
                headers: {
                    'Accept': 'application/json'
                },
                timeout: 3000 // 3 second timeout
            });
            backendAvailable = pingResponse.ok;
        } catch (pingError) {
            console.warn('Backend not accessible:', pingError);
            backendAvailable = false;
        }

        if (!backendAvailable) {
            console.log('Backend not available, using client-side report generation');
            throw new Error('Backend not available');
        }

        // Call the backend API to generate PDF
        const response = await fetch(`${API_BASE_URL}/api/generate-report`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/pdf'
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        // Get the PDF blob
        const blob = await response.blob();

        // Verify we got a PDF
        if (blob.type !== 'application/pdf') {
            console.warn('Response is not a PDF:', blob.type);
            throw new Error('Invalid response format');
        }

        // Create a download link
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'carbon-footprint-report.pdf';
        document.body.appendChild(a);
        a.click();

        // Clean up
        setTimeout(() => {
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }, 100);
    } catch (error) {
        console.error('Error generating report:', error);
        alert('Could not generate PDF report from server. Generating a text report instead.');

        // Fallback to client-side report generation
        generateClientSideReport();
    } finally {
        // Reset button state
        document.getElementById('download-report-btn').textContent = 'Download Report';
        document.getElementById('download-report-btn').disabled = false;
    }
}

// Fallback client-side report generation
function generateClientSideReport() {
    try {
        const totalEmissions = document.getElementById('total-emissions').textContent;
        const transportationEmissions = document.getElementById('transportation-emissions').textContent;
        const energyEmissions = document.getElementById('energy-emissions').textContent;
        const dietEmissions = document.getElementById('diet-emissions').textContent;

        // Get recommendations
        const recommendationsList = document.getElementById('recommendations-list');
        const recommendations = Array.from(recommendationsList.children).map(li => li.textContent);

        // Create report content
        let reportContent = "CARBON FOOTPRINT REPORT\n\n";
        reportContent += `Date: ${new Date().toLocaleDateString()}\n\n`;
        reportContent += "EMISSIONS SUMMARY\n";
        reportContent += `Total Annual Emissions: ${totalEmissions} metric tons CO2e\n`;
        reportContent += `Transportation Emissions: ${transportationEmissions}\n`;
        reportContent += `Home Energy Emissions: ${energyEmissions}\n`;
        reportContent += `Diet & Lifestyle Emissions: ${dietEmissions}\n\n`;

        // Add US average comparison
        const usAverage = 16;
        const percentOfAverage = Math.round((parseFloat(totalEmissions) / usAverage) * 100);
        reportContent += `Your carbon footprint is ${percentOfAverage}% of the US average (${usAverage} tons CO2e per year).\n\n`;

        // Add recommendations
        reportContent += "RECOMMENDATIONS\n";
        recommendations.forEach((rec, index) => {
            reportContent += `${index + 1}. ${rec}\n`;
        });

        // Add input data
        reportContent += "\nYOUR INPUT DATA\n";
        reportContent += `Vehicle Type: ${document.getElementById('vehicle-type').value}\n`;
        reportContent += `Fuel Type: ${document.getElementById('fuel-type').value}\n`;
        reportContent += `Kilometers Per Day: ${document.getElementById('miles-per-day').value}\n`;
        reportContent += `Public Transport (hours/week): ${document.getElementById('public-transport').value}\n`;
        reportContent += `Flights Per Year: ${document.getElementById('flights-per-year').value}\n`;
        reportContent += `Flight Hours: ${document.getElementById('flight-hours').value}\n\n`;

        reportContent += `Electricity (kWh/month): ${document.getElementById('electricity-kwh').value}\n`;
        reportContent += `Natural Gas (therms/month): ${document.getElementById('gas-usage').value}\n`;
        reportContent += `Water Usage (liters/day): ${document.getElementById('water-usage').value}\n`;
        reportContent += `Renewable Energy: ${document.getElementById('renewable-energy').value}\n\n`;

        reportContent += `Diet Type: ${document.getElementById('diet-type').value}\n`;
        reportContent += `Local Food Consumption: ${document.getElementById('local-food').value}\n`;
        reportContent += `Food Waste: ${document.getElementById('food-waste').value}\n`;
        reportContent += `Recycling Level: ${document.getElementById('recycling-level').value}\n\n`;

        reportContent += "Generated by Carbon Footprint Tracker\n";
        reportContent += "Note: This is a simplified text report as the PDF generation service was unavailable.";

        // Create a blob and download
        const blob = new Blob([reportContent], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'carbon-footprint-report.txt';
        document.body.appendChild(a);
        a.click();

        // Clean up
        setTimeout(() => {
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }, 100);
    } catch (error) {
        console.error('Error generating client-side report:', error);
        alert('Failed to generate report. Please try again later.');
    }
} 