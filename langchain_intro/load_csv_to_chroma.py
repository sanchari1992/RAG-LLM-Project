import os
import shutil
import dotenv
from langchain.document_loaders.csv_loader import CSVLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

# Load environment variables from .env
dotenv.load_dotenv()

# Paths for CSV files folder and Chroma persistence directory
CSV_DATA_FOLDER = os.getenv('CSV_DATA_FOLDER', './data')
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

        try:
            # Load the CSV file using CSVLoader with UTF-8 encoding
            loader_file = CSVLoader(file_path=full_path, encoding="utf-8")

            # Load documents from the CSV file
            data_file = loader_file.load()

            # Append the data to all_documents list
            all_documents.extend(data_file)

        except UnicodeDecodeError as e:
            print(f"Encoding error in file {full_path}: {e}")
        except RuntimeError as e:
            print(f"Error loading {full_path}: {e}")

# Step 3: Prepare documents for Chroma DB
formatted_documents = []
for doc in all_documents:
    # Extract fields from the Document object
    content = doc.page_content  # This contains the text content of the document
    # If the Document has metadata, you can access it using doc.metadata
    metadata = doc.metadata if hasattr(doc, 'metadata') else {}

    # Create a formatted document
    formatted_doc = {
        'Name': metadata.get('Name', ''),
        'Rating': metadata.get('Rating', ''),
        'Year': metadata.get('Year', ''),
        'Comment': metadata.get('Comment', ''),
        'text': f"Center: {metadata.get('Name', '')}, Rating: {metadata.get('Rating', '')}, Year: {metadata.get('Year', '')}, Comment: {metadata.get('Comment', '')}"
    }
    formatted_documents.append(formatted_doc)

# Step 4: Initialize Chroma DB with OpenAI Embeddings and load all documents
reviews_vector_db = Chroma.from_documents(
    formatted_documents,
    OpenAIEmbeddings(),
    persist_directory=CHROMA_PERSIST_PATH
)

# Step 5: Creating indexes on relevant fields for optimized querying
reviews_vector_db.create_index(fields=["Name"])  # Index for Name
reviews_vector_db.create_index(fields=["Rating"])  # Index for Rating
reviews_vector_db.create_index(fields=["Year"])  # Index for Year
reviews_vector_db.create_index(fields=["Comment"])  # Index for Comment

# Persist the new data to disk
reviews_vector_db.persist()

print("All CSV files from the data folder have been successfully loaded into Chroma DB, previous data was cleared, and indexes were created.")
