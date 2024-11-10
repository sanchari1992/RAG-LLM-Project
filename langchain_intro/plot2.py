import pandas as pd
import matplotlib.pyplot as plt

# Read the averages from the updated CSV file
averages_df = pd.read_csv('average_scores_combined.csv', index_col=0)

# Plotting the bar graphs for each metric
averages_df.plot(kind='bar', figsize=(12, 8))

# Adding a title and labels
plt.title('Comparison of Average Scores Across Different Approaches')
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
