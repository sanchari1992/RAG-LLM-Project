import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Read the data
data = pd.read_csv("averages.csv")

# Set ground truth as the baseline
ground_truth_value = data[data["Dataset"] == "ground_truth"]["Average Value"].values[0]

# Calculate accuracy (normalize deviations within range 0 to 1)
def calculate_accuracy(value, ground_truth):
    deviation = abs(value - ground_truth)
    return max(0, 1 - deviation / ground_truth)  # Ensure accuracy remains in [0, 1]

data["Accuracy"] = data["Average Value"].apply(lambda x: calculate_accuracy(x, ground_truth_value))

# Group datasets for easier plotting
datasets = {
    "One At A Time": ["unprocessed_oneatatime_rated_csvs", "processed_oneatatime_rated_csvs"],
    "Lump 10": ["unprocessed_lump10_rated_csvs", "processed_lump10_rated_csvs"],
    "Lump 25": ["unprocessed_lump25_rated_csvs", "processed_lump25_rated_csvs"],
    "Lump": ["unprocessed_lump_rated_csvs", "processed_lump_rated_csvs"],
    "Lump 100": ["unprocessed_lump100_rated_csvs", "processed_lump100_rated_csvs"],
}

# Prepare the bar plot
labels = list(datasets.keys())
unprocessed_values = [data[data["Dataset"] == d]["Accuracy"].values[0] for d in sum(datasets.values(), []) if "unprocessed" in d]
processed_values = [data[data["Dataset"] == d]["Accuracy"].values[0] for d in sum(datasets.values(), []) if "processed" in d]

x = np.arange(len(labels))  # Label locations
width = 0.35  # Width of bars

# Plotting
plt.figure(figsize=(10, 6))
plt.bar(x - width / 2, unprocessed_values, width, label="Unprocessed", color="skyblue")
plt.bar(x + width / 2, processed_values, width, label="Processed", color="orange")

# Add labels, title, and legend
plt.xlabel("Prompting Method")
plt.ylabel("Accuracy")
plt.title("Accuracy Comparison for Prompting Methods")
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
