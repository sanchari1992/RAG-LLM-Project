import os
import shutil
import dotenv
from langchain.document_loaders.csv_loader import CSVLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

# Load environment variables from .env
dotenv.load_dotenv()

# Paths for CSV files folder and Chroma persistence directory
CSV_DATA_FOLDER = os.getenv('CSV_DATA_FOLDER')
CHROMA_PERSIST_PATH = "chroma_data"

# Step 1: Delete the existing Chroma data to clear all prior documents
if os.path.exists(CHROMA_PERSIST_PATH):
    shutil.rmtree(CHROMA_PERSIST_PATH)  # Deletes the persistence directory and its contents

# Step 2: Load all CSV files from the data folder and aggregate documents
all_documents = []

for csv_file in os.listdir(CSV_DATA_FOLDER):
    if csv_file.endswith(".csv"):
        full_path = os.path.join(CSV_DATA_FOLDER, csv_file)
        print(f"Processing file: {full_path}")
        
        # Load the CSV file using CSVLoader
        loader_file = CSVLoader(file_path=full_path)
        
        # Load documents from the CSV file
        data_file = loader_file.load()
        
        # Append the data to all_documents list
        all_documents.extend(data_file)

# Step 3: Initialize Chroma DB with OpenAI Embeddings and load all documents
reviews_vector_db = Chroma.from_documents(
    all_documents,
    OpenAIEmbeddings(),
    persist_directory=CHROMA_PERSIST_PATH
)

# Persist the new data to disk
reviews_vector_db.persist()

print("All CSV files from the data folder have been successfully loaded into Chroma DB, and previous data was cleared.")
