import os
import shutil
import dotenv
from flask import Flask, request, jsonify
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, OpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

# Load environment variables from .env
dotenv.load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Paths for Chroma persistence directory
CHROMA_PERSIST_PATH = "chroma_data"

# Step 1: Load the existing Chroma DB
reviews_vector_db = Chroma(
    persist_directory=CHROMA_PERSIST_PATH,
    embedding_function=OpenAIEmbeddings()
)

# Step 2: Define the custom prompt template to restrict answers to database data
prompt_template = """
You are an AI assistant specialized in mental health therapy center reviews from Birmingham, Alabama.
Only answer questions based on the data provided. If the answer is not in the data, respond with "I don't know".

Question: {question}

Answer:
"""

# Step 3: Create the QA chain using the Chroma database as a retriever and GPT as the model
qa_chain = RetrievalQA.from_chain_type(
    llm=OpenAI(model="gpt-3.5-turbo-0125"),
    retriever=reviews_vector_db.as_retriever(),
    chain_type="stuff",  # This uses the default question-answering chain
    return_source_documents=False,  # If you want to see source documents, set this to True
    prompt=PromptTemplate(input_variables=["question"], template=prompt_template)
)

# Step 4: Define the POST route for asking questions
@app.route("/ask", methods=["POST"])
def ask_question():
    try:
        data = request.json
        question = data.get("question", "")
        
        # Use the agent to process the question
        result = qa_chain({"question": question})
        
        return jsonify({"answer": result["result"]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Step 5: Run the Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
