import os
import pandas as pd
import matplotlib.pyplot as plt

# Paths to folders
folders = {
    "Unprocessed Lump": "./unprocessed_lump_rated_csvs",
    "Processed Lump": "./processed_lump_rated_csvs",
    "Unprocessed Lump Example": "./unprocessed_lump_example_rated_csvs",
    "Processed Lump Example": "./processed_lump_example_rated_csvs",
    "Unprocessed Lump Explanation": "./unprocessed_lump_explanation_rated_csvs",
    "Processed Lump Explanation": "./processed_lump_explanation_rated_csvs"
}

# Path to ground truth file
ground_truth_file = "./ground_truth.csv"

# Function to calculate the overall average from the "Average" row in CSVs
def calculate_overall_average(folder_path):
    overall_averages = []
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        df = pd.read_csv(file_path)

        # Check if both "Ranking" and "Friendliness" columns exist
        if "Ranking" not in df.columns or "Friendliness" not in df.columns:
            print(f"Skipping {file_name} due to missing columns.")
            continue

        # Handle files with "Rating" or "General Rating" columns
        rating_column = "General Rating" if "General Rating" in df.columns else "Rating"
        necessary_columns = ["Ranking", "Friendliness", rating_column, "Flexibility", "Ease", "Affordability"]

        # Filter to keep only necessary columns if present
        filtered_df = df[necessary_columns].copy()

        # Check if 'Name' column exists to filter for the "Average" row
        if 'Name' in df.columns:
            avg_row = filtered_df[df["Name"] == "Average"]
        else:
            avg_row = filtered_df.mean(axis=0)

        # Calculate mean if "Average" row is present
        if not avg_row.empty:
            # For rows containing "Average," calculate the row mean
            overall_avg = avg_row.mean(axis=1).values[0] if 'Name' in df.columns else avg_row.mean()
            overall_averages.append(overall_avg)

    # Return the mean of all files in the folder
    return sum(overall_averages) / len(overall_averages) if overall_averages else 0

# Calculate the ground truth overall average
ground_truth_df = pd.read_csv(ground_truth_file, header=None)
ground_truth_avg_row = ground_truth_df.iloc[:, 1:-1].mean(axis=1).values[0]

# Dictionary to store overall averages
overall_averages = {"Ground Truth": ground_truth_avg_row}

# Calculate overall averages for each folder
for label, folder_path in folders.items():
    overall_averages[label] = calculate_overall_average(folder_path)

# Save results to plotdata2.csv
plotdata_df = pd.DataFrame(list(overall_averages.items()), columns=["Data Loading", "Overall Average"])
plotdata_df.to_csv("plotdata2.csv", index=False)

# Calculate accuracy based on ground truth
ground_truth_avg = overall_averages["Ground Truth"]
accuracy_scores = {
    label: min(1, avg / ground_truth_avg) if ground_truth_avg != 0 else 0
    for label, avg in overall_averages.items() if label != "Ground Truth"
}

# Plot accuracy as a bar graph
labels = list(accuracy_scores.keys())
accuracy_values = list(accuracy_scores.values())

# Use ggplot style for better aesthetics
plt.style.use("ggplot")
plt.figure(figsize=(12, 8))

# Create the bar plot
bars = plt.bar(labels, accuracy_values, color=["#4c72b0", "#55a868", "#c44e52", "#8172b3", "#64b5f6", "#ff7043"], alpha=0.85, edgecolor="black")

# Add title and labels with enhanced fonts
plt.title("Accuracy Based on Ground Truth", fontsize=16, fontweight="bold", pad=20)
plt.xlabel("Data Loading Method", fontsize=14, labelpad=10)
plt.ylabel("Accuracy", fontsize=14, labelpad=10)

# Add gridlines for better readability
plt.grid(axis="y", linestyle="--", alpha=0.7)

# Annotate accuracy values on top of the bars
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width() / 2, yval + 0.02, f"{yval:.2f}", ha="center", fontsize=12, fontweight="medium")

# Set axis limits and ticks
plt.ylim(0, 1.1)  # Extend slightly beyond 1 for better visibility of annotations
plt.xticks(rotation=45, fontsize=12)
plt.yticks(fontsize=12)

# Save the figure as a high-resolution image
plt.tight_layout()
plt.savefig("accuracy_plot2.png", dpi=300)  # Save as PNG for high-quality research paper graphics

# Display the plot
plt.show()
