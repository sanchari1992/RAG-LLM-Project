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
        print(formatted_comment)
        formatted_comments.append(formatted_comment)
    
    # Join all formatted comments into a single prompt
    batch_prompt = "\n".join(formatted_comments)
    return batch_prompt

def analyze_comments_batch(df):
    """
    Send all comments in a CSV to ChatGPT as a batch and get scores for ranking, friendliness,
    general ratings, flexibility, ease, and affordability for each comment.
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

        # Parse response
        scores_data = {
            "Name": [],
            "Ranking": [],
            "Friendliness": [],
            "General Rating": [],
            "Flexibility": [],
            "Ease": [],
            "Affordability": []
        }

        # Process the response line by line
        response_lines = response.content.strip().split('\n')
        current_comment_index = -1

        for line in response_lines:
            if line.startswith("Comment"):
                current_comment_index += 1
                scores_data["Name"].append(df.iloc[current_comment_index]["Name"])
            elif current_comment_index >= 0:
                try:
                    # Convert line to float and add to respective score
                    score = float(line.strip())
                    category = list(scores_data.keys())[1:][(current_comment_index % 6)]
                    scores_data[category].append(score)
                except ValueError:
                    continue

        return scores_data

    except Exception as e:
        logging.error(f"Error parsing batch response: {e}")
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

            # Analyze all comments in the file in a single batch
            scores_data = analyze_comments_batch(df)
            
            # Save scores to a new CSV
            new_df = pd.DataFrame(scores_data)
            new_file_path = os.path.join(OUTPUT_FOLDER, f"processed_{filename}")
            new_df.to_csv(new_file_path, index=False)
            logging.info(f"Processed file saved as: {new_file_path}")

# Run the processing function
process_csv_files()
