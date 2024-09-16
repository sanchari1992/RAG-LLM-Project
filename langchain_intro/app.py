import streamlit as st
import requests

# Set the title of the Streamlit app
st.title('Ask a Question')

# Create a text input for the user to enter their question
question = st.text_input("Enter your question:")

# Create a button that submits the question
if st.button('Submit'):
    if question:
        # Make a POST request to your Flask API with the question
        response = requests.post('http://127.0.0.1:5000/ask', json={"question": question})
        
        # Check if the request was successful
        if response.status_code == 200:
            # Display the answer from the API
            answer = response.json().get('answer', 'No answer received')
            st.write("Answer:", answer)
        else:
            st.write('Error:', response.text)
    else:
        st.write('Please enter a question.')
