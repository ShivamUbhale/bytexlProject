import bcrypt
from bson.objectid import ObjectId
from app import mongo
from datetime import datetime

# Utility function to hash passwords
def hash_password(password):
    """
    Hash the password using bcrypt for secure storage.
    """
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed

# Utility function to check if a password is correct
def check_password(hashed_password, password):
    """
    Check if the provided password matches the stored hashed password.
    """
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)

# Utility function to find a user by email
def get_user_by_email(email):
    """
    Get user data by email from the database.
    """
    return mongo.db.users.find_one({'email': email})

# Utility function to find a user by ID
def get_user_by_id(user_id):
    """
    Get user data by ID from the database.
    """
    return mongo.db.users.find_one({'_id': ObjectId(user_id)})

# Utility function to update user profile
def update_user_profile(user_id, photos=None, songs=None, bio=None):
    """
    Update user profile data (photos, songs, bio).
    """
    update_data = {}
    if photos is not None:
        update_data['photos'] = photos
    if songs is not None:
        update_data['songs'] = songs
    if bio is not None:
        update_data['bio'] = bio

    if update_data:
        mongo.db.users.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': update_data}
        )

# Utility function to create a match request
def create_match_request(sender_id, receiver_id):
    """
    Create a match request between two users.
    """
    # Check if there is already an existing match request between the users
    existing_request = mongo.db.match_requests.find_one({
        '$or': [
            {'sender_id': sender_id, 'receiver_id': receiver_id},
            {'sender_id': receiver_id, 'receiver_id': sender_id}
        ],
        'status': {'$in': ['pending', 'accepted']}
    })

    if existing_request:
        return None  # A request already exists or the match is already made

    # Create a new match request
    match_request = {
        'sender_id': sender_id,
        'receiver_id': receiver_id,
        'status': 'pending',
        'created_at': datetime.utcnow()  # Store the time when the request is created
    }

    result = mongo.db.match_requests.insert_one(match_request)
    return result.inserted_id

# Utility function to accept a match request
def accept_match_request(match_request_id):
    """
    Accept a match request.
    """
    match_request = mongo.db.match_requests.find_one({'_id': ObjectId(match_request_id)})

    if match_request and match_request['status'] == 'pending':
        # Update the match request to 'accepted'
        mongo.db.match_requests.update_one(
            {'_id': ObjectId(match_request_id)},
            {'$set': {'status': 'accepted'}}
        )

        # Add each user to the other's 'matches' list
        sender = match_request['sender_id']
        receiver = match_request['receiver_id']

        # Add each user to the other's matches
        mongo.db.users.update_one(
            {'_id': ObjectId(sender)},
            {'$addToSet': {'matches': receiver}}
        )
        mongo.db.users.update_one(
            {'_id': ObjectId(receiver)},
            {'$addToSet': {'matches': sender}}
        )

        return True
    return False

# Utility function to reject a match request
def reject_match_request(match_request_id):
    """
    Reject a match request.
    """
    mongo.db.match_requests.update_one(
        {'_id': ObjectId(match_request_id)},
        {'$set': {'status': 'rejected'}}
    )
    return True

# Utility function to fetch a user's matches
def get_user_matches(user_id):
    """
    Fetch all accepted match requests for a user.
    """
    matches = mongo.db.match_requests.find({
        '$or': [{'sender_id': user_id}, {'receiver_id': user_id}],
        'status': 'accepted'
    })
    return list(matches)

# Utility function to get user match history
def get_chat_history(match_id):
    """
    Get all messages between two users (chat history).
    """
    return list(mongo.db.chats.find({'match_id': match_id}).sort('timestamp', 1))

# Utility function to create a chat message
def create_chat_message(match_id, sender_id, message):
    """
    Create and save a new chat message.
    """
    chat_data = {
        'match_id': match_id,
        'sender_id': sender_id,
        'message': message,
        'timestamp': datetime.utcnow()
    }
    result = mongo.db.chats.insert_one(chat_data)
    return result.inserted_id

# Utility function to prioritize profiles based on music
def prioritize_profiles_by_music(user_id):
    """
    Prioritize users with similar music preferences on the dashboard.
    This compares the songs in their profiles and finds matches.
    """
    user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
    if not user:
        return []

    user_songs = set(user['songs'])
    all_users = mongo.db.users.find()
    
    prioritized_profiles = []

    for other_user in all_users:
        if other_user['_id'] != ObjectId(user_id):  # Skip the current user
            # Compare music choices with other users
            other_user_songs = set(other_user['songs'])
            common_songs = user_songs.intersection(other_user_songs)
            similarity_score = len(common_songs)

            if similarity_score > 0:  # Only prioritize users with common songs
                prioritized_profiles.append({
                    'user': other_user,
                    'similarity_score': similarity_score
                })

    # Sort profiles based on the number of common songs
    prioritized_profiles.sort(key=lambda x: x['similarity_score'], reverse=True)
    
    return prioritized_profiles
