# RAG-LLM-Project

Flow of operation:

1. Folders:
data
Unprocessed data collected from Google reviews.

Code:
clean_data.py

cleaned_data
Processed data from above data.

2. Load to GPT
a. One at a time
rankingCommentsOneByOne.py

b. Lump
rankingCommentsLump.py

c. One at a time with example in prompt
rankingCommentsOneByOneExample.py

d. One at a time with explanation providing
rankingCommentsOneByOneExplanation.py

3. Calculate averages of the rows
For files without explanation, update input folder name and use:
averageScale.py

For files without explanation, update input folder name and use:
averageScaleWithExplanation.py

File: ground_truth.csv
Contains all ground truth values

To gather all averages together:
Use averageScoreCollection.py

Returns:
average_scores_combined.csv

Add ground truth to it and plot accuracy:
accuracyPlot.py

Plot response times
responsePlot.py



3. Load to databases

load_csv_to_mysql.py
load_csv_to_mongo.py
load_csv_to_mongo_grouped.py (Loads data grouped by above average, average, and below average ratings)
load_csv_to_chroma.py

4. Run corresponding API bots (to get graded responses between 0 to 5)

myChatbotRelational.py
myChatbotDocument.py
myChatbotDocument_Grouped.py
myChatbotVector.py

5. Run corresponding API bots with full responses

myRelationalAPIWithoutWeightedCommentTimes.py
myDocumentAPIWithoutWeightedCommentTimes.py
myVectorAPIWithoutWeightedCommentTimes.py

6. Run corresponding API bots with full responses for weights given to when comment was posted

myRelationalAPIWithWeightedCommentTimes.py
myDocumentAPIWithWeightedCommentTimes.py
myVectorAPIWithWeightedCommentTimes.py