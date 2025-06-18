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

# --- Fetch questions and answer_ids only ---
def fetch_questions():
    conn = sqlite3.connect("DataBase/super_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT question, main_id FROM question_table")
    data = cursor.fetchall()
    conn.close()
    return data

# Store questions and corresponding answer_ids
question_data = fetch_questions()
questions, answer_ids = zip(*question_data) if question_data else ([], [])

# --- Create FAISS index ---
faiss_index = None

if questions:
    embeddings = model.encode(questions, convert_to_numpy=True)
    faiss_index = faiss.IndexFlatL2(embeddings.shape[1])
    faiss_index.add(np.array(embeddings))

def get_best_match(user_question, threshold=4.0, top_k=3):
    if not faiss_index or not questions:
        return None, None, None

    corrected = spell_correct(user_question)
    query_vec = model.encode([corrected])[0]
    D, I = faiss_index.search(np.array([query_vec]), k=top_k)

    for dist, idx in zip(D[0], I[0]):
        if dist < threshold:
            matched_q = questions[idx]
            matched_answer_id = answer_ids[idx]
            return matched_q, matched_answer_id, dist

    return None, None, None

# # --- Get the best matching question and its answer_id ---
# def get_best_match(user_question):
#     if not faiss_index or not questions:
#         return None, None, None
#
#     corrected = spell_correct(user_question)
#     query_vec = model.encode([corrected])[0]
#     D, I = faiss_index.search(np.array([query_vec]), k=1)
#
#     best_score = D[0][0]
#     best_idx = I[0][0]
#
#     if best_score < 1.0:
#         matched_q = questions[best_idx]
#         matched_answer_id = answer_ids[best_idx]
#         return matched_q, matched_answer_id, best_score
#     else:
#         return None, None, None

# --- Fetch answer using answer_id ---
def get_answer_by_id(answer_id):
    conn = sqlite3.connect("DataBase/super_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT answer FROM answer_table WHERE main_id = ?", (answer_id,))
    result = cursor.fetchone()
    print(result)
    conn.close()
    return result[0] if result else None

# # --- Build prompt ---
# def construct_prompt(context, question):
#     return f"""
#     ### System Role:
#     You are JCEP, an intelligent assistant trained to give accurate and helpful answers using the information below.
#
#     ### Provided Information:
#     {context}
#
#     ### User Question:
#     {question}
#
#     ### Instructions:
#     - Use the provided context as much as possible.
#     - If not directly answerable, respond politely with best effort.
#     - Be concise and clear.
#     """
def construct_prompt(context, question):
    return f"""You are JCEP clg ai chat bot, a precise assistant.

Answer the user's question using ONLY the provided information.

### Provided Information:
{context}

### User Question:
{question}

### Important Rules:
- DO NOT guess or assume anything not stated clearly.
- DO NOT explain or elaborate beyond what's in the context.
- If the context does not answer the question, say: "The answer is not available in the provided data."
- Be short, direct, and factual.
"""

# --- Query LLaMA ---
def ask_llama(prompt):
    model_name = 'llama3.2:3b'
    response = ollama.chat(model=model_name, messages=[{'role': 'user', 'content': prompt}])
    return response['message']['content']

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    data = request.get_json()
    user_input = data.get("message")

    if not user_input:
        return jsonify({"response": "Please provide a question."})

    matched_q, matched_answer_id, score = get_best_match(user_input)

    print(matched_q)

    if not matched_q or not matched_answer_id:
        return jsonify({"response": "Sorry, I couldn't find a relevant answer."})

    matched_answer = get_answer_by_id(matched_answer_id)

    if not matched_answer:
        return jsonify({"response": "Answer data missing for matched question."})

    prompt = construct_prompt(matched_answer, user_input)
    llama_response = ask_llama(prompt)

    return jsonify({"response": llama_response})

if __name__ == '__main__':
    app.run(debug=True)
