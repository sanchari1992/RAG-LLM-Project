import pandas as pd

# Load your CSV file into a DataFrame
df = pd.read_csv('./data/all_combined.csv')

# Select X random rows (replace X with the number of rows you want)
x = 2000  # Change this to the desired number of random rows
random_rows = df.sample(n=x)

# Optionally save the randomly selected rows to a new CSV file
random_rows.to_csv('./data/random_2000_rows.csv', index=False)
