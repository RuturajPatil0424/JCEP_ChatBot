import sqlite3

# Connect to SQLite database (creates 'chat_data.db' if it doesn't exist)
conn = sqlite3.connect("chat_data.db")
cursor = conn.cursor()

# Create a table for storing questions and answers
cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT NOT NULL,
        answer TEXT NOT NULL
    )
""")

# Commit changes and close the connection
conn.commit()
conn.close()

print("Database 'chat_data.db' created successfully with table 'chat_history'!")
