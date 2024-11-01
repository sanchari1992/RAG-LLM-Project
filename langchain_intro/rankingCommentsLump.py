import os
import csv
import logging
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
import shutil

# Set up logging configuration
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()
CSV_DATA_FOLDER = os.getenv("CSV_DATA_FOLDER")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OUTPUT_FOLDER = "processed_csvs_lump"

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
    - General rating (accept the numeral in the Rating column if it is provided)
    - Flexibility in scheduling
    - Ease of scheduling
    - Affordability

    Respond with each comment's results in the format:
    Comment #:
    Ranking
    Friendliness
    General Rating
    Flexibility
    Ease
    Affordability

    If any information is missing, respond with "0" for that category. 

    Comments:
    {formatted_comments}
    """
    try:
        # Sending the batch prompt and logging the response
        response = chat([HumanMessage(content=prompt)])
        logging.debug(f"GPT Batch Response:\n{response.content}")

        # Parse response into structured data
        scores_data = []
        response_lines = response.content.strip().split('\n')
        current_score = {}
        current_comment_index = -1

        for line in response_lines:
            line = line.strip()
            if line.startswith("Comment"):
                if current_score:
                    scores_data.append(current_score)
                current_score = {"Name": batch[current_comment_index]["Name"]}
                current_comment_index += 1
            elif line:
                try:
                    # This assumes each line corresponds to a specific rating category in sequence
                    score = float(line) if line.isdigit() else 0.0
                    category = ["Ranking", "Friendliness", "General Rating", "Flexibility", "Ease", "Affordability"][
                        len(current_score) - 1
                    ]
                    current_score[category] = score
                except ValueError:
                    logging.warning(f"Unable to parse score for {line}, using 0.0 as a placeholder.")
                    current_score[category] = 0.0

        if current_score:
            print(current_score)
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
                "General Rating": 0.0,
                "Flexibility": 0.0,
                "Ease": 0.0,
                "Affordability": 0.0,
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
                        "General Rating",
                        "Flexibility",
                        "Ease",
                        "Affordability",
                    ]
                    writer = csv.DictWriter(output_file, fieldnames=fieldnames)
                    writer.writeheader()

                    # Process each comment in batches
                    for row in reader:
                        batch.append(row)
                        if len(batch) == BATCH_SIZE:
                            scores_data = analyze_comments_batch(batch)
                            writer.writerows(scores_data)
                            batch.clear()

                    # Process any remaining comments in the last batch
                    if batch:
                        scores_data = analyze_comments_batch(batch)
                        writer.writerows(scores_data)

                logging.info(f"Processed data saved to: {output_file_path}")

# Run the processing function
process_csv_files()
