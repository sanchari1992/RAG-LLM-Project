import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Initialize the figure
fig, ax = plt.subplots(figsize=(12, 8))

# Define coordinates and dimensions of blocks
blocks = {
    "Data Processing Module": (1, 7, 3, 1),
    "Prompting Engine": (5, 7, 3, 1),
    "Evaluation and Visualization Module": (9, 7, 3, 1),
    "Raw Data Collection": (1, 5, 3, 1),
    "Data Cleaning": (1, 3, 3, 1),
    "Single Prompting": (5, 6, 3, 1),
    "Batch Prompting": (5, 5, 3, 1),
    "Enhanced Prompting Strategies": (5, 4, 3, 1),
    "RAG Integration": (5, 3, 3, 1),
    "Database Systems": (5, 1, 3, 1),
    "Algorithm 1": (9, 5, 3, 1),
    "Algorithm 2": (9, 3, 3, 1)
}

# Draw blocks
for block, (x, y, w, h) in blocks.items():
    rect = plt.Rectangle((x, y), w, h, edgecolor='black', facecolor='lightblue', linewidth=2)
    ax.add_patch(rect)
    plt.text(x + w/2, y + h/2, block, ha='center', va='center', fontsize=10, wrap=True)

# Draw arrows between blocks
arrows = [
    ((2.5, 7), (2.5, 6.5)),  # Data Processing -> Raw Data Collection
    ((2.5, 6), (2.5, 5.5)),  # Raw Data Collection -> Data Cleaning
    ((2.5, 5), (6, 5.5)),    # Data Cleaning -> Prompting Engine
    ((6.5, 7), (6.5, 6.5)),  # Prompting Engine -> Single Prompting
    ((6.5, 6), (6.5, 5.5)),  # Single Prompting -> Batch Prompting
    ((6.5, 5), (6.5, 4.5)),  # Batch Prompting -> Enhanced Prompting Strategies
    ((6.5, 4), (6.5, 3.5)),  # Enhanced Prompting Strategies -> RAG Integration
    ((6.5, 3), (6.5, 2.5)),  # RAG Integration -> Database Systems
    ((6.5, 7), (9.5, 7)),    # Prompting Engine -> Evaluation Module
    ((10.5, 7), (10.5, 5.5)), # Evaluation -> Algorithm 1
    ((10.5, 5), (10.5, 3.5))  # Algorithm 1 -> Algorithm 2
]

for (start, end) in arrows:
    ax.annotate("", xy=end, xycoords='data', xytext=start, textcoords='data',
                arrowprops=dict(arrowstyle="->", color="black", lw=1.5))

# General diagram formatting
plt.xlim(0, 13)
plt.ylim(0, 9)
ax.axis('off')
plt.title("Proposed Architecture: Mental Health Review Analysis Framework", fontsize=14)
plt.show()
