from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import sqlite3
# List of available questions
q_list = []
# questions = [
#     "What is AI?",
#     "How does machine learning work?",
#     "Explain the difference between supervised and unsupervised learning.",
#     "What are the advantages of deep learning?",
#     "What is reinforcement learning?",
#     "Who is the managing trustee of this college?"
# ]


# Function to get the best match using cosine similarity
def get_best_match(user_input):
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([user_input] + q_list)
    similarity = cosine_similarity(vectors[0:1], vectors[1:]).flatten()

    best_match_idx = similarity.argmax()
    best_score = similarity[best_match_idx]

    if best_score >= 0.5:  # Adjust threshold as needed
        return q_list[best_match_idx]
    else:
        return "No relevant match found."


def fetch_data_answers():
    conn = sqlite3.connect("../DataBase/chat_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT question, answer FROM chat_history")
    data = cursor.fetchall()  # Fetch all (question, answer) pairs
    conn.close()

    # Convert to dictionary
    qa_dict = {question: answer for question, answer in data}
    return qa_dict



def fetch_questions_answers():
    conn = sqlite3.connect("../DataBase/chat_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT question, answer FROM chat_history")
    data = cursor.fetchall()  # Fetch all (question, answer) pairs
    conn.close()
    return data

def create_qlist(data):
    q_list.clear()
    for i in data:
        q_list.append(i[0])


# Example usage
qa_dict = fetch_questions_answers()
# Example usage
data = fetch_questions_answers()  # Load questions & answers
create_qlist(data)
data_dic = fetch_data_answers()
print(data_dic)

while __name__ == "__main__":
    user_input = input("Ask a question: ")
    match = get_best_match(user_input)
    print(match)
    print(data_dic[match])
