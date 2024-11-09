import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load the CSV file
df = pd.read_csv("./averages/average.csv")

# Define a function to create radar charts
def create_radar_chart(data, categories, title):
    # Number of variables we're plotting
    num_vars = len(categories)

    # Compute angle of each axis
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()

    # Complete the circle
    data = np.concatenate((data,[data[0]]))
    angles += angles[:1]

    # Initialize the radar plot
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))

    # Draw one line per frame with its corresponding label
    ax.plot(angles, data, linewidth=1, linestyle='solid')
    ax.fill(angles, data, 'b', alpha=0.1)

    # Add labels
    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories)
    ax.set_title(title, size=15, color='navy', y=1.1)

    plt.show()

# List of categories (metrics)
categories = list(df.columns[1:])  # Exclude the "Name" column

# Generate a radar chart for each row in the DataFrame
for i, row in df.iterrows():
    name = row['Name']
    data = row[categories].values
    create_radar_chart(data, categories, title=name)
