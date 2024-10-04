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

# Function to get and print collection names
def get_collection_names():
    collection_names = db.list_collection_names()  # Retrieve the collection names
    print("Collections in the database:")
    for name in collection_names:
        print(f"- {name}")  # Print each collection name
    return collection_names

# Function to load a single CSV file into MongoDB
def load_csv_to_mongodb(csv_file, collection_name):
    # Drop the collection if it exists
    db[collection_name].drop()

    # Load data from CSV
    data = pd.read_csv(csv_file)
    records = data.to_dict(orient='records')  # Convert DataFrame to a list of dictionaries

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
    # Load all CSV files from the specified folder into MongoDB
    load_all_csvs_to_mongodb(csv_data_folder)

    # Get and print collection names
    get_collection_names()

    # Close the MongoDB client
    client.close()
