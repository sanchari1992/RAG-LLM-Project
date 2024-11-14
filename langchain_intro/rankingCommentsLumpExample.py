import os
import csv
import logging
import time  # Import time module to track response times
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
import shutil

# Set up logging configuration
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()
CSV_DATA_FOLDER = os.getenv("CLEANED_CSV_FOLDER")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OUTPUT_FOLDER = "processed_lump_rated_csvs"

# Set up ChatOpenAI instance with your API key
chat = ChatOpenAI(api_key=OPENAI_API_KEY, model="gpt-3.5-turbo")

# Ensure output folder is empty at the start of each run
if os.path.exists(OUTPUT_FOLDER):
    shutil.rmtree(OUTPUT_FOLDER)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

BATCH_SIZE = 50  # Process 50 comments at a time

def format_comments_for_batch(batch):
    """
    Format multiple comments for a batch request to the LLM.
    """
    formatted_comments = []
    for i, row in enumerate(batch):
        name = row.get("Name", "Unknown")
        rating = row.get("Rating", "0")
        review_year = row.get("Review Year", "Unknown")
        current_year = 2024  # Adjust as needed or use datetime if needed dynamically
        years_ago = current_year - int(review_year) if review_year.isdigit() else "Unknown"
        comment = row.get("Comment", "")
        
        # Construct the formatted comment for each row
        formatted_comment = f"{i+1}. {name} {rating} stars {years_ago} years ago \"{comment}\""
        formatted_comments.append(formatted_comment)
    
    return "\n".join(formatted_comments)

def analyze_comments_batch(batch):
    """
    Send a batch of comments to ChatGPT and parse the response.
    """
    formatted_comments = format_comments_for_batch(batch)
    
    prompt = f"""
    Below is a list of comments. For each comment, please provide a rating from 1 to 5 for these categories:
    - Ranking
    - Friendliness
    - Rating (accept the numeral in the Rating column if it is provided)
    - Flexibility in scheduling
    - Ease of scheduling
    - Affordability

    Respond with each comment's results in the format:
    Comment #:
    Ranking
    Friendliness
    Rating
    Flexibility
    Ease
    Affordability

    If any information is missing, respond with "0" for that category. 

    Here are some examples of comments and their corresponding scores:

    Example 1:
    Comment: "Alabama Psychiatry and Counseling, Mellanie Herard, 4, 2024, love Dr. Whitt. 5 stars rating solely based on appointment having future appointments Dr. Rabbani."
    Scores:
    5
    4
    4
    4
    4
    0

    Example 2:
    Comment: "I had a terrible experience with the scheduling. The staff was rude, and I waited for over an hour."
    Scores:
    1
    1
    1
    1
    1
    0

    Example 3:
    Comment: "The service was great, and they offered flexible timings which helped me a lot."
    Scores:
    5
    5
    5
    5
    5
    4

    Comments:
    {formatted_comments}
    """
    try:
        # Start timing the GPT response
        start_time = time.time()
        
        # Sending the batch prompt and logging the response
        response = chat([HumanMessage(content=prompt)])
        
        # Calculate response time per row, rounded to two decimal places
        response_time = time.time() - start_time
        response_time_per_row = round(response_time / len(batch), 2)

        logging.debug(f"GPT Batch Response:\n{response.content}")

        # Parse response into structured data
        scores_data = []
        response_lines = response.content.strip().split('\n')
        current_score = {}

        for line in response_lines:
            line = line.strip()
            if line.startswith("Comment"):
                # If current_score is populated, append it to scores_data
                if current_score:
                    current_score["Response Time"] = response_time_per_row  # Add response time per row
                    scores_data.append(current_score)
                # Reset for the new comment
                current_score = {"Name": batch[len(scores_data)]["Name"]}  # Get name by index
            elif line:
                # Split the line by ": " to separate category from its score
                parts = line.split(": ")
                if len(parts) == 2:
                    category = parts[0].strip()
                    try:
                        score = float(parts[1]) if parts[1].isdigit() else 0.0
                    except ValueError:
                        score = 0.0
                    current_score[category] = score

        # Append the last comment score and add response time
        if current_score:
            current_score["Response Time"] = response_time_per_row
            scores_data.append(current_score)

        return scores_data

    except Exception as e:
        logging.error(f"Error parsing batch response: {e}")
        # Return zeroed data for all rows in case of an exception
        return [
            {
                "Name": row["Name"],
                "Ranking": 0.0,
                "Friendliness": 0.0,
                "Rating": 0.0,
                "Flexibility": 0.0,
                "Ease": 0.0,
                "Affordability": 0.0,
                "Response Time": 0.0,  # Add default 0 response time in case of error
            }
            for row in batch
        ]

def process_csv_files():
    for filename in os.listdir(CSV_DATA_FOLDER):
        if filename.endswith(".csv"):
            file_path = os.path.join(CSV_DATA_FOLDER, filename)
            with open(file_path, mode="r", encoding="utf-8") as csv_file:
                reader = csv.DictReader(csv_file)
                batch = []
                output_file_path = os.path.join(OUTPUT_FOLDER, f"processed_{filename}")

                # Set up output CSV with header
                with open(output_file_path, mode="w", newline="", encoding="utf-8") as output_file:
                    fieldnames = [
                        "Name",
                        "Ranking",
                        "Friendliness",
                        "Rating",
                        "Flexibility",
                        "Ease",
                        "Affordability",
                        "Response Time",  # New field for response time per row
                    ]
                    writer = csv.DictWriter(output_file, fieldnames=fieldnames)
                    writer.writeheader()

                    # Process each comment in batches
                    for row in reader:
                        batch.append(row)
                        if len(batch) == BATCH_SIZE:
                            scores_data = analyze_comments_batch(batch)
                            writer.writerows(scores_data)
                            batch.clear()  # Clear the batch after processing

                    # Process any remaining comments in the last batch
                    if batch:
                        scores_data = analyze_comments_batch(batch)
                        writer.writerows(scores_data)

                logging.info(f"Processed data saved to: {output_file_path}")
                
                # Modify column name from 'Rating' to 'General Rating'
                modify_column_name(output_file_path)

def modify_column_name(file_path):
    """
    Modify the column name 'Rating' to 'General Rating' in the processed CSV file.
    """
    temp_file_path = file_path + ".tmp"
    
    with open(file_path, mode="r", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        fieldnames = reader.fieldnames

        # Modify the 'Rating' column to 'General Rating'
        if 'Rating' in fieldnames:
            fieldnames[fieldnames.index('Rating')] = 'General Rating'
        
        with open(temp_file_path, mode="w", newline="", encoding="utf-8") as temp_file:
            writer = csv.DictWriter(temp_file, fieldnames=fieldnames)
            writer.writeheader()
            
            # Write rows with the new column name
            for row in reader:
                writer.writerow(row)

    # Replace original file with the modified one
    shutil.move(temp_file_path, file_path)
    logging.info(f"Column 'Rating' has been renamed to 'General Rating' in: {file_path}")

# Run the processing function
process_csv_files()
