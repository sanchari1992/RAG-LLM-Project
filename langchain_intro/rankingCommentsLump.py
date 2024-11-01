import logging
import os
import pandas as pd
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

def format_comments_for_batch(df):
    """
    Format multiple comments for a batch request to the LLM.
    """
    formatted_comments = []
    for i, row in df.iterrows():
        name = row.get("Name", "Unknown")
        rating = row.get("Rating", "0")
        review_year = row.get("Review Year", "Unknown")
        current_year = pd.Timestamp.now().year
        years_ago = current_year - int(review_year) if pd.notnull(review_year) else "Unknown"
        comment = row.get("Comment", "")
        
        # Construct the formatted comment for each row
        formatted_comment = f"{i+1}. {name} {rating} stars {years_ago} years ago \"{comment}\""
        formatted_comments.append(formatted_comment)
    
    return "\n".join(formatted_comments)

def analyze_comments_batch(df):
    """
    Send a batch of comments to ChatGPT and parse the response.
    """
    formatted_comments = format_comments_for_batch(df)
    
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
        scores_data = {
            "Name": df["Name"].tolist(),
            "Ranking": [],
            "Friendliness": [],
            "General Rating": [],
            "Flexibility": [],
            "Ease": [],
            "Affordability": []
        }

        # Process response line by line
        response_lines = response.content.strip().split('\n')
        current_comment_index = -1

        for line in response_lines:
            line = line.strip()
            if line.startswith("Comment"):
                current_comment_index += 1
            elif line and current_comment_index >= 0:
                try:
                    score = float(line) if line.isdigit() else 0.0
                    category = list(scores_data.keys())[1:][(len(scores_data['Ranking']) - current_comment_index - 1) % 6]
                    scores_data[category].append(score)
                except ValueError:
                    logging.warning(f"Unable to convert score for {line} - adding 0.0 as placeholder.")
                    scores_data[category].append(0.0)
        
        # Normalize list lengths in scores_data
        for key in scores_data.keys():
            while len(scores_data[key]) < len(scores_data["Name"]):
                scores_data[key].append(0.0)

        return scores_data

    except Exception as e:
        logging.error(f"Error parsing batch response: {e}")
        # Return zeroed data for all rows in case of an exception
        return {
            "Name": df["Name"].tolist(),
            "Ranking": [0.0] * len(df),
            "Friendliness": [0.0] * len(df),
            "General Rating": [0.0] * len(df),
            "Flexibility": [0.0] * len(df),
            "Ease": [0.0] * len(df),
            "Affordability": [0.0] * len(df)
        }

def process_csv_files():
    for filename in os.listdir(CSV_DATA_FOLDER):
        if filename.endswith(".csv"):
            file_path = os.path.join(CSV_DATA_FOLDER, filename)
            df = pd.read_csv(file_path)
            
            # Ensure required columns are present
            if "Comment" not in df.columns or "Name" not in df.columns:
                logging.warning(f"Skipping {filename}: required columns missing.")
                continue

            output_file_path = os.path.join(OUTPUT_FOLDER, f"processed_{filename}")

            for start in range(0, len(df), BATCH_SIZE):
                batch_df = df.iloc[start:start + BATCH_SIZE]
                batch_scores = analyze_comments_batch(batch_df)
                
                # Convert batch_scores to DataFrame and save it immediately
                batch_df_result = pd.DataFrame(batch_scores)
                
                if not os.path.exists(output_file_path):
                    # Write header for the first batch
                    batch_df_result.to_csv(output_file_path, index=False, mode='w')
                else:
                    # Append without header for subsequent batches
                    batch_df_result.to_csv(output_file_path, index=False, mode='a', header=False)
                    
                logging.info(f"Processed batch saved to: {output_file_path}")

# Run the processing function
process_csv_files()
