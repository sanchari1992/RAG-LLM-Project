import os
import csv
import shutil
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
csv_folder = os.getenv("CSV_DATA_FOLDER")
output_folder = "processed_csvs"
openai_api_key = os.getenv("OPENAI_API_KEY")

# Set up the ChatGPT model
llm = ChatOpenAI(api_key=openai_api_key, model="gpt-3.5-turbo")

# Ensure output folder is empty at the start of each run
if os.path.exists(output_folder):
    shutil.rmtree(output_folder)
os.makedirs(output_folder, exist_ok=True)

# Define the prompt template
prompt_template = """
Analyze the following comment: "{comment}"
Score it on the following criteria between 1 and 5 (allowing decimals):
Ranking, Friendliness, General Rating, Flexibility, Ease of Scheduling, Affordability.
Provide your response as comma-separated values in this format:
"Ranking, Friendliness, General Rating, Flexibility, Ease of Scheduling, Affordability".
"""

# Process each CSV file in the folder
for filename in os.listdir(csv_folder):
    if filename.endswith(".csv"):
        input_file = os.path.join(csv_folder, filename)
        output_file = os.path.join(output_folder, f"processed_{filename}")
        
        # Read and process each CSV file
        with open(input_file, mode="r", encoding="utf-8") as infile, \
             open(output_file, mode="w", newline='', encoding="utf-8") as outfile:
            
            reader = csv.DictReader(infile)
            fieldnames = ["Name", "Ranking", "Friendliness", "General Rating", "Flexibility", "Ease of Scheduling", "Affordability"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for row in reader:
                comment = row["Comment"]
                name = row["Name"]
                
                # Format the prompt with the comment
                prompt = PromptTemplate(input_variables=["comment"], template=prompt_template).format(comment=comment)
                
                # Call ChatGPT to analyze the comment
                response = llm(prompt)
                
                # Parse the response into scores and ensure they are floats
                try:
                    scores = list(map(float, response.strip().split(',')))
                    ranking, friendliness, general_rating, flexibility, ease_of_scheduling, affordability = scores
                except ValueError:
                    # Handle unexpected format or parsing issues
                    print(f"Failed to parse scores for comment: {comment}")
                    continue
                
                # Write the processed data to the output CSV
                writer.writerow({
                    "Name": name,
                    "Ranking": ranking,
                    "Friendliness": friendliness,
                    "General Rating": general_rating,
                    "Flexibility": flexibility,
                    "Ease of Scheduling": ease_of_scheduling,
                    "Affordability": affordability
                })

print("Processing complete. Scored CSV files are in the 'processed_csvs' folder.")
