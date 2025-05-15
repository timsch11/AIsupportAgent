const messages = document.getElementById('chat-messages');
let currentRequestData = null;

function fetchAnalysis(message) {
    // Show loading indicator
    const loadingElement = document.createElement('div');
    loadingElement.className = 'message bot-message loading';
    loadingElement.textContent = 'Analyzing...';
    messages.appendChild(loadingElement);

    console.log(JSON.stringify({ message: message }))
    
    fetch('/analyze', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ content: message })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        // Remove loading indicator
        messages.removeChild(loadingElement);
        
        // Display the "Antwort" field from the response
        if (data && data.Antwort) {
            appendMessage('bot', data.Antwort);
            
            // Check if there's category and username data
            if (data.Kategorie || data.Benutzer) {
                // Store the current request data
                currentRequestData = {
                    category: data.Kategorie || '',
                    username: data.Benutzername || ''
                };
                
                // Show and populate the request info panel
                showRequestInfo(currentRequestData.category, currentRequestData.username);
            }
        } else {
            appendMessage('bot', 'Sorry, I could not process your request.');
        }
    })
    .catch(error => {
        // Remove loading indicator
        messages.removeChild(loadingElement);
        
        console.error('Error:', error);
        appendMessage('bot', 'An error occurred while processing your request.');
    });
}

function appendMessage(sender, text) {
    const messageElement = document.createElement('div');
    messageElement.className = `message ${sender}-message`;
    
    const textElement = document.createElement('p');
    textElement.textContent = text;
    messageElement.appendChild(textElement);
    
    messages.appendChild(messageElement);
    
    // Scroll to the bottom of the chat
    messages.scrollTop = messages.scrollHeight;
}

function showRequestInfo(category, username) {
    const requestInfoPanel = document.getElementById('request-info-panel');
    const requestTypeInput = document.getElementById('request-type');
    const usernameInput = document.getElementById('username');
    
    // Set values
    requestTypeInput.value = category;
    usernameInput.value = username;
    
    // Show the panel
    requestInfoPanel.style.display = 'block';
}

function hideRequestInfo() {
    const requestInfoPanel = document.getElementById('request-info-panel');
    requestInfoPanel.style.display = 'none';
    currentRequestData = null;
}

function submitAction() {
    const requestType = document.getElementById('request-type').value;
    const username = document.getElementById('username').value;
    
    // Create action data to send to the server
    const actionData = {
        category: requestType,
        username: username,
        // Add any other necessary data
    };
    
    // Show user confirmation in chat
    appendMessage('user', `Confirming action: ${requestType} for user: ${username}`);
    
    // Send data to server
    fetch('/execute-action', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(actionData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            appendMessage('bot', `Action completed successfully: ${data.message}`);
        } else {
            appendMessage('bot', `Failed to complete action: ${data.message}`);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        appendMessage('bot', 'An error occurred while processing your request.');
    })
    .finally(() => {
        hideRequestInfo();
    });
}

document.addEventListener("DOMContentLoaded", function() {
    const exploreBtn = document.getElementById("exploreBtn");
    if (exploreBtn) {
        exploreBtn.addEventListener("click", function() {
            alert("Welcome to our automated booking system! Let's get started.");
        });
    }

    const sendButton = document.getElementById('send-button');
    const input = document.getElementById('user-input');

    sendButton.addEventListener('click', function(e) {
        e.preventDefault();
        const message = input.value.trim();
        if (!message) return;
        
        // Add user message to chat
        appendMessage('user', message);
        input.value = '';
        
        // Send message to API
        fetchAnalysis(message);
    });
    
    // Set up input to submit on Enter key
    input.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendButton.click();
        }
    });
    
    // Confirm action button
    const confirmButton = document.getElementById('confirm-action');
    confirmButton.addEventListener('click', function() {
        submitAction();
    });
    
    // Cancel action button
    const cancelButton = document.getElementById('cancel-action');
    cancelButton.addEventListener('click', function() {
        hideRequestInfo();
        appendMessage('user', 'Action cancelled');
    });
});
