import json
import sqlite3

# Load JSON data from the file
json_file_path = "jcepdata.json"
with open(json_file_path, "r", encoding="utf-8") as file:
    data = json.load(file)

# Connect to SQLite database
conn = sqlite3.connect("chat_data.db")
cursor = conn.cursor()

# Create a table to store questions and answers
cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT UNIQUE,
        answer TEXT
    )
""")

# Extract and insert data into the database
for conversation in data:
    messages = conversation.get("conversations", [])
    user_question = None
    assistant_answer = None

    for msg in messages:
        if msg["role"] == "user":
            user_question = msg["content"]
        elif msg["role"] == "assistant":
            assistant_answer = msg["content"]

        # Insert into database only if the question does not already exist
        if user_question and assistant_answer:
            cursor.execute("SELECT COUNT(*) FROM chat_history WHERE question = ?", (user_question,))
            exists = cursor.fetchone()[0]

            if exists == 0:
                cursor.execute("INSERT INTO chat_history (question, answer) VALUES (?, ?)",
                               (user_question, assistant_answer))

            user_question = None  # Reset for next entry

# Commit changes and close the connection
conn.commit()
conn.close()

print("Data successfully stored in SQLite database! (No duplicates added)")
