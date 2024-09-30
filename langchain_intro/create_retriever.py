import os
import shutil
import dotenv
from langchain.document_loaders.csv_loader import CSVLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

# Load environment variables from .env
dotenv.load_dotenv()

# Paths for CSV files and Chroma persistence directory
# REVIEWS_CSV_PATH = "data/reviews.csv"
# SPECS_CSV_PATH = "data/specs.csv"
CSV_FILE = os.getenv('CSV_FILE')
CHROMA_PERSIST_PATH = "chroma_data"

# Step 1: Delete the existing Chroma data to clear all prior documents
if os.path.exists(CHROMA_PERSIST_PATH):
    shutil.rmtree(CHROMA_PERSIST_PATH)  # Deletes the persistence directory and its contents

# Step 2: Load the CSV file using CSVLoader
loader_file = CSVLoader(file_path=CSV_FILE)

# Step 3: Load documents from the CSV file
data_file = loader_file.load()

# Step 4: Initialize Chroma DB with OpenAI Embeddings and save both documents
reviews_vector_db = Chroma.from_documents(
    data_file,
    OpenAIEmbeddings(),
    persist_directory=CHROMA_PERSIST_PATH
)

# Persist the new data to disk
reviews_vector_db.persist()

print("CSV files have been successfully loaded into Chroma DB and previous data was cleared.")
