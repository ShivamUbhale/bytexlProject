// Send match request to another user
function sendMatchRequest(userId) {
    fetch(`/send_match_request/${userId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
    });
}

// Accept a match request
function acceptMatch(requestId) {
    fetch(`/accept_match/${requestId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        window.location.reload();  // Reload the page to update match status
    });
}

// Decline a match request
function declineMatch(requestId) {
    fetch(`/decline_match/${requestId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        window.location.reload();  // Reload the page to update match status
    });
}

// Start a chat with a matched user
function startChat(matchId) {
    window.location.href = `/chat/${matchId}`;
}
