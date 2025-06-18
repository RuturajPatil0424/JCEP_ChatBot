from flask import Flask, request, jsonify, render_template
import sqlite3
import ollama
import os
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from spellchecker import SpellChecker

app = Flask(__name__)

# --- Load sentence transformer ---
model = SentenceTransformer('all-MiniLM-L6-v2')  # Lightweight and fast

# --- Spell corrector ---
spell = SpellChecker()

def spell_correct(text):
    return " ".join([spell.correction(w) or w for w in text.split()])

# --- Load and embed DB questions ---
def fetch_questions_answers():
    conn = sqlite3.connect("DataBase/chat_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT question, answer FROM chat_history")
    data = cursor.fetchall()
    conn.close()
    return data

data = fetch_questions_answers()
questions, answers = zip(*data)

# Embed and store in FAISS index
embeddings = model.encode(questions, convert_to_numpy=True)
index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(np.array(embeddings))

# Question-answer mapping
qa_dict = dict(zip(questions, answers))

@app.route('/')
def index():
    return render_template('index.html')

def get_top_match(user_question):
    corrected = spell_correct(user_question)
    query_vec = model.encode([corrected])[0]
    D, I = index.search(np.array([query_vec]), k=1)

    best_score = D[0][0]
    best_idx = I[0][0]

    if best_score < 1.0:  # Low distance = high similarity
        matched_q = questions[best_idx]
        return matched_q, qa_dict[matched_q]
    else:
        return None, None

def construct_prompt(context, question):
    return f"""
    ### System Role:
    You are JCEP, an intelligent assistant trained to give accurate and helpful answers using the information below.

    ### Provided Information:
    {context}

    ### User Question:
    {question}

    ### Instructions:
    - Use the provided context as much as possible.
    - If not directly answerable, respond politely with best effort.
    - Be concise and clear.
    """

def ask_llama(prompt):
    model_name = 'llama3:3b'
    response = ollama.chat(model=model_name, messages=[{'role': 'user', 'content': prompt}])
    return response['message']['content']

@app.route('/get_response', methods=['POST'])
def get_response():
    data = request.get_json()
    user_input = data.get("message")

    if not user_input:
        return jsonify({"response": "Please provide a question."})

    matched_q, matched_a = get_top_match(user_input)

    if not matched_q:
        return jsonify({"response": "Sorry, I couldn't find a relevant answer."})

    prompt = construct_prompt(matched_a, user_input)
    llama_response = ask_llama(prompt)

    return jsonify({"response": llama_response})

if __name__ == '__main__':
    app.run(debug=True)