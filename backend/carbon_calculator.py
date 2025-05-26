from fastapi import FastAPI, HTTPException, Form, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import json
import datetime
import tempfile
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

app = FastAPI(title="Carbon Footprint Calculator API")

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, replace with specific frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models for request and response
class EmissionInput(BaseModel):
    # Transportation
    vehicle_type: str
    fuel_type: str
    miles_per_day: float  # Now represents kilometers_per_day
    public_transport: float
    flights_per_year: float
    flight_hours: float
    
    # Home Energy
    electricity_kwh: float
    gas_usage: float
    water_usage: float  # Now represents liters_per_day
    renewable_energy: str
    
    # Diet & Lifestyle
    diet_type: str
    local_food: str
    food_waste: str
    recycling_level: str

class EmissionResult(BaseModel):
    total_emissions: float
    transportation_emissions: float
    energy_emissions: float
    diet_emissions: float
    recommendations: List[str]
    exceeds_threshold: bool

# Emission factors and calculation functions
def calculate_transportation_emissions(vehicle_type, fuel_type, miles_per_day, public_transport, flights_per_year, flight_hours):
    # Note: miles_per_day parameter now actually contains kilometers_per_day
    kilometers_per_day = miles_per_day
    emissions = 0
    
    # Vehicle emissions (tons CO2 per year)
    if vehicle_type != 'none' and kilometers_per_day > 0:
        kilometers_per_year = kilometers_per_day * 365
        
        # Emission factors in kg CO2 per kilometer
        emission_factor = 0
        
        if vehicle_type == 'small-car':
            if fuel_type in ['gasoline', 'petrol']: emission_factor = 0.2
            elif fuel_type == 'diesel': emission_factor = 0.17
            elif fuel_type == 'hybrid': emission_factor = 0.12
            elif fuel_type == 'electric': emission_factor = 0.06
        elif vehicle_type == 'medium-car':
            if fuel_type in ['gasoline', 'petrol']: emission_factor = 0.26
            elif fuel_type == 'diesel': emission_factor = 0.23
            elif fuel_type == 'hybrid': emission_factor = 0.14
            elif fuel_type == 'electric': emission_factor = 0.06
        elif vehicle_type == 'large-car':
            if fuel_type in ['gasoline', 'petrol']: emission_factor = 0.36
            elif fuel_type == 'diesel': emission_factor = 0.32
            elif fuel_type == 'hybrid': emission_factor = 0.19
            elif fuel_type == 'electric': emission_factor = 0.06
        elif vehicle_type == 'motorcycle':
            emission_factor = 0.11
        
        # Convert kg to metric tons (1000 kg = 1 metric ton)
        emissions += (kilometers_per_year * emission_factor) / 1000
    
    # Public transport emissions (tons CO2 per year)
    if public_transport > 0:
        # Average emission factor for public transport (kg CO2 per hour)
        public_transport_factor = 2.5
        emissions += (public_transport * 52 * public_transport_factor) / 1000
    
    # Flight emissions (tons CO2 per year)
    if flights_per_year > 0 and flight_hours > 0:
        # Average emission factor for flights (kg CO2 per hour)
        flight_factor = 90
        emissions += (flights_per_year * flight_hours * flight_factor) / 1000
    
    return round(emissions, 2)

def calculate_energy_emissions(electricity_kwh, gas_usage, water_usage, renewable_energy):
    # Note: water_usage parameter now represents liters_per_day
    liters_per_day = water_usage
    emissions = 0
    
    # Electricity emissions (tons CO2 per year)
    if electricity_kwh > 0:
        # Average emission factor for electricity (kg CO2 per kWh)
        electricity_factor = 0.42
        
        # Apply reduction for renewable energy
        if renewable_energy == 'partial': electricity_factor *= 0.7
        elif renewable_energy == 'significant': electricity_factor *= 0.3
        elif renewable_energy == 'complete': electricity_factor = 0
        
        emissions += (electricity_kwh * 12 * electricity_factor) / 1000
    
    # Natural gas emissions (tons CO2 per year)
    if gas_usage > 0:
        # Emission factor for natural gas (kg CO2 per therm)
        gas_factor = 5.3
        emissions += (gas_usage * 12 * gas_factor) / 1000
    
    # Water usage emissions (tons CO2 per year)
    if liters_per_day > 0:
        # Emission factor for water (kg CO2 per 1000 liters)
        water_factor = 1.2  # Adjusted for liters instead of gallons
        emissions += (liters_per_day * 365 * water_factor) / (1000 * 1000)
    
    return round(emissions, 2)

