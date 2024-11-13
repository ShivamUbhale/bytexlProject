const socket = io.connect('http://localhost:5000');  // Assuming you're using Socket.io

// Send a message
document.getElementById('send-message').addEventListener('click', function() {
    const message = document.getElementById('message-input').value;
    if (message) {
        socket.emit('send_message', {
            message: message,
            to: matchUserId  // The ID of the matched user
        });
        document.getElementById('message-input').value = '';  // Clear input field
    }
});

// Receive a message
socket.on('receive_message', function(data) {
    const messageContainer = document.getElementById('messages');
    const newMessage = document.createElement('div');
    newMessage.classList.add('message');
    newMessage.textContent = data.message;
    messageContainer.appendChild(newMessage);
});
