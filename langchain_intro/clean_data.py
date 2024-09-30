import pandas as pd
import re

# Load the CSV file into a DataFrame
df = pd.read_csv('./data/random_2000_rows.csv')

# Define a function to clean text by removing unreadable characters (like emojis)
def clean_text(text):
    # Replace any non-alphanumeric character (except spaces, punctuation) with an empty string
    clean_text = re.sub(r'[^a-zA-Z0-9\s.,?!]', '', text)
    return clean_text

# Apply the cleaning function to the 'content' column
df['content'] = df['content'].apply(lambda x: clean_text(str(x)))

# Drop rows with undefined (NaN) values in 'content' or 'score'
df = df.dropna(subset=['content', 'score'])

# Optionally, reset the index after dropping rows
df.reset_index(drop=True, inplace=True)

# Save the cleaned DataFrame back to a CSV file
df.to_csv('./data/cleaned_random_2000_rows.csv', index=False)

print("Data cleaned and saved to cleaned_random_2000_rows.csv")
