import os
import pandas as pd
import shutil
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage

# Load environment variables
load_dotenv()
CSV_DATA_FOLDER = os.getenv("CSV_DATA_FOLDER")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Set up ChatOpenAI instance with your API key
chat = ChatOpenAI(api_key=OPENAI_API_KEY, model="gpt-3.5-turbo")

# Define the output folder
output_folder = "processed_csvs"

# Ensure the output folder is empty at the start of each run
if os.path.exists(output_folder):
    # Remove all files in the folder
    shutil.rmtree(output_folder)
os.makedirs(output_folder, exist_ok=True)

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
    Only return the rating number with new lines and no additional text. If you cannot rate it for any reason, give it a 0.

    For example, if the comment sent is 'The best literally changed me for the better.' the response should be '5\n0\n5\n0\n4\n5'.

    Comment: "{comment}"
    """
    
    try:
        response = chat([HumanMessage(content=prompt)])
        scores = response.content.split('\n')
        scores = {key: float(value.strip()) for key, value in 
                  (line.split(":") for line in scores if ':' in line)}
        return scores
    except Exception as e:
        print(f"Error parsing response: {e}")
        return {
            "Ranking": None,
            "Friendliness": None,
            "General Rating": None,
            "Flexibility": None,
            "Ease": None,
            "Affordability": None
        }

def process_csv_files():
    for filename in os.listdir(CSV_DATA_FOLDER):
        if filename.endswith(".csv"):
            file_path = os.path.join(CSV_DATA_FOLDER, filename)
            df = pd.read_csv(file_path)
            
            # Ensure required columns are present
            if "Comment" not in df.columns or "Name" not in df.columns:
                print(f"Skipping {filename}: required columns missing.")
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
            new_file_path = os.path.join(output_folder, f"processed_{filename}")
            new_df.to_csv(new_file_path, index=False)
            print(f"Processed file saved as: {new_file_path}")

# Run the processing function
process_csv_files()
