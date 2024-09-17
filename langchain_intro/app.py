import streamlit as st
import requests

# Define the URL for your Flask API
API_URL = "http://127.0.0.1:5000/ask"

# Initialize session state to keep track of chat history and input
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'waiting_for_response' not in st.session_state:
    st.session_state.waiting_for_response = False

# Function to send a question to the Flask API and get the response
def get_response(question):
    try:
        response = requests.post(API_URL, json={"question": question})
        if response.status_code == 200:
            return response.json().get("answer", "No answer received.")
        else:
            return "Error occurred: " + response.text
    except Exception as e:
        return "Request failed: " + str(e)

# Streamlit UI
st.title("Chat with the Assistant")

# Create a placeholder for chat history
chat_placeholder = st.empty()

# Display chat history function
def display_chat_history():
    chat_placeholder.empty()  # Clear previous chat history
    for msg in st.session_state.messages:
        if msg['type'] == 'user':
            st.write(f"**You**: {msg['text']}")
        else:
            st.write(f"**Assistant**: {msg['text']}")

# Input field for the user to type their message
user_input = st.text_input("You:", value="")

# Button to submit the message
if st.button("Send"):
    if user_input and not st.session_state.waiting_for_response:
        # Add user's message to the chat history
        st.session_state.messages.append({"type": "user", "text": user_input})
        
        # Disable the input field and show a loading spinner
        st.session_state.waiting_for_response = True

        # Display chat history before waiting for the response
        display_chat_history()
        
        # Get the response from the API
        with st.spinner('Waiting for response...'):
            response = get_response(user_input)
        
        # Add assistant's response to the chat history
        st.session_state.messages.append({"type": "assistant", "text": response})
        
        # Reset input field and waiting state
        st.session_state.waiting_for_response = False
        # Update chat history again after adding response
        display_chat_history()
        
        # Clear input field by setting it to an empty string
        st.session_state.user_input = ""
