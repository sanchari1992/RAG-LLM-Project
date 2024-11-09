import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load the CSV file
df = pd.read_csv("./averages/average.csv")

# Set up the bar graph
def create_bar_graph(df):
    categories = df.columns[1:]  # Metrics (skip "Name" column)
    num_categories = len(categories)
    bar_width = 0.15  # Width of each bar
    x = np.arange(num_categories)  # Label locations

    # Create figure and axis
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot each counseling center's data
    for i, row in df.iterrows():
        name = row['Name']
        values = row[categories]
        ax.bar(x + i * bar_width, values, width=bar_width, label=name)

    # Add some text for labels, title, and custom x-axis tick labels
    ax.set_xlabel('Metrics')
    ax.set_ylabel('Scores')
    ax.set_title('Comparison of Counseling Centers by Metric')
    ax.set_xticks(x + bar_width * (len(df) - 1) / 2)  # Center the ticks
    ax.set_xticklabels(categories)
    ax.legend(title="Counseling Centers")

    plt.xticks(rotation=45)
    plt.tight_layout()  # Adjust layout to fit everything nicely
    plt.show()

# Call the function to create the bar graph
create_bar_graph(df)
