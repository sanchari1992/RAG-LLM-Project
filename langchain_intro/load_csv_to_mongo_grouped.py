import os
import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection details from .env
mongodb_uri = os.getenv('MONGODB_URI')
database_name = os.getenv('DATABASE_NAME')
csv_data_folder = os.getenv('CSV_DATA_FOLDER')  # Folder where CSV files are stored

# Create a MongoDB client
client = MongoClient(mongodb_uri)
db = client[database_name]

# Function to drop all collections in the database
def drop_all_collections():
    collection_names = db.list_collection_names()  # Get all collection names
    for collection_name in collection_names:
        db[collection_name].drop()  # Drop each collection
        print(f"Dropped collection: {collection_name}")

# Function to categorize ratings
def categorize_rating(rating):
    if rating in [1, 2]:
        return "bad"
    elif rating == 3:
        return "neutral"
    elif rating in [4, 5]:
        return "good"
    else:
        return "unknown"  # In case of unexpected rating

# Function to load a single CSV file into MongoDB
def load_csv_to_mongodb(csv_file, collection_name):
    # Load data from CSV
    data = pd.read_csv(csv_file)

    # Check if 'Rating' column exists and categorize ratings
    if 'Rating' not in data.columns:
        print("Error: 'Rating' column not found in the CSV.")
        return
    
    # Add a new column 'Rating Category' based on the existing 'Rating' column
    data['Rating Category'] = data['Rating'].apply(categorize_rating)

    # Convert DataFrame to a list of dictionaries
    records = data.to_dict(orient='records')

    # Insert the records into MongoDB
    collection = db[collection_name]
    collection.insert_many(records)  # Insert the records into MongoDB
    print(f"Loaded {len(records)} records into {collection_name}.")

    # Add a text index on the 'Comment' field for full-text search
    collection.create_index([("Comment", "text")])  # Create a text index on the Comment field
    print(f"Text index created on the 'Comment' field.")

# Function to load all CSV files from the folder into MongoDB
def load_all_csvs_to_mongodb(data_folder):
    for csv_file in os.listdir(data_folder):
        if csv_file.endswith(".csv"):
            full_path = os.path.join(data_folder, csv_file)
            collection_name = os.path.splitext(csv_file)[0]  # Use file name (without extension) as collection name
            print(f"Processing file: {full_path}")
            load_csv_to_mongodb(full_path, collection_name)

if __name__ == "__main__":
    # Drop all collections in the database before loading new data
    drop_all_collections()

    # Load all CSV files from the specified folder into MongoDB
    load_all_csvs_to_mongodb(csv_data_folder)

    # Close the MongoDB client
    client.close()
