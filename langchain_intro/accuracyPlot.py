import pandas as pd

# Load the average_scores_combined.csv file
df = pd.read_csv('average_scores_combined.csv')

# Drop the "Response Time" column since we don’t need it for accuracy calculations
df = df.drop(columns=["Response Time"])

# Extract the "Ground Truth" row to use for accuracy calculation
ground_truth_row = df.iloc[0, 1:]  # All columns except "Data Loading"

# Initialize an empty DataFrame to store accuracy values
accuracy_df = pd.DataFrame(columns=df.columns[:-1])  # Exclude "Response Time" from columns

# Calculate accuracy for each row, except the "Ground Truth" row
for i in range(1, len(df)):
    row = df.iloc[i, 1:]  # Select only the numeric columns
    accuracy = row / ground_truth_row  # Calculate accuracy as a ratio to "Ground Truth"
    accuracy["Data Loading"] = df.iloc[i, 0]  # Add the "Data Loading" label
    accuracy_df = pd.concat([accuracy_df, pd.DataFrame([accuracy])], ignore_index=True)

# Round accuracy values to two decimal places
accuracy_df = accuracy_df.round(2)

# Save the accuracy DataFrame to a new file called accuracy.csv
accuracy_df.to_csv('accuracy.csv', index=False)

# Print the result for verification
print(accuracy_df)
