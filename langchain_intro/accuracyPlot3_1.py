import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Read the data
data = pd.read_csv("averages_batches.csv")

# Set ground truth as the baseline
ground_truth_value = data[data["Dataset"] == "ground_truth"]["Average Value"].values[0]

# Calculate accuracy (normalize deviations within range 0 to 1)
def calculate_accuracy(value, ground_truth):
    deviation = abs(value - ground_truth)
    return max(0, 1 - deviation / ground_truth)  # Ensure accuracy remains in [0, 1]

data["Accuracy"] = data["Average Value"].apply(lambda x: calculate_accuracy(x, ground_truth_value))

# Group datasets for easier plotting
datasets = {
    "Batch Size: 1": ["unprocessed_oneatatime_rated_csvs", "processed_oneatatime_rated_csvs"],
    "Batch Size: 10": ["unprocessed_lump10_rated_csvs", "processed_lump10_rated_csvs"],
    "Batch Size: 25": ["unprocessed_lump25_rated_csvs", "processed_lump25_rated_csvs"],
    "Batch Size: 50": ["unprocessed_lump_rated_csvs", "processed_lump_rated_csvs"],
    "Batch Size: 100": ["unprocessed_lump100_rated_csvs", "processed_lump100_rated_csvs"],
}

# Prepare the bar plot
labels = list(datasets.keys())
unprocessed_values = []
processed_values = []

for group in datasets.values():
    unprocessed = data[data["Dataset"] == group[0]]["Accuracy"].values
    processed = data[data["Dataset"] == group[1]]["Accuracy"].values
    
    # Ensure that values exist for the datasets
    unprocessed_values.append(unprocessed[0] if len(unprocessed) > 0 else 0)
    processed_values.append(processed[0] if len(processed) > 0 else 0)

x = np.arange(len(labels))  # Label locations
width = 0.35  # Width of bars

# Plotting
plt.figure(figsize=(10, 6))
plt.bar(x - width / 2, unprocessed_values, width, label="Unprocessed", color="#4c72b0", alpha=0.85, edgecolor="black")
plt.bar(x + width / 2, processed_values, width, label="Processed", color="#55a868", alpha=0.85, edgecolor="black")

# Add labels, title, and legend
plt.xlabel("Prompting Method")
plt.ylabel("Accuracy")
plt.title("Accuracy Comparison for Batch Prompting Methods with Different Batch Sizes")
plt.xticks(x, labels, rotation=45)
plt.ylim(0, 1)
plt.legend(loc="upper left")

# Add value annotations
for i, v in enumerate(unprocessed_values):
    plt.text(x[i] - width / 2, v + 0.02, f"{v:.2f}", ha="center", fontsize=8)
for i, v in enumerate(processed_values):
    plt.text(x[i] + width / 2, v + 0.02, f"{v:.2f}", ha="center", fontsize=8)

plt.tight_layout()
plt.show()
