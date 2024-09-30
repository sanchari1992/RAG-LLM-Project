import os
import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection
mongodb_uri = os.getenv('MONGODB_URI')
database_name = os.getenv('DATABASE_NAME')
reviews_collection_name = os.getenv('REVIEWS_COLLECTION')

# Create a MongoDB client
client = MongoClient(mongodb_uri)
db = client[database_name]

# Function to load CSV to MongoDB
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
    
    # Add indexing on key fields
    # You can create indexes on multiple fields based on your query patterns
    collection.create_index([("reviewId", 1)])  # Ascending index on reviewId
    collection.create_index([("app", 1)])       # Ascending index on app
    collection.create_index([("score", 1)])     # Ascending index on score
    
    print("Indexes have been created on reviewId, app, and score fields.")

# File paths
reviews_file = os.getenv('CSV_FILE')

# Load the CSV files into MongoDB
load_csv_to_mongodb(reviews_file, reviews_collection_name)

# Close the MongoDB client
client.close()
