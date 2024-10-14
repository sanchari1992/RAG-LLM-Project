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

# Function to load a single CSV file into MongoDB
def load_csv_to_mongodb(csv_file, collection_name):
    data = pd.read_csv(csv_file)
    records = []
    for _, row in data.iterrows():
        record = {
            "CounselingCenter": row['Counseling Center'],
            "Review": {
                "Name": row['Name'],
                "Rating": row['Rating'],
                "ReviewYear": row['Review Year'],
                "Comment": row['Comment']
            }
        }
        records.append(record)

    collection = db[collection_name]
    collection.insert_many(records)
    collection.create_index([("Review.Comment", "text")])
    print(f"Loaded {len(records)} records into {collection_name}.")


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
