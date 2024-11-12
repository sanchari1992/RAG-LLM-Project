import os
import logging
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
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.schema.runnable import RunnablePassthrough
from langchain.agents import (
    create_openai_functions_agent,
    Tool,
    AgentExecutor,
)
from langchain import hub
from datetime import datetime

# Load environment variables
dotenv.load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

REVIEWS_CHROMA_PATH = "chroma_data/"

# Step 1: Initialize Chroma vector DB for reviews
reviews_vector_db = Chroma(
    persist_directory=REVIEWS_CHROMA_PATH,
    embedding_function=OpenAIEmbeddings()
)

# Step 2: Set up the retriever from the Chroma DB
reviews_retriever = reviews_vector_db.as_retriever(k=10)  # Fetch top 10 matches

# Function to apply weight to each review based on year
def apply_year_weight(reviews):
    current_year = datetime.now().year
    last_year = current_year - 1
    weighted_reviews = []

    for review in reviews:
        review_text = review['document']  # or however the review text is accessed in Chroma
        review_year = review['metadata'].get('Review Year', current_year)  # Access review year from metadata, default to current year if missing
        
        # Determine the weight
        if review_year == current_year:
            weight = 1
        elif review_year == last_year:
            weight = 0.7
        else:
            weight = 0.2
        
        # Apply the weight by repeating or modifying text (simplified approach)
        weighted_text = (review_text + " ") * int(weight * 10)  # Repeat text based on weight multiplier
        weighted_reviews.append(weighted_text.strip())
    
    return " ".join(weighted_reviews)

# Step 3: Define the review templates
review_template_str = """You are restricted to using ONLY the database entries provided to you. 
Do not answer any questions based on your own knowledge or any external sources. Use only the following context to answer questions.
Look for trends in the comments, such as whether they are generally positive, negative, or neutral regarding specific aspects of the services, staff, or scheduling options. Return a full-text answer based on this context.

{context}
"""

review_system_prompt = SystemMessagePromptTemplate(
    prompt=PromptTemplate(
        input_variables=["context"],
        template=review_template_str,
    )
)

review_human_prompt = HumanMessagePromptTemplate(
    prompt=PromptTemplate(
        input_variables=["question"],
        template="{question}",
    )
)

messages = [review_system_prompt, review_human_prompt]

review_prompt_template = ChatPromptTemplate(
    input_variables=["context", "question"],
    messages=messages,
)

# Step 4: Set up the ChatOpenAI model and output parser
chat_model = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0, max_tokens=200)
output_parser = StrOutputParser()

# Step 5: Create the review chain, incorporating the weighted context function
def create_weighted_review_context(question):
    reviews = reviews_retriever.retrieve({"query": question})
    weighted_context = apply_year_weight(reviews)
    return weighted_context

review_chain = (
    {"context": create_weighted_review_context, "question": RunnablePassthrough()}
    | review_prompt_template
    | chat_model
    | output_parser
)

# Step 6: Define tools, each of which can answer based on the database content
tools = [
    Tool(
        name="Reviews",
        func=review_chain.invoke,
        description="""Useful when you need to answer questions from the Chromadb database
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

# Step 8: Set up the agent with the OpenAI model and tools
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
        return jsonify({"answer": result["output"]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
if __name__ == "__main__":
    app.run(debug=True)
