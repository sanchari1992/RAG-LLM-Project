import os
from langchain_openai import ChatOpenAI

# Initialize the OpenAI model
model = ChatOpenAI(model="gpt-3.5-turbo")  # Specify your model here

def evaluate_answer(question, answer):
    prompt = (
        f"Evaluate the following answer to the question on a scale of 0 to 5, "
        f"where 0 means the answer does not adhere to the question at all, "
        f"and 5 means the answer perfectly adheres to the question.\n\n"
        f"Question: {question}\n"
        f"Answer: {answer}\n"
        f"Rating (0-5):"
    )
    prompt = f"""
    Evaluate the following answer to the question on a scale of 0 to 5, 
    where 0 means the answer does not adhere to the question at all, 
    and 5 means the answer perfectly adheres to the question.
    Question: {question}\n
    Answer: {answer}\n
    Rating (0-5):

    Respond with only the numbers for each category, one per line, or "0" if a category is not mentioned in the comment.

    Example:
    Question:"Does Alabama Psychiatry and Counseling have generally good rankings in the reviews?"
    Answer:"There are no reviews or comments available for 'Alabama Psychiatry and Counseling' in the database provided."
    Rating: 0
    
    Question:"Are the staff at Eastside Mental Health considered friendly by reviewers?"
    Answer:"The reviews about the staff at Eastside Mental Health are mixed. Some reviewers have positive interactions with staff members like Dr. Yulia Spencer and Neal Tillman, who are described as caring and helpful. However, there are also negative comments mentioning issues like high turnover of doctors, concerns about nurse practitioners prescribing medications, and dissatisfaction with the level of care provided."
    Rating: 3
    """
    
    response = model.predict(prompt)  # Get the model's response
    return response.strip()  # Clean up the response

def process_file(input_file, output_folder):
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Prepare output file path
    output_file = os.path.join(output_folder, os.path.basename(input_file))

    with open(input_file, 'r') as file:
        lines = file.readlines()

    with open(output_file, 'w') as outfile:
        for i in range(len(lines)):
            line = lines[i].strip()
            if line.startswith('P'):  # Question line
                question = line.split('""')[1]  # Extract the question
                if i + 1 < len(lines):  # Check if the next line exists
                    answer = lines[i + 1].strip().split('""')[1]  # Extract the answer
                    rating = evaluate_answer(question, answer)  # Get the rating
                    outfile.write(f"{line}\nAP{line[1]}\"{rating}\"\n")  # Write to output

if __name__ == "__main__":
    # Define the input and output paths
    input_folder_path = "langchain_intro/responses"
    output_folder_path = "langchain_intro/scaled_Responses"

    # Prompt user for the filename to process
    input_file_name = input("Enter the filename to process (including extension, e.g., 'file.txt'): ")

    # Construct the full input file path
    input_file_path = os.path.join(input_folder_path, input_file_name)

    # Check if the file exists
    if os.path.isfile(input_file_path):
        process_file(input_file_path, output_folder_path)
        print(f"Processed: {input_file_name}")
    else:
        print(f"File '{input_file_name}' not found in '{input_folder_path}'. Please check the filename and try again.")