def calculate_diet_emissions(diet_type, local_food, food_waste, recycling_level):
    emissions = 0
    
    # Diet emissions (tons CO2 per year)
    # Base emissions by diet type (tons CO2 per year)
    if diet_type == 'meat-heavy': emissions += 3.3
    elif diet_type == 'meat-medium': emissions += 2.5
    elif diet_type == 'pescatarian': emissions += 1.9
    elif diet_type == 'vegetarian': emissions += 1.7
    elif diet_type == 'vegan': emissions += 1.5
    
    # Adjust for local food consumption
    local_food_factor = 1.0
    if local_food == 'mostly': local_food_factor = 0.9
    elif local_food == 'half': local_food_factor = 0.95
    elif local_food == 'some': local_food_factor = 0.98
    elif local_food == 'very-little': local_food_factor = 1.0
    
    emissions *= local_food_factor
    
    # Adjust for food waste
    food_waste_factor = 1.0
    if food_waste == 'minimal': food_waste_factor = 1.0
    elif food_waste == 'low': food_waste_factor = 1.05
    elif food_waste == 'average': food_waste_factor = 1.1
    elif food_waste == 'high': food_waste_factor = 1.2
    elif food_waste == 'very-high': food_waste_factor = 1.3
    
    emissions *= food_waste_factor
    
    # Adjust for recycling level
    recycling_reduction = 0
    if recycling_level == 'minimal': recycling_reduction = 0.1
    elif recycling_level == 'moderate': recycling_reduction = 0.3
    elif recycling_level == 'extensive': recycling_reduction = 0.5
    elif recycling_level == 'zero-waste': recycling_reduction = 0.8
    
    # Add waste & consumption emissions and apply recycling reduction
    waste_emissions = 1.5 * (1 - recycling_reduction)
    emissions += waste_emissions
    
    return round(emissions, 2)

def generate_recommendations(data):
    # Note: data.miles_per_day now represents kilometers_per_day
    kilometers_per_day = data.miles_per_day
    recommendations = []
    
    # Transportation recommendations
    if data.vehicle_type != 'none' and data.vehicle_type != 'electric' and kilometers_per_day > 30:
        recommendations.append('Consider carpooling or using public transportation to reduce your daily driving emissions.')
    
    if data.vehicle_type != 'none' and data.vehicle_type != 'electric' and data.vehicle_type != 'hybrid':
        recommendations.append('When possible, consider switching to a more fuel-efficient or electric vehicle.')
    
    if data.public_transport < 2 and kilometers_per_day > 15:
        recommendations.append('Try using public transportation more frequently for your regular commute.')
    
    if data.flights_per_year > 3:
        recommendations.append('Consider reducing air travel or offsetting your flight emissions through carbon offset programs.')
    
    # Energy recommendations
    if data.electricity_kwh > 500 and data.renewable_energy == 'none':
        recommendations.append('Look into renewable energy options for your home, such as solar panels or a green energy provider.')
    
    if data.electricity_kwh > 300:
        recommendations.append('Reduce electricity usage by using energy-efficient appliances and turning off lights and devices when not in use.')
    
    if data.gas_usage > 50:
        recommendations.append('Improve home insulation and heating efficiency to reduce natural gas consumption.')
    
    if data.water_usage > 300:  # Adjusted threshold for liters
        recommendations.append('Install water-efficient fixtures and be mindful of water usage to reduce your water-related emissions.')
    
    # Diet & lifestyle recommendations
    if data.diet_type in ['meat-heavy', 'meat-medium']:
        recommendations.append('Consider reducing meat consumption, particularly red meat, to lower your dietary carbon footprint.')
    
    if data.local_food in ['very-little', 'some']:
        recommendations.append('Try to purchase more locally produced food to reduce transportation emissions in your food supply chain.')
    
    if data.food_waste in ['high', 'very-high']:
        recommendations.append('Plan meals carefully and store food properly to reduce food waste.')
    
    if data.recycling_level in ['none', 'minimal']:
        recommendations.append('Improve your recycling habits and try to reduce single-use plastics and packaging.')
    
    # Limit to 5 most relevant recommendations
    if len(recommendations) > 5:
        recommendations = recommendations[:5]
    
    return recommendations

