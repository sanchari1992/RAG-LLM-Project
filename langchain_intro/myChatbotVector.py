from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
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
from tools import get_current_wait_time

# Load environment variables
dotenv.load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

REVIEWS_CHROMA_PATH = "chroma_data/"

# Define the review templates
review_template_str = """You are restricted to using ONLY the database entries provided to you.
Do not answer any questions based on your own knowledge or any external sources. 
You must base your answer entirely on the provided context. 

If the context does not contain the information needed to answer the question, 
respond with 'I don't know'. 

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

chat_model = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)
output_parser = StrOutputParser()

# Initialize Chroma vector DB for reviews
reviews_vector_db = Chroma(
    persist_directory=REVIEWS_CHROMA_PATH,
    embedding_function=OpenAIEmbeddings()
)

reviews_retriever = reviews_vector_db.as_retriever(k=10)

review_chain = (
    {"context": reviews_retriever, "question": RunnablePassthrough()}
    | review_prompt_template
    | chat_model
    | output_parser
)

tools = [
    Tool(
        name="Reviews",
        func=review_chain.invoke,
        description="""Useful when you need to answer questions
        about the top 20 applications on the Google Play Store from the data in the database.
        Useful for answering questions from the available reviews. Also useful to frame 
        answers gathered from the information within the reviews, such as feedback.
        Pass the entire question as input to the tool. For instance,
        if the question is "Which social networking application do people prefer?",
        the input should be "Which social networking application do people prefer?"
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
