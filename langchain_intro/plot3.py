import os
import pandas as pd
import matplotlib.pyplot as plt

# Set paths for the folders containing the CSV files with averages
EXAMPLE_CSVS_AVERAGES_FILE = './example_csvs_averages.csv'
PROCESSED_CSVS_AVERAGES_FILE = './processed_csvs_averages.csv'
EXPLANATION_CSVS_AVERAGES_FILE = './explanation_csvs_averages.csv'
PROCESSED_CSVS_LUMP_AVERAGES_FILE = './processed_csvs_lump_averages.csv'

# Load the ground truth CSV file
ground_truth_file = './ground_truth.csv'
ground_truth_df = pd.read_csv(ground_truth_file)

# Columns for the attributes
columns_to_plot = ["Ranking", "Friendliness", "General Rating", "Flexibility", "Ease", "Affordability", "Response Time"]

# Function to read and process the average CSV files
def process_averages_file(file_path):
    df = pd.read_csv(file_path, header=None)
    df.columns = ['File', 'Affordability', 'Ease', 'Flexibility', 'Friendliness', 'General Rating', 'Ranking', 'Response Time']
    df.set_index('File', inplace=True)
    return df

# Read the averages from the CSV files generated in the previous step
example_df = process_averages_file(EXAMPLE_CSVS_AVERAGES_FILE)
processed_df = process_averages_file(PROCESSED_CSVS_AVERAGES_FILE)
explanation_df = process_averages_file(EXPLANATION_CSVS_AVERAGES_FILE)
lump_df = process_averages_file(PROCESSED_CSVS_LUMP_AVERAGES_FILE)

# Function to plot the data for each mental health center
def plot_data_for_center(center_name, ground_truth_df, example_df, processed_df, explanation_df, lump_df):
    # Extract data for the specific mental health center by matching the full name from ground_truth
    ground_truth_name = f'ground_truth_{center_name}_Dataset'  # Full name in ground truth
    center_gt = ground_truth_df[ground_truth_df['Name'] == ground_truth_name]
    
    if center_gt.empty:
        print(f"Ground truth not found for {center_name}")
        return

    # Extract the averages for the center from each CSV
    center_example = example_df.loc[f'explanation_csvs_processed_{center_name}']
    center_processed = processed_df.loc[f'explanation_csvs_processed_{center_name}']
    center_explanation = explanation_df.loc[f'explanation_csvs_processed_{center_name}']
    center_lump = lump_df.loc[f'explanation_csvs_processed_{center_name}']

    # Create a DataFrame for plotting
    plot_df = pd.DataFrame({
        'Ground Truth': center_gt[columns_to_plot].values.flatten(),
        'Example': center_example[columns_to_plot].values.flatten(),
        'Processed': center_processed[columns_to_plot].values.flatten(),
        'Explanation': center_explanation[columns_to_plot].values.flatten(),
        'Lump': center_lump[columns_to_plot].values.flatten()
    }, index=columns_to_plot)

    # Plotting the data
    plot_df.plot(kind='bar', figsize=(10, 6))

    # Adding a title and labels
    plt.title(f'Comparison of Average Scores for {center_name}')
    plt.xlabel('Metrics')
    plt.ylabel('Average Score')

    # Customize the legend title and rotation for clarity
    plt.legend(title='Approach')

    # Rotate the x-axis labels for better readability
    plt.xticks(rotation=45)

    # Adjust layout to prevent clipping of labels
    plt.tight_layout()

    # Show the plot
    plt.show()

# List of centers to plot
center_names = ['Alabama_Psychiatry', 'Birmingham_Anxiety', 'Eastside_Mental_Health', 'Restorative_Counseling', 'Thriveworks_Counseling']

# Plot data for each center
for center_name in center_names:
    plot_data_for_center(center_name, ground_truth_df, example_df, processed_df, explanation_df, lump_df)
