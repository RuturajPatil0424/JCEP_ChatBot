# JCEP Chatbot

## Overview
JCEP is an intelligent chatbot designed to answer user queries using a combination of a fine-tuned Llama model and a local SQLite database. It attempts to match user queries with stored questions and answers and, if necessary, generates a response using an AI model.

## Features
- Uses SQLite to store and retrieve historical chat data.
- Employs fuzzy matching with `fuzzywuzzy` to find the best-matching question.
- If a match is found, it retrieves and refines the answer using a fine-tuned Llama model (`ollama`).
- If no match is found, it constructs a prompt and queries the Llama model for a response.
- Saves chatbot responses to `Outputfile.txt`.

## Requirements
Ensure you have the following installed:
- Python 3.x
- SQLite3
- `fuzzywuzzy`
- `ollama`
- `sqlite3`

To install dependencies, run:
```sh
pip install fuzzywuzzy[speedup] ollama
```

## File Structure
- `chat_data.db` - SQLite database storing chat history.
- `Outputfile.txt` - Stores the chatbot's responses.
- `main.py` - The chatbot script.

## How It Works
1. The chatbot loads existing question-answer pairs from `chat_data.db`.
2. It listens for user input.
3. It tries to find a closely matching question from the database using `fuzzywuzzy`.
4. If a match is found, it returns the stored answer, refining it with `ollama`.
5. If no match is found, it queries `ollama` directly.
6. The chatbot displays the response and logs it.
7. The conversation continues until the user types `exit`.

## Running the Chatbot
To start the chatbot, run:
```sh
python main.py
```

## Customization
- **Threshold Adjustment**: Change the confidence threshold (`90`) in `find_best_match()` to fine-tune matching sensitivity.
- **Database Path**: Modify the `sqlite3.connect()` line to point to a different database file.
- **Fine-Tuned Model**: Replace `'jcepai'` with your preferred model name in `ask_finetuned_llama()`.

## Notes
- Ensure `chat_data.db` exists and has a `chat_history` table with `question` and `answer` columns.
- The chatbot requires `ollama` to be properly set up.
- Modify `Construct_prompt()` to customize prompt formatting for the AI model.

## License
This project is for educational and personal use. Modify and distribute as needed.

