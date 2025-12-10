const chatHistory = document.getElementById('chat-history');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');

// Connect to WebSocket
const ws = new WebSocket("ws://localhost:8081/ws");

let currentAiMessageDiv = null;

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);

    if (data.type === 'log') {
        // Show tool usage as system logs
        appendMessage(data.content, 'system-log');
    } 
    else if (data.type === 'token') {
        // Stream text token by token
        if (!currentAiMessageDiv) {
            currentAiMessageDiv = appendMessage('', 'ai-message');
        }
        currentAiMessageDiv.textContent += data.content;
        scrollToBottom();
    } 
    else if (data.type === 'end') {
        // Reset for next turn
        currentAiMessageDiv = null;
    }
};

function appendMessage(text, className) {
    const div = document.createElement('div');
    div.className = `message ${className}`;
    div.textContent = text;
    chatHistory.appendChild(div);
    scrollToBottom();
    return div;
}

function scrollToBottom() {
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

function sendMessage() {
    const text = userInput.value.trim();
    if (!text) return;

    // Display user message
    appendMessage(text, 'user-message');
    
    // Send to backend
    ws.send(JSON.stringify({ message: text }));
    
    userInput.value = '';
}

sendBtn.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});