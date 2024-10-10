import os
import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from dotenv import load_dotenv

# Download the stopwords from nltk
nltk.download('punkt')
nltk.download('stopwords')

# Load environment variables from .env file if needed
load_dotenv()

# Define the folder paths
DATA_FOLDER = os.getenv('CSV_DATA_FOLDER')
CLEANED_DATA_FOLDER =os.getenv('CLEANED_CSV_FOLDER')  # Folder to store the cleaned CSV files

# Create the cleaned_data folder if it doesn't exist
if not os.path.exists(CLEANED_DATA_FOLDER):
    os.makedirs(CLEANED_DATA_FOLDER)

# Get stop words from NLTK
stop_words = set(stopwords.words('english'))

def clean_comment(comment):
    """Remove filler words (stopwords) from the comment and return the cleaned text."""
    # Tokenize the comment into words
    words = word_tokenize(comment)

    # Remove stopwords and join the remaining words back into a sentence
    cleaned_words = [word for word in words if word.lower() not in stop_words]

    return ' '.join(cleaned_words)

def clean_csv_file(csv_file):
    """Load a CSV file, clean the 'Comment' column, and save the cleaned file to the cleaned_data folder."""
    # Load the CSV file into a pandas DataFrame
    df = pd.read_csv(csv_file)

    # Check if 'Comment' column exists in the DataFrame
    if 'Comment' not in df.columns:
        print(f"'Comment' column not found in {csv_file}. Skipping this file.")
        return

    # Clean the 'Comment' column
    df['Comment'] = df['Comment'].apply(lambda x: clean_comment(str(x)))

    # Save the cleaned DataFrame to a new CSV file in the cleaned_data folder
    cleaned_csv_file = os.path.join(CLEANED_DATA_FOLDER, os.path.basename(csv_file))
    df.to_csv(cleaned_csv_file, index=False)
    print(f"Cleaned data saved to {cleaned_csv_file}")

def clean_all_csvs_in_folder(data_folder):
    """Process and clean all CSV files in the given folder."""
    for csv_file in os.listdir(data_folder):
        if csv_file.endswith(".csv"):
            full_path = os.path.join(data_folder, csv_file)
            print(f"Processing file: {full_path}")
            clean_csv_file(full_path)

if __name__ == "__main__":
    # Clean all CSV files in the data folder
    clean_all_csvs_in_folder(DATA_FOLDER)
