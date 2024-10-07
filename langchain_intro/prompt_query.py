import requests
import json
import time
from datetime import datetime

# Function to extract questions from the input file
def extract_questions(input_file):
    questions = []
    with open(input_file, 'r') as file:
        lines = file.readlines()
        is_question_section = False
        for line in lines:
            line = line.strip()
            if line == "*****":
                if is_question_section:
                    break
                else:
                    is_question_section = True
            elif is_question_section:
                questions.append(line)
    return questions

# Function to make POST request to the API for each question
def get_answers(questions):
    api_url = "http://127.0.0.1:5000/ask"
    headers = {"Content-Type": "application/json"}
    answers = []

    for question in questions:
        try:
            question_number, question_text = question.split('.', 1)
            question_payload = {"question": question_text.strip()}
            
            # Sending POST request and waiting for response
            response = requests.post(api_url, headers=headers, data=json.dumps(question_payload), timeout=300)
            
            if response.status_code == 200:
                answer_data = response.json()
                answer = answer_data.get("answer", "No answer received.")
            else:
                answer = "Failed to get answer."

            answers.append(f"{question_number}.\"{question_text.strip()}\"\nA1.\"{answer}\"\n")
        except Exception as e:
            answers.append(f"{question_number}.\"{question_text.strip()}\"\nA1.\"Error: {str(e)}\"\n")
    return answers

# Function to write responses to the output file
def write_responses(questions, answers, output_file):
    current_time = datetime.now().strftime("%H:%M:%S")
    current_date = datetime.now().strftime("%Y-%m-%d")

    with open(output_file, 'w') as file:
        file.write(f"Responses: Time: {current_time} Date: {current_date}\n")
        file.write("*****\n")
        
        for question, answer in zip(questions, answers):
            file.write(f"{question}\n{answer}")
            file.write("*****\n")

if __name__ == "__main__":
    # Ask user for the input file name
    input_file = input("Please enter the name of the input file (with extension): ")
    input_file = "./prompts/" + input_file

    # Generate the output file name based on current datetime
    current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"response_{current_datetime}.txt"
    output_file = "./responses/" + output_file
    
    # Extract questions from the input file
    questions = extract_questions(input_file)

    # Get answers by sending POST requests
    answers = get_answers(questions)

    # Write the responses to the output file
    write_responses(questions, answers, output_file)

    print(f"Responses have been written to {output_file}")
