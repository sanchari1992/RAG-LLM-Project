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

# Function to fetch reviews from MySQL
def fetch_reviews_from_db(question):
    cursor = mysql_connection.cursor(dictionary=True)
    query = """
        SELECT review_body FROM reviews
        WHERE MATCH(review_body) AGAINST (%s IN NATURAL LANGUAGE MODE)
        LIMIT 10
    """
    cursor.execute(query, (question,))
    reviews = cursor.fetchall()
    cursor.close()

    context = " ".join([review['review_body'] for review in reviews])
    return context

# Define the review templates
review_template_str = """You are restricted to using ONLY the database entries provided to you.
Do not answer any questions based on your own knowledge or any external sources. 
You must base your answer entirely on the provided context. 

If the context does not contain the information needed to answer the question, 
respond with 'I don't know'. 

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

chat_model = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)
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
        description="Useful when answering questions about IoT medical devices from the MySQL database."
    ),
]

hospital_agent_prompt = PromptTemplate(
    input_variables=["input", "agent_scratchpad"],
    template="""You are a helpful assistant. You must only answer questions based on the existing database information.

    Do not use any external knowledge. If the answer is not available in the context, say 'I don't know.'

    Question: {input}
    Agent Scratchpad: {agent_scratchpad}"""
)

hospital_agent = create_openai_functions_agent(
    llm=chat_model,
    prompt=hospital_agent_prompt,
    tools=tools,
)

hospital_agent_executor = AgentExecutor(
    agent=hospital_agent,
    tools=tools,
    return_intermediate_steps=False,
    verbose=True,
)

@app.route("/ask", methods=["POST"])
def ask_question():
    try:
        data = request.json
        question = data.get("question", "")
        context = fetch_reviews_from_db(question)
        result = hospital_agent_executor({"input": question, "context": context})
        return jsonify({"answer": result["output"]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
