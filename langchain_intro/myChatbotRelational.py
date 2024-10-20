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

def fetch_reviews_from_db(question, max_reviews_per_table=5):
    cursor = mysql_connection.cursor(dictionary=True)

    # Get all table names dynamically
    cursor.execute("SHOW TABLES")
    tables = [table['Tables_in_' + os.getenv('MYSQL_DATABASE')] for table in cursor.fetchall()]
    
    context = ""
    token_count = 0  # Track the number of tokens

    tokens_per_word = 1.3
    max_tokens = 16000  # Stay below the limit

    # Query each table for matching reviews
    for table in tables:
        query = f"""
            SELECT Comment FROM {table}
            WHERE MATCH(Comment) AGAINST (%s IN NATURAL LANGUAGE MODE)
            LIMIT {max_reviews_per_table}
        """
        cursor.execute(query, (question,))
        reviews = cursor.fetchall()

        # Add reviews to the context, but truncate if too long
        for review in reviews:
            truncated_review = truncate_review(review['Comment'], max_words=50)
            review_token_count = int(len(truncated_review.split()) * tokens_per_word)

            if token_count + review_token_count < max_tokens:
                context += truncated_review + " "
                token_count += review_token_count
            else:
                break  # Stop if we exceed the token limit

    cursor.close()

    return context.strip()


# Define the review templates
review_template_str = """You are restricted to using ONLY the database entries provided to you.
Do not answer any questions based on your own knowledge or any external sources. 
You must base your answer entirely on the provided context.

Your task is to summarize the sentiment of the reviews for all answers to any questions asked. Look for trends in the comments, such as whether they are generally positive, negative, or neutral regarding specific aspects of the services, staff, or scheduling options.

If the reviews mention staff being friendly or rude, summarize that sentiment. If the reviews generally mention a center having flexible or easy scheduling, summarize that sentiment. If the reviews generally mention a center being affordable or expensive, summarize that sentiment. Basically summarize all sentiments based on all the available reviews from all relations and give answer. If the context does not contain the information needed to answer the question, respond with 'I don't know.'

Please aim to answer the question within 5 iterations.

Here are examples of how to respond:
- If the reviews say, "The staff at XYZ Counseling are very friendly and helpful," you could respond, "The staff at XYZ Counseling are considered friendly by reviewers."
- If no reviews mention a certain aspect, you should respond, "I don't know."

Do not make the answers too long. Make them brief.

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
        description="""Useful when you need to answer questions
        about mental health center reviews from the available data in the MySQL database.
        Pass the entire question as input to the tool.""",
    ),
]

mybot_agent_prompt = PromptTemplate(
    input_variables=["input", "agent_scratchpad"],
    template="""You are a helpful assistant. You must only answer questions based on the existing database information.

    Do not use any external knowledge. If the answer is not available in the context, say 'I don't know.'

    Once you have found an adequate answer based on the reviews, you should stop querying and return your final answer.

    Question: {input}
    Agent Scratchpad: {agent_scratchpad}"""
)

mybot_agent = create_openai_functions_agent(
    llm=chat_model,
    prompt=mybot_agent_prompt,
    tools=tools,
)

# Updating the AgentExecutor to stop once the answer is found
mybot_agent_executor = AgentExecutor(
    agent=mybot_agent,
    tools=tools,
    return_intermediate_steps=False,
    verbose=True,
    max_iterations=10
)

@app.route("/ask", methods=["POST"])
def ask_question():
    try:
        data = request.json
        question = data.get("question", "")
        context = fetch_reviews_from_db(question)
        result = mybot_agent_executor({"input": question, "context": context})
        return jsonify({"answer": result["output"]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)