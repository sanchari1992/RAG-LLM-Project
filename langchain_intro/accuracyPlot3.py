import os
import pandas as pd

# Define paths
ground_truth_file = "ground_truth.csv"
folders = [
    "unprocessed_oneatatime_rated_csvs",
    "unprocessed_lump10_rated_csvs",
    "unprocessed_lump25_rated_csvs",
    "unprocessed_lump_rated_csvs",
    "unprocessed_lump100_rated_csvs",
    "processed_oneatatime_rated_csvs",
    "processed_lump10_rated_csvs",
    "processed_lump25_rated_csvs",
    "processed_lump_rated_csvs",
    "processed_lump100_rated_csvs",
]

# Function to calculate the average of a row
def calculate_average(row):
    return row.mean()

# Calculate average for the ground truth file
ground_truth_df = pd.read_csv(ground_truth_file, header=None)
ground_truth_average = round(calculate_average(ground_truth_df.iloc[:, 1:].mean(axis=1)), 2)

# Dictionary to store results
averages = {"ground_truth": ground_truth_average}

# Calculate averages for each folder
for folder in folders:
    folder_average = 0
    folder_path = os.path.join(folder)
    file_count = 0

    if os.path.exists(folder_path):
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            if file_name.endswith(".csv"):
                df = pd.read_csv(file_path)
                
                # Ensure "Average" row exists
                avg_row = df[df["Name"] == "Average"]
                if not avg_row.empty:
                    # Calculate the average of the "Average" row (excluding Response Time)
                    row_average = avg_row.iloc[:, 1:-1].mean(axis=1).values[0]
                    folder_average += row_average
                    file_count += 1

    # Average the folder's results if files exist
    if file_count > 0:
        averages[folder] = round(folder_average / file_count, 2)
    else:
        averages[folder] = 0.00

# Save results to a CSV file
output_file = "averages_batches.csv"
results_df = pd.DataFrame(list(averages.items()), columns=["Dataset", "Average Value"])
results_df.to_csv(output_file, index=False)

print(f"Averages saved to {output_file}")
