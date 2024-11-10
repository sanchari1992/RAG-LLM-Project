import os
import pandas as pd

# Set paths for the folders containing the CSV files
PROCESSED_CSV_FOLDER = './processed_csvs'
EXAMPLE_CSV_FOLDER = './example_csvs'
EXPLANATION_CSV_FOLDER = './explanation_csvs'
PROCESSED_CSVS_LUMP_FOLDER = './processed_csvs_lump'  # Add this folder

# Names of the files to process (same file names across folders)
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
def extract_averages(file_path):
    df = pd.read_csv(file_path)
    # Print columns to verify column names
    print(f"Columns in {file_path}: {df.columns.tolist()}")
    
    # Get the last row, drop any columns with NaN values, and only keep relevant columns
    last_row = df.iloc[-1].dropna()
    existing_columns = [col for col in columns_to_plot if col in last_row.index]
    return last_row[existing_columns].astype(float)

# Function to calculate and save averages for each folder
def calculate_and_save_folder_averages(folder_path, folder_name):
    averages = []
    for file_name in file_names:
        file_path = os.path.join(folder_path, file_name)
        averages.append(extract_averages(file_path))
    
    # Convert the list of averages to a DataFrame
    averages_df = pd.DataFrame(averages, index=file_names)
    
    # Calculate mean averages across all files in the folder
    mean_averages = averages_df.mean()
    
    # Save the averages to a CSV file
    mean_averages.to_csv(f'{folder_name}_mean_averages.csv', header=True)

# Calculate and save averages for each folder
calculate_and_save_folder_averages(EXAMPLE_CSV_FOLDER, 'example_csvs')
calculate_and_save_folder_averages(PROCESSED_CSV_FOLDER, 'processed_csvs')
calculate_and_save_folder_averages(EXPLANATION_CSV_FOLDER, 'explanation_csvs')
calculate_and_save_folder_averages(PROCESSED_CSVS_LUMP_FOLDER, 'processed_csvs_lump')

print("Mean averages saved in separate files for each folder.")
