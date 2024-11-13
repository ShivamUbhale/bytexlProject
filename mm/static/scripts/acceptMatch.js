function acceptMatch(requestId, senderId) {
    fetch('/accept-match-request', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ requestId: requestId })
    }).then(response => {
        if (response.ok) {
            alert('Match accepted!');
            // Redirect to the chat page with the matched user's ID (senderId)
            window.location.href = `/chat/${senderId}`;
        } else {
            alert('Error accepting the match request.');
        }
    }).catch(error => {
        console.error('Error:', error);
    });
}
