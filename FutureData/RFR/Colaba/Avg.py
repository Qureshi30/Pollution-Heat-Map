import pandas as pd

# Path to the original CSV file
file_path = r"C:\Users\siddi\OneDrive\Desktop\python\pollution-heatmap\FutureData\RFR\Colaba\RFR_Predicted_20.csv"

# Load the CSV data into a pandas DataFrame
df = pd.read_csv(file_path)

# Convert 'Timestamp' to datetime type with automatic format inference
df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')

# Group by the 'Timestamp' column and calculate the mean for each group
averaged_data = df.groupby('Timestamp').mean()

# Save the result to the original CSV file (overwrite)
averaged_data.to_csv(file_path)

# Show the averaged data
print(averaged_data)
