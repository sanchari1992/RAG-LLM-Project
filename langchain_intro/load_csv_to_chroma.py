import os
import shutil
import dotenv
from langchain.document_loaders.csv_loader import CSVLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document  # Import the Document class

# Load environment variables from .env
dotenv.load_dotenv()

# Paths for CSV files folder and Chroma persistence directory
CSV_DATA_FOLDER = os.getenv('CSV_DATA_FOLDER', './data')  # CSV folder path
CHROMA_PERSIST_PATH = "chroma_data"  # Chroma DB storage path

# Step 1: Delete the existing Chroma data to clear all prior documents
if os.path.exists(CHROMA_PERSIST_PATH):
    shutil.rmtree(CHROMA_PERSIST_PATH)  # Deletes the persistence directory and its contents
    print(f"Existing Chroma DB deleted at {CHROMA_PERSIST_PATH}")

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

# Step 3: Prepare documents for Chroma DB as `Document` objects
formatted_documents = []
for doc in all_documents:
    # Extract fields from the Document object
    content = doc.page_content  # This contains the text content of the document
    metadata = doc.metadata if hasattr(doc, 'metadata') else {}

    # Check if content is valid
    if not content.strip():
        print(f"Skipping empty content for metadata: {metadata}")
        continue

    # Debugging step: Print content and metadata before formatting
    print("\nLoaded Document Content:")
    print(content)
    print("Loaded Metadata:")
    print(metadata)

    # Create a Document object for Chroma with the actual content
    formatted_doc = Document(
        page_content=content,  # Use the actual review content
        metadata={
            'Counseling Center': metadata.get('Counseling Center', ''),
            'Name': metadata.get('Name', ''),
            'Rating': metadata.get('Rating', ''),
            'Year': metadata.get('Year', ''),
            'Comment': metadata.get('Comment', '')
        }
    )

    # Add the formatted document to the list
    formatted_documents.append(formatted_doc)

# Step 4: Initialize Chroma DB with OpenAI Embeddings and load all documents
print("\nStoring documents in ChromaDB...")
reviews_vector_db = Chroma.from_documents(
    formatted_documents,
    OpenAIEmbeddings(),
    persist_directory=CHROMA_PERSIST_PATH
)

# Step 5: Persist the new data to disk
reviews_vector_db.persist()

print("\nAll CSV files from the data folder have been successfully loaded into Chroma DB and previous data was cleared.")

# Step 6: Test retrieval from ChromaDB to verify stored data
retriever = reviews_vector_db.as_retriever(k=10)  # Retrieve top 10 results

# Try querying with a sample question
sample_query = "What do people say about counseling at Center A?"
print(f"\nQuerying ChromaDB with: '{sample_query}'")
results = retriever.get_relevant_documents(sample_query)

# Step 7: Print retrieved results to verify
print("\nRetrieved Results from ChromaDB:")
for result in results:
    print(result.page_content)  # This should print the actual stored review content

print("\nIf the above results are valid, the setup works correctly.")
