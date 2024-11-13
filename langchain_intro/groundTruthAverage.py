import pandas as pd

# Load the ground_truth.csv file
ground_truth_df = pd.read_csv('ground_truth.csv', header=None)
# Assign column names for better readability
ground_truth_df.columns = ["Dataset", "Affordability", "Ease", "Flexibility", "Friendliness", "General Rating", "Ranking", "Response Time"]

# Calculate the averages for each column (excluding the first column)
ground_truth_averages = ground_truth_df.iloc[:, 1:].mean().round(2)

# Load the average_scores_combined.csv file
average_scores_combined_df = pd.read_csv('average_scores_combined.csv')

# Rename the first column to "Data Loading"
average_scores_combined_df.rename(columns={'Unnamed: 0': 'Data Loading'}, inplace=True)

# Create the new row with ground truth averages, named "Ground Truth"
new_row = pd.DataFrame([["Ground Truth"] + ground_truth_averages.tolist()], columns=average_scores_combined_df.columns)

# Insert the new row as the second row in the DataFrame
average_scores_combined_df = pd.concat([average_scores_combined_df.iloc[:1], new_row, average_scores_combined_df.iloc[1:]], ignore_index=True)

# Save the updated DataFrame back to average_scores_combined.csv
average_scores_combined_df.to_csv('average_scores_combined.csv', index=False)

# Print the updated DataFrame
print(average_scores_combined_df)
