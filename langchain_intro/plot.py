import os
import pandas as pd
import matplotlib.pyplot as plt

# Set paths for the folders containing the CSV files
PROCESSED_CSV_FOLDER = './processed_csvs'
EXAMPLE_CSV_FOLDER = './example_csvs'
EXPLANATION_CSV_FOLDER = './explanation_csvs'

# Names of the files to compare (same file names across folders)
file_names = [
    'processed_Alabama_Psychiatry_Dataset.csv',
    'processed_Birmingham_Anxiety_Dataset.csv',
    'processed_Eastside_Mental_Health_Dataset.csv',
    'processed_Restorative_Counseling_Dataset.csv',
    'processed_Thriveworks_Counseling_Dataset.csv'
]

# Columns to plot
columns_to_plot = ["Ranking", "Friendliness", "General Rating", "Flexibility", "Ease", "Affordability", "Response Time"]

# Function to extract average values from the last row of each file
def extract_averages(folder_path, file_name):
    file_path = os.path.join(folder_path, file_name)
    df = pd.read_csv(file_path)
    return df.iloc[-1][columns_to_plot].astype(float)

# Dictionary to store the averages for each dataset
data = {
    'Processed': [],
    'Example': [],
    'Explanation': []
}

# Extract averages from each folder
for file_name in file_names:
    data['Processed'].append(extract_averages(PROCESSED_CSV_FOLDER, file_name))
    data['Example'].append(extract_averages(EXAMPLE_CSV_FOLDER, file_name))
    data['Explanation'].append(extract_averages(EXPLANATION_CSV_FOLDER, file_name))

# Convert the list of averages to DataFrames
processed_df = pd.DataFrame(data['Processed'], index=file_names)
example_df = pd.DataFrame(data['Example'], index=file_names)
explanation_df = pd.DataFrame(data['Explanation'], index=file_names)

# Calculate the mean averages across centers for each approach
processed_mean = processed_df.mean()
example_mean = example_df.mean()
explanation_mean = explanation_df.mean()

# Combine the averages for plotting
averages_df = pd.DataFrame({
    'Processed': processed_mean,
    'Example': example_mean,
    'Explanation': explanation_mean
})

# Plotting the bar graphs for each metric
averages_df.plot(kind='bar', figsize=(12, 8))
plt.title('Comparison of Average Scores Across Different Approaches')
plt.xlabel('Metrics')
plt.ylabel('Average Score')
plt.legend(title='Approach')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
