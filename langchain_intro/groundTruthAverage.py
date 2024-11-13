import pandas as pd

# Load the CSV file
file_path = './ground_truth.csv'
df = pd.read_csv(file_path, header=None)

# Set column names for better readability
df.columns = ["Dataset", "Affordability", "Ease", "Flexibility", "Friendliness", "General Rating", "Ranking", "Response Time"]

# Calculate the average of each column (excluding the first column)
averages = df.iloc[:, 1:].mean()

# Create a new DataFrame for the averages
average_row = pd.DataFrame([["ground_truth"] + averages.tolist()], columns=df.columns)

# Append the average row to the original DataFrame
df_with_average = pd.concat([df, average_row], ignore_index=True)

# Save to a new CSV or print the output
print(df_with_average)
# Optionally, save to a new CSV file
df_with_average.to_csv('ground_truth_with_averages.csv', index=False)

# Print the average row for reference
print(average_row)
