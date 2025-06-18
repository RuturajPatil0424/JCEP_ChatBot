import sqlite3
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import ollama
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

q_list = []

def get_best_match(user_input):
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([user_input] + q_list)
    similarity = cosine_similarity(vectors[0:1], vectors[1:]).flatten()

    best_match_idx = similarity.argmax()
    best_score = similarity[best_match_idx]

    if best_score >= 0.4:  # Adjust threshold as needed
        return q_list[best_match_idx]
    else:
        return "No relevant match found."

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
       - If an answer is found in the provided information, use that.
       - If an answer is missing in information, use your own knowledge.
       - Keep responses clear and well-structured.
       """
    # - Keep responses clear and well-structured and dont mention in answer information is provided you.
    return prompt


def ask_finetuned_llama(questionToAsk):
    desiredModel = 'llama3.2:3b'

    responce = ollama.chat(model=desiredModel, messages=[{'role': 'user', 'content': f'{questionToAsk}'}])
    OllamaResponse = responce['message']['content']
    with open("Outputfile.txt", "w", encoding="utf-8") as text_file:
        text_file.write(OllamaResponse)
    return (OllamaResponse)


# Function to fetch all questions and answers from the database
def fetch_questions_answers():
    conn = sqlite3.connect("DataBase/chat_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT question, answer FROM chat_history")
    data = cursor.fetchall()  # Fetch all (question, answer) pairs
    conn.close()
    return data

def fetch_data_answers():
    conn = sqlite3.connect("DataBase/chat_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT question, answer FROM chat_history")
    data = cursor.fetchall()  # Fetch all (question, answer) pairs
    conn.close()

    # Convert to dictionary
    qa_dict = {question: answer for question, answer in data}
    return qa_dict


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
    data_dic = fetch_data_answers()
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        match = get_best_match(user_input)
        print(match)
        d_answer = data_dic[match]
        f_prompt = Construct_prompt(d_answer,user_input)
        answer = ask_finetuned_llama(f_prompt)
        print(answer)

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
