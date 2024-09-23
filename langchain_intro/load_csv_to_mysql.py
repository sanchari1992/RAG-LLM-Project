import os
import pandas as pd
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import glob

# Load environment variables from .env file
load_dotenv()

# Get MySQL connection details from .env
MYSQL_HOST = os.getenv('MYSQL_HOST')
MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE')

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

def load_csv_to_table(csv_file, connection):
    """Load a single CSV file into a MySQL table"""
    # Get table name from the CSV file name (without extension)
    table_name = os.path.splitext(os.path.basename(csv_file))[0]

    # Load CSV file into a pandas DataFrame
    df = pd.read_csv(csv_file)

    # Create MySQL table and insert data
    cursor = connection.cursor()
    try:
        # Create table if it doesn't exist
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            {', '.join([f'{col} LONGTEXT' if col == 'body' else f'{col} TEXT' for col in df.columns])}
        )
        """
        cursor.execute(create_table_query)
        
        # Insert data into table
        for _, row in df.iterrows():
            insert_query = f"INSERT INTO {table_name} VALUES ({', '.join(['%s'] * len(row))})"
            cursor.execute(insert_query, tuple(row))
        
        connection.commit()
        print(f"Data from {csv_file} successfully loaded into {table_name} table")

    except Error as e:
        print(f"Error while loading data into MySQL: {e}")

    finally:
        cursor.close()

def load_all_csvs_to_db(folder_path, connection):
    """Load all CSV files in a folder to MySQL tables"""
    csv_files = glob.glob(f"{folder_path}/*.csv")
    for csv_file in csv_files:
        load_csv_to_table(csv_file, connection)

if __name__ == "__main__":
    # Connect to MySQL
    connection = connect_to_mysql()
    
    if connection:
        # Define the folder containing your CSV files
        csv_folder = './csv_files/'
        
        # Load all CSV files into MySQL tables
        load_all_csvs_to_db(csv_folder, connection)
        
        # Close the MySQL connection
        connection.close()
