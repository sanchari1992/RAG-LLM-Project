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
OUTPUT_FOLDER = "processed_csvs"

# Set up ChatOpenAI instance with your API key
chat = ChatOpenAI(api_key=OPENAI_API_KEY, model="gpt-3.5-turbo")

# Ensure output folder is empty at the start of each run
if os.path.exists(OUTPUT_FOLDER):
    shutil.rmtree(OUTPUT_FOLDER)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def analyze_comment(comment):
    """
    Send a comment to ChatGPT and get scores for ranking, friendliness,
    general ratings, flexibility, ease, and affordability.
    """
    prompt = f"""
    Please rate the following comment on a scale of 1 to 5 for these categories:
    - Ranking (1 to 5)
    - Friendliness (1 to 5)
    - General rating (1 to 5)
    - Flexibility in scheduling (1 to 5)
    - Ease of scheduling (1 to 5)
    - Affordability (1 to 5)

    Respond with only the numbers for each category, one per line, or "0" if a category is not mentioned in the comment.

    Comment: "{comment}"
    """
    
    try:
        # Sending the prompt and logging the response
        response = chat([HumanMessage(content=prompt)])
        logging.debug(f"GPT Response:\n{response.content}")

        # Split response by newlines and clean whitespace
        scores = response.content.strip().split('\n')
        
        # Ensure we have exactly 6 scores
        if len(scores) != 6:
            logging.warning("Unexpected number of scores received. Filling with zeros.")
            scores += ['0'] * (6 - len(scores))  # Fill missing scores with 0

        # Convert scores to float
        processed_scores = {
            "Ranking": float(scores[0]) if scores[0] else 0.0,
            "Friendliness": float(scores[1]) if scores[1] else 0.0,
            "General Rating": float(scores[2]) if scores[2] else 0.0,
            "Flexibility": float(scores[3]) if scores[3] else 0.0,
            "Ease": float(scores[4]) if scores[4] else 0.0,
            "Affordability": float(scores[5]) if scores[5] else 0.0
        }
        return processed_scores
    except Exception as e:
        logging.error(f"Error parsing response: {e}")
        return {
            "Ranking": 0.0,
            "Friendliness": 0.0,
            "General Rating": 0.0,
            "Flexibility": 0.0,
            "Ease": 0.0,
            "Affordability": 0.0
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
            
            scores_data = {
                "Name": [],
                "Ranking": [],
                "Friendliness": [],
                "General Rating": [],
                "Flexibility": [],
                "Ease": [],
                "Affordability": []
            }
            
            for _, row in df.iterrows():
                scores_data["Name"].append(row["Name"])
                scores = analyze_comment(row["Comment"])
                
                # Append each score to its respective list
                scores_data["Ranking"].append(scores.get("Ranking"))
                scores_data["Friendliness"].append(scores.get("Friendliness"))
                scores_data["General Rating"].append(scores.get("General Rating"))
                scores_data["Flexibility"].append(scores.get("Flexibility"))
                scores_data["Ease"].append(scores.get("Ease"))
                scores_data["Affordability"].append(scores.get("Affordability"))
            
            # Save scores to a new CSV
            new_df = pd.DataFrame(scores_data)
            new_file_path = os.path.join(OUTPUT_FOLDER, f"processed_{filename}")
            new_df.to_csv(new_file_path, index=False)
            logging.info(f"Processed file saved as: {new_file_path}")

# Run the processing function
process_csv_files()
