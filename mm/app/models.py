import datetime
from app.__init__ import mongo
from bson.objectid import ObjectId

# User model structure (MongoDB-based)
class User:
    def __init__(self, email, password, username, photos=None, songs=None, bio=""):
        self.email = email
        self.password = password
        self.username = username
        self.photos = photos or []
        self.songs = songs or []
        self.bio = bio
        self.matches = []  # List to store match IDs
        self.match_requests = []  # Store match request IDs for incoming/outgoing requests

    @classmethod
    def get_by_id(cls, user_id):
        return mongo.db.users.find_one({'_id': ObjectId(user_id)})

    @classmethod
    def get_by_email(cls, email):
        return mongo.db.users.find_one({'email': email})

    @classmethod
    def create_user(cls, email, password, username, photos=None, songs=None, bio=""):
        user_data = {
            'email': email,
            'password': password,
            'username': username,
            'photos': photos or [],
            'songs': songs or [],
            'bio': bio,
            'matches': [],
            'match_requests': []
        }
        result = mongo.db.users.insert_one(user_data)
        return result.inserted_id

    @classmethod
    def update_profile(cls, user_id, photos=None, songs=None, bio=""):
        return mongo.db.users.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {
                'photos': photos or [],
                'songs': songs or [],
                'bio': bio
            }}
        )

    def __repr__(self):
        return f'<User {self.username}>'

# Match Request model (MongoDB-based)
class MatchRequest:
    def __init__(self, sender_id, receiver_id, status="pending"):
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.status = status  # "pending", "accepted", "rejected"

    @classmethod
    def create_match_request(cls, sender_id, receiver_id):
        match_request_data = {
            'sender_id': sender_id,
            'receiver_id': receiver_id,
            'status': 'pending'
        }
        result = mongo.db.match_requests.insert_one(match_request_data)
        return result.inserted_id

    @classmethod
    def update_status(cls, match_request_id, status):
        return mongo.db.match_requests.update_one(
            {'_id': ObjectId(match_request_id)},
            {'$set': {'status': status}}
        )

    @classmethod
    def get_pending_requests(cls, receiver_id):
        return list(mongo.db.match_requests.find({'receiver_id': receiver_id, 'status': 'pending'}))

    @classmethod
    def get_user_matches(cls, user_id):
        return list(mongo.db.match_requests.find({
            '$or': [{'sender_id': user_id}, {'receiver_id': user_id}],
            'status': 'accepted'
        }))

    def __repr__(self):
        return f'<MatchRequest {self.sender_id} -> {self.receiver_id}, {self.status}>'

# Chat model (MongoDB-based)
class Chat:
    def __init__(self, match_id, sender_id, message):
        self.match_id = match_id
        self.sender_id = sender_id
        self.message = message
        self.timestamp = datetime.datetime.utcnow()  # Automatically add timestamp

    @classmethod
    def create_message(cls, match_id, sender_id, message):
        chat_data = {
            'match_id': match_id,
            'sender_id': sender_id,
            'message': message,
            'timestamp': datetime.datetime.utcnow()
        }
        result = mongo.db.chats.insert_one(chat_data)
        return result.inserted_id

    @classmethod
    def get_chat_history(cls, match_id):
        return list(mongo.db.chats.find({'match_id': match_id}).sort('timestamp', 1))

    def __repr__(self):
        return f'<Chat {self.sender_id} -> {self.match_id}, {self.message}>'
