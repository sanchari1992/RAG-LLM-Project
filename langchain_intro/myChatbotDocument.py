from flask import Flask, request, jsonify
from flask_cors import CORS
import dotenv
import os
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
from pymongo import MongoClient

# Load environment variables
dotenv.load_dotenv()

app = Flask(__name__)
CORS(app)

# MongoDB connection
mongodb_uri = os.getenv('MONGODB_URI')
database_name = os.getenv('DATABASE_NAME')

# Create a MongoDB client
client = MongoClient(mongodb_uri)
db = client[database_name]

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

# Mapping keywords to collection names
collection_mapping = {
    'mental health': 'mental_health_centers',  # Adjust collection names as needed
    'center': 'mental_health_centers',
    # Add other mappings here
}

# Function to fetch the appropriate collection name based on incoming requests
def get_collection_name_from_question(question):
    question_lower = question.lower()
    for keyword, collection_name in collection_mapping.items():
        if keyword in question_lower:
            return collection_name
    return None  # Return None if no matching collection found

# Function to retrieve reviews from MongoDB based on the dynamic collection name
def fetch_reviews_from_mongodb(question):
    collection_name = get_collection_name_from_question(question)  # Get the dynamic collection name

    # Check if the collection exists
    if collection_name is None or collection_name not in db.list_collection_names():
        return "Collection not found or not specified."

    # Search for relevant reviews based on the question (full-text search on 'Comment')
    reviews = db[collection_name].find({
        "$text": {"$search": question}
    }).limit(10)

    # Create a context string from the retrieved reviews
    context = ""
    for review in reviews:
        # Assuming 'Comment', 'Name', 'Rating', and 'Review_Year' are the fields
        review_content = (
            f"Center: {review['Name']}\n"
            f"Rating: {review['Rating']}/5\n"
            f"Review Year: {review['Review_Year']}\n"
            f"Comment: {review['Comment']}\n\n"
        )
        context += review_content
    
    return context if context else "I don't know."

# Modify the review_chain to use MongoDB data
review_chain = (
    {"context": fetch_reviews_from_mongodb, "question": RunnablePassthrough()}
    | review_prompt_template
    | chat_model
    | output_parser
)

tools = [
    Tool(
        name="Reviews",
        func=review_chain.invoke,
        description="""Useful when you need to answer questions
        about mental health center reviews in the database.
        The reviews include fields like 'Center Name', 'Rating', 'Review Year', and 'Comment'.
        Pass the entire question as input to the tool. For example,
        if the question is "What do people think of Center A?",
        the input should be "What do people think of Center A?"
        """,
    ),
]

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
    return_intermediate_steps=False,
    verbose=True,
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
    app.run(debug=True)
