import os
import pandas as pd

# Set paths for the folders containing the CSV files
PROCESSED_CSV_FOLDER = './processed_csvs'
EXAMPLE_CSV_FOLDER = './example_csvs'
PROCESSED_CSVS_LUMP_FOLDER = './processed_csvs_lump'
EXPLANATION_CSV_FOLDER = './explanation_csvs'

# Names of the files to process (same file names across folders)
file_names = [
    'processed_Alabama_Psychiatry_Dataset.csv',
    'processed_Birmingham_Anxiety_Dataset.csv',
    'processed_Eastside_Mental_Health_Dataset.csv',
    'processed_Restorative_Counseling_Dataset.csv',
    'processed_Thriveworks_Counseling_Dataset.csv'
]

# Columns to plot for general processing (excluding Explanation columns)
columns_to_plot = ["Ranking", "Friendliness", "General Rating", "Flexibility", "Ease", "Affordability", "Response Time (s)"]

# Function to extract average values from the last row of each file
def extract_averages(file_path, columns_to_consider):
    df = pd.read_csv(file_path)
    # Print columns to verify column names
    print(f"Columns in {file_path}: {df.columns.tolist()}")
    
    # Get the last row, drop any columns with NaN values, and only keep relevant columns
    last_row = df.iloc[-1].dropna()
    existing_columns = [col for col in columns_to_consider if col in last_row.index]
    return last_row[existing_columns].astype(float)

# Function to process each folder and save average rows to file for general folders
def save_averages_to_file_general(folder_path, folder_name):
    with open(f'{folder_name}_averages.csv', 'w') as f:
        for file_name in file_names:
            file_path = os.path.join(folder_path, file_name)
            averages = extract_averages(file_path, columns_to_plot)
            # Save averages with the file name prefix (e.g., example_csvs_alabama_psychiatry)
            f.write(f"{folder_name}_{file_name.split('.')[0]},{','.join(map(str, averages))}\n")

# Function to process the explanation folder and save average rows to file
def save_averages_to_file_explanation(folder_path, folder_name):
    with open(f'{folder_name}_averages.csv', 'w') as f:
        for file_name in file_names:
            file_path = os.path.join(folder_path, file_name)
            averages = extract_averages(file_path, columns_to_plot)
            # Save averages with the file name prefix (e.g., explanation_csvs_alabama_psychiatry)
            f.write(f"{folder_name}_{file_name.split('.')[0]},{','.join(map(str, averages))}\n")

# Process general folders (EXAMPLE_CSV_FOLDER, PROCESSED_CSV_FOLDER, and PROCESSED_CSVS_LUMP_FOLDER)
save_averages_to_file_general(EXAMPLE_CSV_FOLDER, 'example_csvs')
save_averages_to_file_general(PROCESSED_CSV_FOLDER, 'processed_csvs')
save_averages_to_file_general(PROCESSED_CSVS_LUMP_FOLDER, 'processed_csvs_lump')

# Process the explanation folder separately
save_averages_to_file_explanation(EXPLANATION_CSV_FOLDER, 'explanation_csvs')

print("Averages saved in separate files for all folders.")
