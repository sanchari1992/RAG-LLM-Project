import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load the CSV file
df = pd.read_csv("./averages/average.csv")

# Set up the bar graph
def create_grouped_bar_chart(df):
    metrics = df.columns[1:]  # Metrics columns (skip "Name" column)
    num_metrics = len(metrics)
    bar_width = 0.15  # Width of each bar
    x = np.arange(num_metrics)  # Label locations for each metric

    # Create figure and axis
    fig, ax = plt.subplots(figsize=(12, 6))

    # Plot each counseling center's data with a specific offset for bars
    for i, (index, row) in enumerate(df.iterrows()):
        name = row['Name']
        values = row[metrics]
        ax.bar(x + i * bar_width, values, width=bar_width, label=name)

    # Set labels and title
    ax.set_xlabel('Metrics')
    ax.set_ylabel('Scores')
    ax.set_title('Counseling Center Comparison by Metrics')
    ax.set_xticks(x + bar_width * (len(df) - 1) / 2)  # Center x-ticks under bars
    ax.set_xticklabels(metrics, rotation=45)

    # Add legend
    ax.legend(title="Counseling Centers")

    # Show the plot
    plt.tight_layout()
    plt.show()

# Call the function to create the grouped bar chart
create_grouped_bar_chart(df)
