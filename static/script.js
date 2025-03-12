function sendMessage() {
    const userInput = document.getElementById('user-input').value;
    if (userInput.trim() === "") return;

    // Display user message in the chatbox
    displayMessage(userInput, 'user');

    // Send user input to Flask backend
    fetch('/get_response', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message: userInput })
    })
    .then(response => response.json())
    .then(data => {
        displayMessage(data.response, 'bot');
    })
    .catch(error => console.error('Error:', error));

    // Clear input box
    document.getElementById('user-input').value = "";
}

function displayMessage(message, sender) {
    const chatBox = document.getElementById('chat-box');
    const messageElement = document.createElement('div');
    messageElement.classList.add(sender === 'user' ? 'user-message' : 'bot-message');
    messageElement.textContent = message;
    chatBox.appendChild(messageElement);

    // Scroll to latest message
    chatBox.scrollTop = chatBox.scrollHeight;
}

function handleEnter(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}

let isChatbotOpen = false;

function toggleChatbot() {
    const chatContainer = document.getElementById('chat-container');

    if (isChatbotOpen) {
        chatContainer.style.right = '-420px'; // Hide
    } else {
        chatContainer.style.right = '20px'; // Show
    }

    isChatbotOpen = !isChatbotOpen;
}

// Function to display developer information
function showInfo() {
    alert("Software Developed By:\n- Vishwajeet Yadav\n- Omkar Patil\n- Gautami Pawar\n- Dipali Mane\n\nUnder the guidance of:\n- Mr. S.Y. Inamader");
}

// Handle "Enter" key press
function handleEnter(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
}