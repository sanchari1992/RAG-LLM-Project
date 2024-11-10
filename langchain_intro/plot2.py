# plot_averages.py

import pandas as pd
import matplotlib.pyplot as plt

# Read the averages from the CSV file
averages_df = pd.read_csv('average_scores.csv', index_col=0)

# Plotting the bar graphs for each metric
averages_df.plot(kind='bar', figsize=(12, 8))
plt.title('Comparison of Average Scores Across Different Approaches')
plt.xlabel('Metrics')
plt.ylabel('Average Score')
plt.legend(title='Approach')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
