import sqlite3
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import ollama

q_list = []
def Construct_prompt(content, questions):
    # Construct the formatted prompt
    prompt = f"""
    ### System Role:
    You are JCEP, an intelligent chatbot designed to provide accurate answers based on the given information. If the answer is not available in the provided content, use your own knowledge to respond.

    ### Provided Information:
    {content}

    ### Questions:
    {questions}

    ### Response Instructions:
    - Analyze the user's input carefully.  
    - Understand the intent behind the user's input.  
    - Match the user's input with the most relevant question from the list.  
    - Ignore minor spelling mistakes or variations.  
    - Respond ONLY with the exact matched question or "No relevant match found."  
    - If none of the questions are relevant, respond with "No relevant match found."  
    - Keep responses clear and well-structured.
    - dont give Explanation and user input, give only matched relevant question from list in Response.
    """
    # - Keep responses clear and well-structured and dont mention in answer information is provided you.
    return prompt

def q_match_prompt(questionslist,user_input):
    print(questionslist)
    formatted_questions = "\n".join([f"{i + 1}. {q}" for i, q in enumerate(questionslist)])

    Q_Prompt = f"""System Role:
You are an AI model designed to match user input to the closest relevant question from a list.

### Provided Questions:
{formatted_questions}

### User Input:
{user_input}

### Instructions:
- Carefully analyze the user's input.  
- Focus on the meaning and intent of the user input rather than exact wording.  
- Match the input to the most relevant question from the list, even if there are spelling mistakes or incomplete phrases.  
- Respond ONLY with the exact matched question or "No relevant match found."  
- If none of the questions are relevant, respond with "No relevant match found."  
- Do NOT provide any explanation or include the user input in the response — return only the matched question from the list.  
- The response should ONLY one the matched question — no additional text or explanation.  

### Example:
**User Input:** managing trustee  
**Response:** Who is the managing trustee of this college?  
    """
    return Q_Prompt

def ask_finetuned_llama(questionToAsk):
    desiredModel = 'llama3.2:1b'

    responce = ollama.chat(model=desiredModel, messages=[{'role': 'user', 'content': f'{questionToAsk}'}])
    OllamaResponse = responce['message']['content']
    with open("../Outputfile.txt", "w", encoding="utf-8") as text_file:
        text_file.write(OllamaResponse)
    return (OllamaResponse)


# Function to fetch all questions and answers from the database
def fetch_questions_answers():
    conn = sqlite3.connect("../DataBase/chat_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT question, answer FROM chat_history")
    data = cursor.fetchall()  # Fetch all (question, answer) pairs
    conn.close()
    return data


# Function to find the best match for user input
def find_best_match(user_input, data):
    questions = [q[0] for q in data]  # Extract all questions
    best_match, score = process.extractOne(user_input, questions, scorer=fuzz.partial_ratio)

    if score > 70:  # Confidence threshold (adjustable)
        for question, answer in data:
            if question == best_match:
                return answer, best_match, score
    return None, None, None

def create_qlist(data):
    q_list.clear()
    for i in data:
        q_list.append(i[0])


# Chatbot function
def chatbot():
    print("Chatbot is ready! Type 'exit' to quit.")
    data = fetch_questions_answers()  # Load questions & answers
    create_qlist(data)
    print(q_list)


    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        print(data)
        finput = q_match_prompt(q_list,user_input)
        # print(finput)
        answer = ask_finetuned_llama(finput)
        print(answer)

        # answer, best_match, score = find_best_match(user_input, data)
        # print(answer)
        #
        # if answer:
        #     # print(answer)
        #     # print(user_input)
        #     prompt = Construct_prompt(answer, user_input)
        #     # print(prompt)
        #     answers = ask_finetuned_llama(prompt)
        #     # print(f"\nChatbot (Matched: {best_match} [Score: {score}]): {answer}")
        #     print(answers)
        # else:
        #     prompt = Construct_prompt(answer, user_input)
        #     # print(prompt)
        #     answers = ask_finetuned_llama(prompt)
        #     print(answers)
        #     print("\nChatbot: Sorry, I couldn't understand your question.")


# Run the chatbot
chatbot()
