import os
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
RATED_CSV_FOLDER = os.getenv("RATED_CSV_FOLDER")

def add_average_row_to_csv(file_path):
    """
    Add a row with averages to the CSV file.
    """
    df = pd.read_csv(file_path)
    
    # Calculate the averages of the numeric columns and round them to two decimal places
    averages = df.mean(numeric_only=True).round(2)
    
    # Create a new DataFrame for the average row
    average_row = pd.DataFrame({
        "Name": ["Average"],  # Name is set to "Average"
        **{col: [averages[col]] for col in averages.index}  # Average values for other columns
    })
    
    # Append the average row to the original DataFrame
    df_with_average = pd.concat([df, average_row], ignore_index=True)
    
    # Save the modified DataFrame back to the CSV file
    df_with_average.to_csv(file_path, index=False)
    print(f"Added average row to {file_path}")

def process_csv_files():
    """
    Process all CSV files in the specified directory to add average rows.
    """
    for filename in os.listdir(RATED_CSV_FOLDER):
        if filename.endswith(".csv"):
            file_path = os.path.join(RATED_CSV_FOLDER, filename)
            add_average_row_to_csv(file_path)

# Run the function to process CSV files
process_csv_files()
