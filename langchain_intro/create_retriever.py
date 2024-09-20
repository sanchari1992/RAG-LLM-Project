import os
import shutil
import dotenv
from langchain.document_loaders.csv_loader import CSVLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

# Load environment variables from .env
dotenv.load_dotenv()

# Paths for CSV files and Chroma persistence directory
REVIEWS_CSV_PATH = "data/reviews.csv"
SPECS_CSV_PATH = "data/specs.csv"
CHROMA_PERSIST_PATH = "chroma_data"

# Step 1: Delete the existing Chroma data to clear all prior documents
if os.path.exists(CHROMA_PERSIST_PATH):
    shutil.rmtree(CHROMA_PERSIST_PATH)  # Deletes the persistence directory and its contents

# Step 2: Load the CSV files using CSVLoader
loader_reviews = CSVLoader(file_path=REVIEWS_CSV_PATH)
loader_specs = CSVLoader(file_path=SPECS_CSV_PATH)

# Step 3: Load documents from both CSV files
reviews = loader_reviews.load()
specs = loader_specs.load()

# Step 4: Initialize Chroma DB with OpenAI Embeddings and save both documents
reviews_vector_db = Chroma.from_documents(
    reviews + specs,  # Combine reviews and specs documents
    OpenAIEmbeddings(),
    persist_directory=CHROMA_PERSIST_PATH
)

# Persist the new data to disk
reviews_vector_db.persist()

print("CSV files have been successfully loaded into Chroma DB and previous data was cleared.")
