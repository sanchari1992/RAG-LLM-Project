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

# Function to process each folder and save average rows to file
def save_averages_to_file(folder_path, folder_name):
    with open(f'{folder_name}_averages.csv', 'w') as f:
        for file_name in file_names:
            file_path = os.path.join(folder_path, file_name)
            averages = extract_averages(file_path)
            # Save averages with the file name prefix (e.g., example_csvs_alabama_psychiatry)
            f.write(f"{folder_name}_{file_name.split('.')[0]},{','.join(map(str, averages))}\n")

# Process each folder
save_averages_to_file(EXAMPLE_CSV_FOLDER, 'example_csvs')
save_averages_to_file(PROCESSED_CSV_FOLDER, 'processed_csvs')
save_averages_to_file(EXPLANATION_CSV_FOLDER, 'explanation_csvs')
save_averages_to_file(PROCESSED_CSVS_LUMP_FOLDER, 'processed_csvs_lump')

print("Averages saved in separate files for each folder.")
