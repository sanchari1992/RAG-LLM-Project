import streamlit as st
import requests

# Define the URL for your Flask API
API_URL = "http://127.0.0.1:5000/ask"

# Initialize session state to keep track of chat history
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Function to send a question to the Flask API and get the response
def get_response(question):
    response = requests.post(API_URL, json={"question": question})
    if response.status_code == 200:
        return response.json().get("answer", "No answer received.")
    else:
        return "Error occurred: " + response.text

# Streamlit UI
st.title("Chat with the Assistant")

# Display chat history
for msg in st.session_state.messages:
    if msg['type'] == 'user':
        st.write(f"**You**: {msg['text']}")
    else:
        st.write(f"**Assistant**: {msg['text']}")

# Input field for the user to type their message
user_input = st.text_input("You:", "")

# Button to submit the message
if st.button("Send"):
    if user_input:
        # Add user's message to the chat history
        st.session_state.messages.append({"type": "user", "text": user_input})
        
        # Get the response from the API
        response = get_response(user_input)
        
        # Add assistant's response to the chat history
        st.session_state.messages.append({"type": "assistant", "text": response})
        
        # Clear the input field
        st.text_input("You:", "", key="new_input")
