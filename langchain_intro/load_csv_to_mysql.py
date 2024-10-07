import os
import pandas as pd
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get MySQL connection details from .env
MYSQL_HOST = os.getenv('MYSQL_HOST')
MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE')
CSV_DATA_FOLDER = os.getenv('CSV_DATA_FOLDER')  # Folder where CSV files are stored

def connect_to_mysql():
    """Connect to MySQL database"""
    try:
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )
        if connection.is_connected():
            print("Successfully connected to MySQL database")
            return connection
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None

def drop_all_tables(connection):
    """Drop all tables in the current database"""
    cursor = connection.cursor()
    try:
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        for table in tables:
            drop_query = f"DROP TABLE IF EXISTS {table[0]}"
            cursor.execute(drop_query)
            print(f"Table {table[0]} dropped successfully.")
        connection.commit()
    except Error as e:
        print(f"Error while dropping tables: {e}")
    finally:
        cursor.close()

def load_csv_to_table(csv_file, connection):
    """Load a single CSV file into a MySQL table"""
    # Get table name from the CSV file name (without extension)
    table_name = os.path.splitext(os.path.basename(csv_file))[0]

    # Load CSV file into a pandas DataFrame and drop NaN values
    df = pd.read_csv(csv_file).dropna()  # Drop rows with NaN values

    # Create MySQL table and insert data
    cursor = connection.cursor()
    try:
        # Create table if it doesn't exist
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            Counseling_Center VARCHAR(255),
            Name VARCHAR(255) NOT NULL,
            Rating INT,
            Review_Year INT,
            Comment TEXT
        )
        """
        cursor.execute(create_table_query)
        
        # Insert data into table
        for _, row in df.iterrows():
            insert_query = f"INSERT INTO {table_name} VALUES ({', '.join(['%s'] * len(row))})"
            cursor.execute(insert_query, tuple(row))
        
        connection.commit()
        print(f"Data from {csv_file} successfully loaded into {table_name} table")

        # Create a full-text index on 'Comment' column
        cursor.execute(f"CREATE FULLTEXT INDEX idx_comment ON {table_name} (Comment);")
        print(f"Fulltext index on 'Comment' column created for {table_name}.")

        # Add index on 'Review_Year' column for faster queries
        if 'Review_Year' in df.columns:
            add_index_query = f"CREATE INDEX idx_review_year ON {table_name} (Review_Year);"
            cursor.execute(add_index_query)
            print(f"Index on 'Review_Year' column created for {table_name}.")

    except Error as e:
        print(f"Error while loading data into MySQL: {e}")

    finally:
        cursor.close()

def load_all_csvs_from_folder(data_folder, connection):
    """Load all CSV files from the specified folder into MySQL"""
    for csv_file in os.listdir(data_folder):
        if csv_file.endswith(".csv"):
            full_path = os.path.join(data_folder, csv_file)
            print(f"Processing file: {full_path}")
            load_csv_to_table(full_path, connection)

if __name__ == "__main__":
    # Connect to MySQL
    connection = connect_to_mysql()
    
    if connection:
        # Drop all existing tables in the database
        drop_all_tables(connection)

        # Load all CSV files from the data folder
        load_all_csvs_from_folder(CSV_DATA_FOLDER, connection)

        # Close the MySQL connection
        connection.close()
