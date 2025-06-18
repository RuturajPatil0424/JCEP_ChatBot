from flask import Flask, request, jsonify, render_template
import sqlite3
import ollama
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os

app = Flask(__name__)
# Serve HTML file
@app.route('/')
def index():
    return render_template('index.html')

# Load questions and answers from the database
def fetch_questions_answers():
    conn = sqlite3.connect("DataBase/chat_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT question, answer FROM chat_history")
    data = cursor.fetchall()
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

# Load data into q_list
q_list = []
def create_qlist(data):
    q_list.clear()
    for i in data:
        q_list.append(i[0])


# Construct prompt for LLaMA model
def Construct_prompt(content, questions):
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
    return prompt

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

# Send query to fine-tuned LLaMA model
def ask_finetuned_llama(questionToAsk):
    desiredModel = 'llama3.2:3b'
    response = ollama.chat(model=desiredModel, messages=[{'role': 'user', 'content': f'{questionToAsk}'}])
    OllamaResponse = response['message']['content']
    return OllamaResponse

data = fetch_questions_answers()  # Load questions & answers
create_qlist(data)
data_dic = fetch_data_answers()
# Handle user input
@app.route('/get_response', methods=['POST'])
def get_response():

    data = request.get_json()
    user_input = data.get("message")

    if not user_input:
        return jsonify({"response": "Please provide a question."})

    else:
        match = get_best_match(user_input)
        if "No relevant match found" in str(match):
            response = "Sorry, I couldn't understand your question."
            return jsonify({"response": response})

        else:
            d_answer = data_dic[match]
            f_prompt = Construct_prompt(d_answer, user_input)
            answer = ask_finetuned_llama(f_prompt)

            if answer:
                prompt = Construct_prompt(answer, user_input)
                response = ask_finetuned_llama(prompt)
            else:
                response = "Sorry, I couldn't understand your question."

            return jsonify({"response": response})




if __name__ == '__main__':
    app.run(debug=True)
