import os
import pandas as pd

# Set paths for the folders containing the CSV files with averages
EXAMPLE_CSVS_AVERAGES_FILE = './example_csvs_averages.csv'
PROCESSED_CSVS_AVERAGES_FILE = './processed_csvs_averages.csv'
EXPLANATION_CSVS_AVERAGES_FILE = './explanation_csvs_averages.csv'
PROCESSED_CSVS_LUMP_AVERAGES_FILE = './processed_csvs_lump_averages.csv'

# Columns to plot
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

# Combine the dataframes into one with the attributes as rows and the folders as columns
averages_combined_df = pd.DataFrame({
    'Affordability': [example_df['Affordability'].mean(), processed_df['Affordability'].mean(), explanation_df['Affordability'].mean(), lump_df['Affordability'].mean()],
    'Ease': [example_df['Ease'].mean(), processed_df['Ease'].mean(), explanation_df['Ease'].mean(), lump_df['Ease'].mean()],
    'Flexibility': [example_df['Flexibility'].mean(), processed_df['Flexibility'].mean(), explanation_df['Flexibility'].mean(), lump_df['Flexibility'].mean()],
    'Friendliness': [example_df['Friendliness'].mean(), processed_df['Friendliness'].mean(), explanation_df['Friendliness'].mean(), lump_df['Friendliness'].mean()],
    'General Rating': [example_df['General Rating'].mean(), processed_df['General Rating'].mean(), explanation_df['General Rating'].mean(), lump_df['General Rating'].mean()],
    'Ranking': [example_df['Ranking'].mean(), processed_df['Ranking'].mean(), explanation_df['Ranking'].mean(), lump_df['Ranking'].mean()],
    'Response Time': [example_df['Response Time'].mean(), processed_df['Response Time'].mean(), explanation_df['Response Time'].mean(), lump_df['Response Time'].mean()]
}, index=['Processed', 'Example', 'Explanation', 'Lump'])

# Save the final combined averages to a CSV file
averages_combined_df = averages_combined_df.round(2)  # Round values to 2 decimal places
averages_combined_df.to_csv('average_scores_combined.csv')

print("Average scores saved in 'average_scores_combined.csv'")
