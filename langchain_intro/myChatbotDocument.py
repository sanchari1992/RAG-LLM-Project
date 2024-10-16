import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from langchain_openai import ChatOpenAI
from langchain.prompts import (
    PromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
)
from langchain_core.output_parsers import StrOutputParser
from langchain.agents import create_openai_functions_agent, Tool, AgentExecutor
import dotenv

# Load environment variables
dotenv.load_dotenv()

# Flask app setup
app = Flask(__name__)
CORS(app)

# # Set up logging
# logging.basicConfig(level=logging.WARNING)

# MongoDB connection
mongodb_uri = os.getenv('MONGODB_URI')
database_name = os.getenv('DATABASE_NAME')

# Create a MongoDB client
client = MongoClient(mongodb_uri)
db = client[database_name]

# Function to get and print collection names
def get_collection_names():
    return db.list_collection_names()  # Retrieve the collection names

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

review_prompt_template = ChatPromptTemplate(
    input_variables=["context", "question"],
    messages=messages,
)

chat_model = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)
output_parser = StrOutputParser()

# Function to retrieve all reviews from all collections in MongoDB
def fetch_all_reviews():
    context = ""
    collection_names = get_collection_names()  # Get all collection names

    # Iterate over each collection and retrieve reviews
    for collection_name in collection_names:
        reviews = db[collection_name].find()
        for review in reviews:
            review_content = (
                f"Center: {review['Counseling Center']}\n"
                f"Name: {review['Name']}\n"
                f"Rating: {review['Rating']}/5\n"  # Use the correct column name
                f"Review Year: {review['Review Year']}\n"
                f"Comment: {review['Comment']}\n\n"
            )
            context += review_content
    
    # Return context or a default message if empty
    return context if context else "I don't know."

# Function to truncate context to a specific length
def truncate_context(context, max_length=4000):
    if len(context) > max_length:
        return context[:max_length] + "... (truncated)"
    return context

# Function to create the review chain
def create_review_chain(context, question):
    # Truncate the context if it's too long
    context = truncate_context(context)

    # Construct the prompt
    context_prompt = review_prompt_template.invoke({"context": context, "question": question})
    
    # Get the answer from the chat model
    answer = chat_model.invoke(context_prompt)

    return output_parser.parse(answer)

# Tool setup for the agent
tools = [
    Tool(
        name="Reviews",
        func=lambda question: create_review_chain(fetch_all_reviews(), question),
        description="""Useful when you need to answer questions
        about therapists and mental health counseling centers based on the reviews in the database.
        The reviews include fields like 'Counseling Center', 'Name', 'Rating', 'Review Year', and 'Comment'.
        Pass the entire question as input to the tool. For example,
        if the question is "What do people think of Center A?",
        the input should be "What do people think of Center A?"
        """,
    ),
]

# Agent setup
mybot_agent_prompt = PromptTemplate(
    input_variables=["input", "agent_scratchpad"],
    template="""You are a helpful assistant. You must only answer questions based on the existing database information.

    Do not use any external knowledge. If the answer is not available in the context, say 'I don't know.'

    Question: {input}
    Agent Scratchpad: {agent_scratchpad}"""
)

mybot_agent = create_openai_functions_agent(
    llm=chat_model,
    prompt=mybot_agent_prompt,
    tools=tools,
)

mybot_agent_executor = AgentExecutor(
    agent=mybot_agent,
    tools=tools,
    return_intermediate_steps=True,
    verbose=True,  # Set verbose to False to reduce console output
)

@app.route("/ask", methods=["POST"])
def ask_question():
    try:
        data = request.json
        question = data.get("question", "")
        result = mybot_agent_executor({"input": question})
        return jsonify({"answer": result["output"]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)  # Set to False in production
