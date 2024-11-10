# gather_averages.py

import os
import pandas as pd

# Set paths for the folders containing the CSV files
PROCESSED_CSV_FOLDER = './processed_csvs'
EXAMPLE_CSV_FOLDER = './example_csvs'
EXPLANATION_CSV_FOLDER = './explanation_csvs'
PROCESSED_CSVS_LUMP_FOLDER = './processed_csvs_lump'  # Add this folder

# Names of the files to compare (same file names across folders)
file_names = [
    'processed_Alabama_Psychiatry_Dataset.csv',
    'processed_Birmingham_Anxiety_Dataset.csv',
    'processed_Eastside_Mental_Health_Dataset.csv',
    'processed_Restorative_Counseling_Dataset.csv',
    'processed_Thriveworks_Counseling_Dataset.csv'
]

# Columns to plot
columns_to_plot = ["Ranking", "Friendliness", "General Rating", "Flexibility", "Ease", "Affordability", "Response Time"]

# Function to extract average values from the last row of each file
def extract_averages(folder_path, file_name):
    file_path = os.path.join(folder_path, file_name)
    df = pd.read_csv(file_path)
    
    # Skip the 'average' row if it exists (or any other non-relevant row)
    if 'Average' in df['Name'].values:
        df = df[df['Name'] != 'Average']  # Remove the 'average' row
    
    # Print columns to verify column names
    print(f"Columns in {file_name}:", df.columns.tolist())
    
    # Get the last row, drop any columns with NaN values, and only keep relevant columns
    last_row = df.iloc[-1].dropna(subset=columns_to_plot)
    
    existing_columns = [col for col in columns_to_plot if col in last_row.index]
    return last_row[existing_columns].astype(float)

# Dictionary to store the averages for each dataset
data = {
    'Processed': [],
    'Example': [],
    'Explanation': [],
    'Lump': []  # For processed_csvs_lump
}

# Extract averages from each folder
for file_name in file_names:
    data['Processed'].append(extract_averages(PROCESSED_CSV_FOLDER, file_name))
    data['Example'].append(extract_averages(EXAMPLE_CSV_FOLDER, file_name))
    data['Explanation'].append(extract_averages(EXPLANATION_CSV_FOLDER, file_name))
    data['Lump'].append(extract_averages(PROCESSED_CSVS_LUMP_FOLDER, file_name))  # Extract for lump folder

# Convert the list of averages to DataFrames
processed_df = pd.DataFrame(data['Processed'], index=file_names)
example_df = pd.DataFrame(data['Example'], index=file_names)
explanation_df = pd.DataFrame(data['Explanation'], index=file_names)
lump_df = pd.DataFrame(data['Lump'], index=file_names)  # DataFrame for Lump folder

# Calculate the mean averages across centers for each approach
processed_mean = processed_df.mean()
example_mean = example_df.mean()
explanation_mean = explanation_df.mean()
lump_mean = lump_df.mean()  # Calculate mean for Lump

# Combine the averages for saving to a CSV file
averages_df = pd.DataFrame({
    'Processed': processed_mean,
    'Example': example_mean,
    'Explanation': explanation_mean,
    'Lump': lump_mean  # Add Lump averages
})

# Round the values to two decimal places
averages_df = averages_df.round(2)

averages_df.to_csv('average_scores.csv', index=True)

print("Averages saved to 'average_scores.csv'")
