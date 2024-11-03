import logging
import os
import pandas as pd
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
import shutil

# Set up logging configuration
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()
CSV_DATA_FOLDER = os.getenv("CSV_DATA_FOLDER")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OUTPUT_FOLDER = "explanation_csvs"

# Set up ChatOpenAI instance with your API key
chat = ChatOpenAI(api_key=OPENAI_API_KEY, model="gpt-3.5-turbo")

# Ensure output folder is empty at the start of each run
if os.path.exists(OUTPUT_FOLDER):
    shutil.rmtree(OUTPUT_FOLDER)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Mapping for expected category names
CATEGORY_MAPPING = {
    "Ranking": "Ranking",
    "Friendliness": "Friendliness",
    "General Rating": "General Rating",
    "Flexibility in scheduling": "Flexibility",
    "Ease of scheduling": "Ease",
    "Affordability": "Affordability"
}

def format_comment(row):
    """
    Format the comment to include name, rating, and years ago.
    """
    name = row.get("Name", "Unknown")
    rating = row.get("Rating", "0")
    review_year = row.get("Review Year", "Unknown")
    current_year = pd.Timestamp.now().year
    years_ago = current_year - int(review_year) if pd.notnull(review_year) else "Unknown"
    comment = row.get("Comment", "")
    
    # Construct the formatted comment
    formatted_comment = f"{name} {rating} stars {years_ago} years ago \"{comment}\""
    return formatted_comment

def analyze_comment(row):
    """
    Send a formatted comment to ChatGPT and get scores and explanations for ranking, friendliness,
    general ratings, flexibility, ease, and affordability.
    """
    formatted_comment = format_comment(row)
    
    prompt = f"""
    Please rate the following comment on a scale of 1 to 5 for these categories and provide a brief explanation for each rating:
    - Ranking (1 to 5)
    - Friendliness (1 to 5)
    - General rating (1 to 5) (Accept the numeral in the Rating column if available)
    - Flexibility in scheduling (1 to 5)
    - Ease of scheduling (1 to 5)
    - Affordability (1 to 5)

    Respond with each category's rating followed by a brief justification. Example response format:
    Ranking: 5 - The reviewer speaks highly of the service.
    Friendliness: 4 - The reviewer mentions a friendly staff.
    General Rating: 4 - The rating is 4 stars based on the review.
    Flexibility: 3 - The reviewer mentions minor scheduling issues.
    Ease: 4 - Scheduling was straightforward according to the reviewer.
    Affordability: 2 - There was a comment about high prices.

    Comment: "{formatted_comment}"
    """
    
    try:
        # Sending the prompt and logging the response
        response = chat([HumanMessage(content=prompt)])
        logging.debug(f"GPT Response:\n{response.content}")

        # Split response by newlines and clean whitespace
        response_lines = response.content.strip().split('\n')
        
        # Initialize dictionaries for scores and explanations
        scores = {}
        explanations = {}

        # Parse response line by line
        for line in response_lines:
            if ": " in line:
                category, detail = line.split(": ", 1)
                parts = detail.split(" - ", 1)
                
                # Map the GPT category to our standard category names
                mapped_category = CATEGORY_MAPPING.get(category.strip(), None)
                
                if mapped_category:
                    # Extract score and explanation
                    score = float(parts[0]) if parts[0].isdigit() else 0.0
                    explanation = parts[1] if len(parts) > 1 else "No explanation provided."

                    # Populate scores and explanations
                    scores[mapped_category] = score
                    explanations[mapped_category] = explanation

        # Ensure we have values for all categories
        for category in CATEGORY_MAPPING.values():
            if category not in scores:
                scores[category] = 0.0
                explanations[category] = "No explanation provided."

        return scores, explanations

    except Exception as e:
        logging.error(f"Error parsing response: {e}")
        # Return zeros and default explanations in case of an exception
        return (
            {category: 0.0 for category in CATEGORY_MAPPING.values()},
            {category: "No explanation provided." for category in CATEGORY_MAPPING.values()}
        )

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
                "Ranking Explanation": [],
                "Friendliness": [],
                "Friendliness Explanation": [],
                "General Rating": [],
                "General Rating Explanation": [],
                "Flexibility": [],
                "Flexibility Explanation": [],
                "Ease": [],
                "Ease Explanation": [],
                "Affordability": [],
                "Affordability Explanation": []
            }
            
            for _, row in df.iterrows():
                scores_data["Name"].append(row["Name"])
                scores, explanations = analyze_comment(row)
                
                # Append each score and explanation to their respective lists
                for category in scores:
                    scores_data[category].append(scores[category])
                    scores_data[f"{category} Explanation"].append(explanations[category])
            
            # Save scores and explanations to a new CSV
            new_df = pd.DataFrame(scores_data)
            new_file_path = os.path.join(OUTPUT_FOLDER, f"processed_{filename}")
            new_df.to_csv(new_file_path, index=False)
            logging.info(f"Processed file saved as: {new_file_path}")

# Run the processing function
process_csv_files()