def generate_pdf_report(result, input_data):
    # Create a temporary file for the PDF
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    pdf_path = temp_file.name
    temp_file.close()
    
    # Create the PDF document
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    
    # Add title
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=18,
        alignment=1,
        spaceAfter=12
    )
    elements.append(Paragraph("Carbon Footprint Report", title_style))
    elements.append(Spacer(1, 0.25*inch))
    
    # Add date
    date_style = ParagraphStyle(
        'Date',
        parent=styles['Normal'],
        fontSize=10,
        alignment=1
    )
    elements.append(Paragraph(f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", date_style))
    elements.append(Spacer(1, 0.5*inch))
    
    # Add summary section
    elements.append(Paragraph("Emissions Summary", styles['Heading2']))
    elements.append(Spacer(1, 0.1*inch))
    
    # Create summary table
    summary_data = [
        ["Category", "Emissions (tons CO2e)"],
        ["Transportation", str(result.transportation_emissions)],
        ["Home Energy", str(result.energy_emissions)],
        ["Diet & Lifestyle", str(result.diet_emissions)],
        ["Total", str(result.total_emissions)]
    ]
    
    summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.green),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.white),
        ('ALIGN', (0, 0), (1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (1, 0), 12),
        ('BACKGROUND', (0, -1), (1, -1), colors.lightgreen),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Add comparison to average
    us_average = 16
    comparison_text = f"Your carbon footprint is {round((result.total_emissions / us_average) * 100)}% of the US average ({us_average} tons CO2e per year)."
    if result.exceeds_threshold:
        comparison_text += " Your emissions are above the recommended threshold. Please consider implementing the recommendations below."
    elements.append(Paragraph(comparison_text, styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))
    
    # Add recommendations section
    elements.append(Paragraph("Recommendations", styles['Heading2']))
    elements.append(Spacer(1, 0.1*inch))
    
    for i, recommendation in enumerate(result.recommendations):
        elements.append(Paragraph(f"{i+1}. {recommendation}", styles['Normal']))
        elements.append(Spacer(1, 0.1*inch))
    
    # Add input data section
    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph("Your Input Data", styles['Heading2']))
    elements.append(Spacer(1, 0.1*inch))
    
    # Transportation data
    elements.append(Paragraph("Transportation", styles['Heading3']))
    transport_data = [
        ["Vehicle Type", input_data.vehicle_type],
        ["Fuel Type", input_data.fuel_type],
        ["Kilometers Per Day", str(input_data.miles_per_day)],
        ["Public Transport (hours/week)", str(input_data.public_transport)],
        ["Flights Per Year", str(input_data.flights_per_year)],
        ["Flight Hours", str(input_data.flight_hours)]
    ]
    transport_table = Table(transport_data, colWidths=[3*inch, 2*inch])
    transport_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
    ]))
    elements.append(transport_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Home Energy data
    elements.append(Paragraph("Home Energy", styles['Heading3']))
    energy_data = [
        ["Electricity (kWh/month)", str(input_data.electricity_kwh)],
        ["Natural Gas (therms/month)", str(input_data.gas_usage)],
        ["Water Usage (liters/day)", str(input_data.water_usage)],
        ["Renewable Energy", input_data.renewable_energy]
    ]
    energy_table = Table(energy_data, colWidths=[3*inch, 2*inch])
    energy_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightyellow),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
    ]))
    elements.append(energy_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Diet & Lifestyle data
    elements.append(Paragraph("Diet & Lifestyle", styles['Heading3']))
    diet_data = [
        ["Diet Type", input_data.diet_type],
        ["Local Food Consumption", input_data.local_food],
        ["Food Waste", input_data.food_waste],
        ["Recycling Level", input_data.recycling_level]
    ]
    diet_table = Table(diet_data, colWidths=[3*inch, 2*inch])
    diet_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgreen),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
    ]))
    elements.append(diet_table)
    
    # Build the PDF
    doc.build(elements)
    
    return pdf_path

@app.get("/")
async def root():
    return {"message": "Welcome to Carbon Footprint Calculator API"}

@app.post("/api/calculate-emissions")
async def calculate_emissions(data: EmissionInput):
    try:
        # Calculate emissions for each category
        transportation_emissions = calculate_transportation_emissions(
            data.vehicle_type, data.fuel_type, data.miles_per_day, 
            data.public_transport, data.flights_per_year, data.flight_hours
        )
        
        energy_emissions = calculate_energy_emissions(
            data.electricity_kwh, data.gas_usage, data.water_usage, data.renewable_energy
        )
        
        diet_emissions = calculate_diet_emissions(
            data.diet_type, data.local_food, data.food_waste, data.recycling_level
        )
        
        # Calculate total emissions
        total_emissions = round(transportation_emissions + energy_emissions + diet_emissions, 2)
        
        # Generate recommendations
        recommendations = generate_recommendations(data)
        
        # Check if emissions exceed threshold (e.g., 10 tons CO2e per year)
        exceeds_threshold = total_emissions > 10
        
        # Create result object
        result = EmissionResult(
            total_emissions=total_emissions,
            transportation_emissions=transportation_emissions,
            energy_emissions=energy_emissions,
            diet_emissions=diet_emissions,
            recommendations=recommendations,
            exceeds_threshold=exceeds_threshold
        )
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating emissions: {str(e)}")

@app.post("/api/generate-report")
async def generate_report(data: EmissionInput):
    try:
        # First calculate emissions
        result = await calculate_emissions(data)
        
        # Generate PDF report
        pdf_path = generate_pdf_report(result, data)
        
        # Return the PDF file
        return FileResponse(
            path=pdf_path,
            filename="carbon-footprint-report.pdf",
            media_type="application/pdf"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")

# Run with: uvicorn carbon_calculator:app --reload --port 8002
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002) 