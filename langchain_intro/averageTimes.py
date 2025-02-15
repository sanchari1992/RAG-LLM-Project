import os
import pandas as pd
import numpy as np

# Define folder paths
base_path = "/Users/sanchari/Documents/GitHub/RAG-LLM-PROJECT"
folders = {
    "Single Prompting": ["unprocessed_oneatatime_rated_csvs", "processed_oneatatime_rated_csvs"],
    "Batch Prompting (10)": ["unprocessed_lump10_rated_csvs", "processed_lump10_rated_csvs"],
    "Batch Prompting (25)": ["./unprocessed_lump25_rated_csvs", "processed_lump25_rated_csvs"],
    "Batch Prompting (50)": ["unprocessed_lump_rated_csvs", "processed_lump_rated_csvs"],
    "Batch Prompting (100)": ["unprocessed_lump100_rated_csvs", "processed_lump100_rated_csvs"],
    "Prompting with Examples": ["unprocessed_lump_example_rated_csvs", "processed_lump_example_rated_csvs"],
    "Prompting with Explanations": ["unprocessed_lump_explanation_rated_csvs", "processed_lump_explanation_rated_csvs"],
}

def calculate_runtime(folder_path):
    """Calculate the average and standard deviation of response times for all CSV files in a folder."""
    response_times = []
    
    for file in os.listdir(folder_path):
        if file.endswith(".csv"):
            df = pd.read_csv(os.path.join(folder_path, file))
            response_times.extend(df["Response Time"].tolist())
    
    if response_times:
        avg_time = np.mean(response_times)
        std_dev = np.std(response_times)
        return round(avg_time, 2), round(std_dev, 2)
    else:
        return None, None

# Collect results
results_unprocessed = []
results_processed = []

for strategy, (unprocessed_folder, processed_folder) in folders.items():
    unprocessed_path = os.path.join(base_path, unprocessed_folder)
    processed_path = os.path.join(base_path, processed_folder)
    
    avg_unprocessed, std_unprocessed = calculate_runtime(unprocessed_path)
    avg_processed, std_processed = calculate_runtime(processed_path)
    
    results_unprocessed.append([strategy, avg_unprocessed, std_unprocessed])
    results_processed.append([strategy, avg_processed, std_processed])

# Convert results to DataFrame
columns = ["Prompting Strategy", "Average Query Time (seconds)", "Standard Deviation (seconds)"]
df_unprocessed = pd.DataFrame(results_unprocessed, columns=columns)
df_processed = pd.DataFrame(results_processed, columns=columns)

# Display tables
print("Unprocessed Data Runtime Analysis:")
print(df_unprocessed.to_string(index=False))

print("\nProcessed Data Runtime Analysis:")
print(df_processed.to_string(index=False))
