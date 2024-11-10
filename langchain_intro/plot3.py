import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV data into dataframes
ground_truth_file = 'ground_truth.csv'
processed_file = 'processed_csvs_averages.csv'
example_file = 'example_csvs_averages.csv'
explanation_file = 'explanation_csvs_averages.csv'
lump_file = 'processed_csvs_lump_averages.csv'

# Load data from CSV files
ground_truth_df = pd.read_csv(ground_truth_file, header=None, names=['Name', 'Ranking', 'Friendliness', 'General Rating', 'Flexibility', 'Ease', 'Affordability', 'Response Time'])
processed_df = pd.read_csv(processed_file, header=None, names=['File', 'Affordability', 'Ease', 'Flexibility', 'Friendliness', 'General Rating', 'Ranking', 'Response Time'])
example_df = pd.read_csv(example_file, header=None, names=['File', 'Affordability', 'Ease', 'Flexibility', 'Friendliness', 'General Rating', 'Ranking', 'Response Time'])
explanation_df = pd.read_csv(explanation_file, header=None, names=['File', 'Affordability', 'Ease', 'Flexibility', 'Friendliness', 'General Rating', 'Ranking', 'Response Time'])
lump_df = pd.read_csv(lump_file, header=None, names=['File', 'Affordability', 'Ease', 'Flexibility', 'Friendliness', 'General Rating', 'Ranking', 'Response Time'])

# Set the index as 'File' for the processed dataframes
processed_df.set_index('File', inplace=True)
example_df.set_index('File', inplace=True)
explanation_df.set_index('File', inplace=True)
lump_df.set_index('File', inplace=True)

# List of centers
centers = ['Alabama_Psychiatry', 'Birmingham_Anxiety', 'Eastside_Mental_Health', 'Restorative_Counseling', 'Thriveworks_Counseling']

# Columns to plot
columns_to_plot = ['Ranking', 'Friendliness', 'General Rating', 'Flexibility', 'Ease', 'Affordability', 'Response Time']

# Function to plot the data for each center and each dataset
def plot_center_data(center_name, ground_truth_df, processed_df, example_df, explanation_df, lump_df):
    # Extract ground truth data
    ground_truth_name = f'ground_truth_{center_name}_Dataset'
    ground_truth = ground_truth_df[ground_truth_df['Name'] == ground_truth_name].iloc[0]

    # Extract processed, example, explanation, and lumped data
    processed = processed_df.loc[f'processed_csvs_processed_{center_name}_Dataset']
    example = example_df.loc[f'example_csvs_processed_{center_name}_Dataset']
    explanation = explanation_df.loc[f'explanation_csvs_processed_{center_name}_Dataset']
    lump = lump_df.loc[f'processed_csvs_lump_processed_{center_name}_Dataset']

    # Prepare data for plotting (align data by columns)
    plot_data = pd.DataFrame({
        'Ground Truth': ground_truth[columns_to_plot].values,
        'Processed': processed[columns_to_plot].values,
        'Example': example[columns_to_plot].values,
        'Explanation': explanation[columns_to_plot].values,
        'Lump': lump[columns_to_plot].values
    }, index=columns_to_plot)

    # Plot each attribute in separate bars
    plot_data.plot(kind='bar', figsize=(10, 6))
    
    # Customize the plot
    plt.title(f'Comparison of Average Scores for {center_name}')
    plt.xlabel('Metrics')
    plt.ylabel('Average Score')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.legend(title='Approach')

    # Show the plot
    plt.show()

# Generate plots for each center
for center in centers:
    plot_center_data(center, ground_truth_df, processed_df, example_df, explanation_df, lump_df)
