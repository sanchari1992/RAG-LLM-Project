# RAG-LLM Project

This project explores the use of various database structures and prompting techniques with GPT-based models to generate insights from mental health counseling reviews. The project is organized into multiple folders and scripts, each with specific tasks, from data cleaning to API implementation.

## Project Structure

### 1. Data Processing

#### Folders
- **data**: Contains unprocessed review data collected from Google reviews.
- **cleaned_data**: Contains processed data output by the `clean_data.py` script.

#### Scripts
- **clean_data.py**: Cleans raw data files from the `data` folder and outputs processed files to the `cleaned_data` folder.

### 2. Loading Data to GPT

This step processes and formats review comments to be loaded to GPT in different configurations.

#### Methods
- **One at a Time**: Processes each comment individually.
  - **Script**: `rankingCommentsOneByOne.py`
  
- **Lump**: Processes all comments as a single, concatenated input.
  - **Script**: `rankingCommentsLump.py`
  
- **One at a Time with Example in Prompt**: Each comment is processed individually, with an example included in the prompt to guide GPT’s response.
  - **Script**: `rankingCommentsOneByOneExample.py`
  
- **One at a Time with Explanation Provided**: Each comment is processed individually, with an additional explanatory context provided in the prompt.
  - **Script**: `rankingCommentsOneByOneExplanation.py`

### 3. Calculate Averages

These scripts calculate average scores from GPT responses and organize them for analysis.

#### Steps
1. **Calculate Row Averages**:
   - **Script**: `averageScale.py` (for files without explanations)
   - **Script**: `averageScaleWithExplanation.py` (for files with explanations)
   
2. **Ground Truth Values**:
   - **File**: `ground_truth.csv` - Contains ground truth values for comparison.

3. **Collect Averages**:
   - **Script**: `averageScoreCollection.py` - Collects all averages into a single file, `average_scores_combined.csv`.
   
4. **Accuracy and Response Time Analysis**:
   - **Accuracy Plot**:
     - **Script**: `accuracyPlot.py` - Adds ground truth values to `average_scores_combined.csv` and calculates accuracy.
     - **Script**: `accuracyPlot1.py` - Calculate overall accuracy based on ground truth for one at a time and lump for both processed and unprocessed data and plots it.
   - **Response Time Plot**:
     - **Script**: `responsePlot.py` - Plots response times for different approaches.

### 4. Load Data to Databases

Scripts for loading the cleaned data to various databases.

#### Database Loading Scripts
- **MySQL**: Loads data to a relational database.
  - **Script**: `load_csv_to_mysql.py`
  
- **MongoDB**:
  - **Standard**: Loads data to MongoDB.
    - **Script**: `load_csv_to_mongo.py`
  - **Grouped**: Loads data grouped by above average, average, and below average ratings.
    - **Script**: `load_csv_to_mongo_grouped.py`
    
- **ChromaDB**: Loads data into a Chroma vector database.
  - **Script**: `load_csv_to_chroma.py`

### 5. Graded Responses API

Runs API bots to get graded responses (from 0 to 5) based on database queries.

#### API Bots for Graded Responses
- **Relational Database**: `myChatbotRelational.py`
- **Document Database**: `myChatbotDocument.py`
- **Document Database (Grouped)**: `myChatbotDocument_Grouped.py`
- **Vector Database**: `myChatbotVector.py`

### 6. Full Responses API (No Weighting)

Runs API bots to return full-text responses from the database, without weighting based on comment timing.

#### API Bots for Full Responses
- **Relational Database**: `myRelationalAPIWithoutWeightedCommentTimes.py`
- **Document Database**: `myDocumentAPIWithoutWeightedCommentTimes.py`
- **Vector Database**: `myVectorAPIWithoutWeightedCommentTimes.py`

### 7. Full Responses API (With Weighting Based on Comment Timing)

Runs API bots to return full-text responses from the database, applying weights based on the timing of each comment.

#### API Bots for Weighted Responses
- **Relational Database**: `myRelationalAPIWithWeightedCommentTimes.py`
- **Document Database**: `myDocumentAPIWithWeightedCommentTimes.py`
- **Vector Database**: `myVectorAPIWithWeightedCommentTimes.py`

---

Each step in this project enables different insights and comparisons between various database structures, data loading methods, and GPT-based prompt configurations.
