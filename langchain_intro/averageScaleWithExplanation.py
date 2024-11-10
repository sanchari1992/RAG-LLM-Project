import os
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
PROCESSED_CSV_FOLDER = os.getenv("PROCESSED_EXPLANATION_CSV_FOLDER")

def add_average_row_to_csv(file_path):
    """
    Add a row with averages for specific columns to the CSV file, setting non-numeric columns to None for cleaner output.
    """
    # Read the CSV file
    df = pd.read_csv(file_path)
    
    # Specify only the columns needed for averaging
    numeric_columns = ["Ranking", "Friendliness", "General Rating", "Flexibility", "Ease", "Affordability", "Response Time"]
    
    # Calculate averages for the selected numeric columns and round them to two decimal places
    averages = df[numeric_columns].mean().round(2)
    
    # Create the average row with None for non-numeric columns
    average_row = {col: None for col in df.columns}  # Set all columns to None initially
    average_row.update({"Name": "Average"})          # Set "Name" column to "Average"
    average_row.update(averages.to_dict())           # Add calculated averages to numeric columns

    # Append the average row to the DataFrame
    df_with_average = pd.concat([df, pd.DataFrame([average_row])], ignore_index=True)
    
    # Save the modified DataFrame back to the CSV file
    df_with_average.to_csv(file_path, index=False)
    print(f"Added average row to {file_path}")

def process_csv_files():
    """
    Process all CSV files in the specified directory to add average rows.
    """
    for filename in os.listdir(PROCESSED_CSV_FOLDER):
        if filename.endswith(".csv"):
            file_path = os.path.join(PROCESSED_CSV_FOLDER, filename)
            add_average_row_to_csv(file_path)

# Run the function to process CSV files
process_csv_files()
