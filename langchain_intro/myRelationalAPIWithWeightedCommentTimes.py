import os
import mysql.connector
from flask import Flask, request, jsonify
from flask_cors import CORS
import dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import (
    PromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
)
from langchain_core.output_parsers import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from langchain.agents import (
    create_openai_functions_agent,
    Tool,
    AgentExecutor,
)
from langchain import hub
import datetime

# Load environment variables
dotenv.load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# MySQL connection
def connect_to_mysql():
    try:
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST'),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD'),
            database=os.getenv('MYSQL_DATABASE')
        )
        if connection.is_connected():
            print("Successfully connected to MySQL database")
            return connection
    except mysql.connector.Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None

mysql_connection = connect_to_mysql()

def truncate_review(review, max_words=100):
    words = review.split()
    if len(words) > max_words:
        return " ".join(words[:max_words]) + "..."
    return review

# Modify the fetch_reviews_from_db function to include weights based on the year
def fetch_reviews_from_db(question, max_reviews_per_table=5):
    cursor = mysql_connection.cursor(dictionary=True)

    # Get all table names dynamically
    cursor.execute("SHOW TABLES")
    tables = [table['Tables_in_' + os.getenv('MYSQL_DATABASE')] for table in cursor.fetchall()]
    
    context = ""
    token_count = 0  # Track the number of tokens

    tokens_per_word = 1.3
    max_tokens = 16000  # Stay below the limit

    # Get the current year and last year for weighting
    current_year = datetime.datetime.now().year
    last_year = current_year - 1

    # Query each table for matching reviews
    for table in tables:
        query = f"""
            SELECT Comment, `Review Year` FROM {table}
            WHERE MATCH(Comment) AGAINST (%s IN NATURAL LANGUAGE MODE)
            LIMIT {max_reviews_per_table}
        """
        cursor.execute(query, (question,))
        reviews = cursor.fetchall()

        # Add reviews to the context, but truncate if too long
        for review in reviews:
            review_year = review['Review Year']
            truncated_review = truncate_review(review['Comment'], max_words=50)

            # Calculate weight based on the review year
            if review_year == current_year:
                weight = 1
            elif review_year == last_year:
                weight = 0.7
            else:
                weight = 0.2

            review_token_count = int(len(truncated_review.split()) * tokens_per_word)

            if token_count + review_token_count < max_tokens:
                # Add weighted review to context
                context += f"[Weight: {weight}] {truncated_review} "
                token_count += review_token_count
            else:
                break  # Stop if we exceed the token limit

    cursor.close()

    return context.strip()

# Update the review templates
review_template_str = """You are restricted to using ONLY the database entries provided to you. 
Do not answer any questions based on your own knowledge or any external sources.  Use only the following context to answer questions.
Look for trends in the comments, such as whether they are generally positive, negative, or neutral regarding specific aspects of the services, staff, or scheduling options. 
 Return whatever information you get in the first try itself. No need to refine further for a better answer.
Try to categorize this returned information on a scale of 0 to 5 in terms of the question asked:
- 0: No information at all
- 1: Very Poor
- 2: Poor
- 3: Average
- 4: Good
- 5: Excellent

Respond with only the numbers for each category, one per line, or "0" if a category is not mentioned in the comment.

For example, if returned information is "The feedback for counseling center C is generally friendly.", return '4'.

{context}
"""

review_system_prompt = SystemMessagePromptTemplate(
    prompt=PromptTemplate(input_variables=["context"], template=review_template_str)
)

review_human_prompt = HumanMessagePromptTemplate(
    prompt=PromptTemplate(input_variables=["question"], template="{question}")
)

messages = [review_system_prompt, review_human_prompt]
review_prompt_template = ChatPromptTemplate(input_variables=["context", "question"], messages=messages)

chat_model = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0, max_tokens=200)
output_parser = StrOutputParser()

# Replace Chroma with MySQL-based retrieval
review_chain = (
    {"context": fetch_reviews_from_db, "question": RunnablePassthrough()}
    | review_prompt_template
    | chat_model
    | output_parser
)

tools = [
    Tool(
        name="Reviews",
        func=review_chain.invoke,
        description="""Useful when you need to answer questions from the SQL database
        about mental health counseling centers - their ratings, rankings, staff, affordability, properties etc based on the reviews in the database.
        There are five relations on five different counseling centers in Birmingham, Alabama.
        The reviews include fields like 'Counseling Center', 'Name', 'Rating', 'Review Year', and 'Comment'.
        Pass the entire question as input to the tool. For example,
        if the question is "What do people think of Center A?",
        the input should be "What do people think of Center A?"
        """,
    ),
]

mybot_agent_prompt = hub.pull("hwchase17/openai-functions-agent")
mybot_agent = create_openai_functions_agent(
    llm=chat_model,
    prompt=mybot_agent_prompt,
    tools=tools,
)
mybot_agent_executor = AgentExecutor(
    agent=mybot_agent,
    tools=tools,
    return_intermediate_steps=True,
    verbose=True,
    max_iterations=5
)

@app.route("/ask", methods=["POST"])
def ask_question():
    try:
        data = request.json
        question = data.get("question", "")
        result = mybot_agent_executor({"input": question})

        # Check and format the response to ensure it is within the range of 1 to 5 or "0"
        ratings = result["output"].strip().splitlines()
        formatted_ratings = []

        for rating in ratings:
            if rating.isdigit() and 1 <= int(rating) <= 5:
                formatted_ratings.append(rating)
            else:
                formatted_ratings.append("0")  # Assign "0" for invalid ratings

        return jsonify({"answer": "\n".join(formatted_ratings)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
