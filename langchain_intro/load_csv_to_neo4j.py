import os
import pandas as pd
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get Neo4j connection details from .env
NEO4J_URI = os.getenv('NEO4J_URI')
NEO4J_USERNAME = os.getenv('NEO4J_USERNAME')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')
CSV_DATA_FOLDER = os.getenv('CSV_DATA_FOLDER')  # Folder where CSV files are stored

class Neo4jLoader:
    def __init__(self, uri, user, password):
        """Initialize the Neo4j driver"""
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        """Close the Neo4j driver"""
        if self.driver:
            self.driver.close()

    def clear_database(self):
        """Clear all data from the Neo4j database"""
        with self.driver.session() as session:
            # Delete all nodes and relationships in the database
            session.run("MATCH (n) DETACH DELETE n")
            print("All existing data in the Neo4j database has been deleted.")

    def load_csv_to_neo4j(self, csv_file):
        """Load a single CSV file into Neo4j as nodes and relationships"""
        # Load CSV file into a pandas DataFrame and drop NaN values
        df = pd.read_csv(csv_file).dropna()

        with self.driver.session() as session:
            for _, row in df.iterrows():
                # Cypher query to create Counseling Center nodes and relationships
                query = """
                MERGE (center:CounselingCenter {name: $center_name})
                MERGE (person:Person {name: $person_name})
                CREATE (review:Review {
                    rating: $rating, 
                    review_year: $review_year, 
                    comment: $comment
                })
                MERGE (person)-[:WROTE]->(review)
                MERGE (review)-[:FOR]->(center)
                """
                session.run(query, 
                            center_name=row['Counseling Center'], 
                            person_name=row['Name'], 
                            rating=row['Rating'], 
                            review_year=row['Review Year'], 
                            comment=row['Comment'])
            print(f"Data from {csv_file} successfully loaded into Neo4j.")

    def create_indexes(self):
        """Create indexes on relevant fields for faster querying"""
        with self.driver.session() as session:
            # Create an index on 'CounselingCenter' names
            session.run("CREATE INDEX idx_center_name IF NOT EXISTS FOR (c:CounselingCenter) ON (c.name)")
            print("Index on 'Counseling Center' name created.")

            # Create an index on 'Person' names
            session.run("CREATE INDEX idx_person_name IF NOT EXISTS FOR (p:Person) ON (p.name)")
            print("Index on 'Person' name created.")

            # Create an index on 'Review' rating and review year
            session.run("CREATE INDEX idx_review_rating_year IF NOT EXISTS FOR (r:Review) ON (r.rating, r.review_year)")
            print("Index on 'Review' rating and review year created.")

def load_all_csvs_from_folder(data_folder, neo4j_loader):
    """Load all CSV files from the specified folder into Neo4j"""
    for csv_file in os.listdir(data_folder):
        if csv_file.endswith(".csv"):
            full_path = os.path.join(data_folder, csv_file)
            print(f"Processing file: {full_path}")
            neo4j_loader.load_csv_to_neo4j(full_path)

if __name__ == "__main__":
    # Initialize Neo4j loader
    neo4j_loader = Neo4jLoader(uri=NEO4J_URI, user=NEO4J_USERNAME, password=NEO4J_PASSWORD)

    try:
        # Clear all existing data from Neo4j database
        neo4j_loader.clear_database()

        # Load all CSV files from the data folder
        load_all_csvs_from_folder(CSV_DATA_FOLDER, neo4j_loader)

        # Create indexes for faster querying
        neo4j_loader.create_indexes()

    finally:
        # Close the Neo4j connection
        neo4j_loader.close()
