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

# Function to calculate the aggregate of a row
def calculate_aggregate(row):
    return row.sum()

# Calculate aggregate for the ground truth file
ground_truth_df = pd.read_csv(ground_truth_file, header=None)
ground_truth_aggregate = calculate_aggregate(ground_truth_df.iloc[:, 1:].sum(axis=1))

# Dictionary to store results
aggregates = {"ground_truth": ground_truth_aggregate}

# Calculate aggregates for each folder
for folder in folders:
    folder_aggregate = 0
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
                    folder_aggregate += calculate_aggregate(avg_row.iloc[:, 1:-1].sum(axis=1))
                    file_count += 1

    # Average the folder aggregate if files exist
    if file_count > 0:
        aggregates[folder] = folder_aggregate / file_count
    else:
        aggregates[folder] = 0

# Save results to a CSV file
output_file = "aggregates_batches.csv"
results_df = pd.DataFrame(list(aggregates.items()), columns=["Dataset", "Aggregate Value"])
results_df.to_csv(output_file, index=False)

print(f"Aggregates saved to {output_file}")
