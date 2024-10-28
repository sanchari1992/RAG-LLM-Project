import os
import pandas as pd
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
CSV_DATA_FOLDER = os.getenv("CSV_DATA_FOLDER")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Set up OpenAI API key
openai.api_key = OPENAI_API_KEY

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

    Comment: "{comment}"
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "You are a helpful assistant."},
                  {"role": "user", "content": prompt}],
        max_tokens=100
    )
    
    try:
        scores = response['choices'][0]['message']['content'].split('\n')
        scores = {key: int(value.strip()) for key, value in 
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
            new_file_path = os.path.join("processed_csvs", f"processed_{filename}")
            new_df.to_csv(new_file_path, index=False)
            print(f"Processed file saved as: {new_file_path}")

# Ensure output folder exists
if not os.path.exists("processed_csvs"):
    os.makedirs("processed_csvs")

# Run the processing function
process_csv_files()
