import os
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
PROCESSED_CSV_FOLDER = os.getenv("PROCESSED_EXPLANATION_CSV_FOLDER")

def add_average_row_to_csv(file_path):
    """
    Add a row with averages for specific columns to the CSV file.
    """
    # Read the CSV file
    df = pd.read_csv(file_path)
    
    # Select only the columns needed for averaging
    numeric_columns = ["Ranking", "Friendliness", "General Rating", "Flexibility", "Ease", "Affordability"]
    df_numeric = df[numeric_columns]
    
    # Calculate averages for the selected columns and round them to two decimal places
    averages = df_numeric.mean().round(2)
    
    # Create a new DataFrame for the average row with "Name" set to "Average"
    average_row = pd.DataFrame({
        "Name": ["Average"],
        **{col: [averages[col]] for col in numeric_columns}
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
    for filename in os.listdir(PROCESSED_CSV_FOLDER):
        if filename.endswith(".csv"):
            file_path = os.path.join(PROCESSED_CSV_FOLDER, filename)
            add_average_row_to_csv(file_path)

# Run the function to process CSV files
process_csv_files()
