import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from datetime import datetime
from flask_socketio import SocketIO, emit, join_room
from werkzeug.utils import secure_filename
from flask import send_from_directory

from app.models import User


# Initialize the app, MongoDB, and SocketIO
app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/musicmatch'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
mongo = PyMongo(app)
socketio = SocketIO(app)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_user():
    return mongo.db.users.find_one({'email': session.get('user_id')})

def calculate_similarity(songs1, songs2):
    common_songs = set(songs1).intersection(set(songs2))
    return len(common_songs)

# Routes
def initialize_routes(app): 
 @app.route('/')
 def home():
    return render_template('base.html')

 @app.route('/register', methods=['GET', 'POST'])
 def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        songs = request.form.getlist('songs')

        mongo.db.users.insert_one({
            'username': username,
            'password': password,
            'email': email,
            'songs': songs,
            'created_at': datetime.now()
        })
        return redirect('/login')
    return render_template('register.html')

 @app.route('/login', methods=['GET', 'POST'])
 def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            return "Username or password missing", 400

        user = mongo.db.users.find_one({'username': username, 'password': password})
        if user:
            session['user_id'] = str(user['_id'])
            return redirect(url_for('dashboard'))
        else:
            return "Invalid credentials", 401
    return render_template('login.html')

 @app.route('/profile', methods=['GET', 'POST'])
 def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = mongo.db.users.find_one({'_id': ObjectId(session['user_id'])})
    
    if request.method == 'POST':
        username = request.form.get('username')
        bio = request.form.get('bio')
        songs = request.form.getlist('songs')
        photos = []
        
        for i in range(1, 3):  # Assuming two photos
            photo = request.files.get(f'photo{i}')
            if photo and allowed_file(photo.filename):
                filename = secure_filename(photo.filename)
                photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                photo.save(photo_path)
                photos.append(f'uploads/{filename}')

        mongo.db.users.update_one(
            {'_id': ObjectId(session['user_id'])},
            {'$set': {'username': username, 'bio': bio, 'songs': songs, 'photos': photos}}
        )
        return redirect(url_for('profile'))
    return render_template('profile.html', user=user)

 @app.route('/uploads/<filename>')
 def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

 @app.route('/dashboard')
 def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    
    user_id = session['user_id']
    current_user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
    users = mongo.db.users.find({'_id': {'$ne': ObjectId(user_id)}})
    match_requests = mongo.db.match_requests.find({'receiver_id': user_id, 'status': 'pending'})
    
    return render_template('dashboard.html', current_user=current_user, users=users, match_requests=match_requests)

 @app.route('/send-match-request', methods=['POST'])
 def send_match_request():
    try:
        data = request.get_json()
        user_id = data['userId']
        sender_id = session['user_id']

        user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
        if not user:
            return jsonify({'error': 'User not found'}), 404

        mongo.db.match_requests.insert_one({
            'sender_id': sender_id,
            'receiver_id': user_id,
            'status': 'pending'
        })

        return jsonify({'status': 'success'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

 @app.route('/accept-match-request', methods=['POST'])
 def accept_match_request():
    try:
        data = request.get_json()
        request_id = data['requestId']
        match_request = mongo.db.match_requests.find_one({'_id': ObjectId(request_id)})
        if not match_request:
            return jsonify({'error': 'Match request not found'}), 404

        mongo.db.match_requests.update_one(
            {'_id': ObjectId(request_id)},
            {'$set': {'status': 'accepted'}}
        )

        return jsonify({'status': 'success'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

 @app.route('/decline-match-request', methods=['POST'])
 def decline_match_request():
    try:
        data = request.get_json()
        request_id = data['requestId']
        match_request = mongo.db.match_requests.find_one({'_id': ObjectId(request_id)})
        if not match_request:
            return jsonify({'error': 'Match request not found'}), 404

        mongo.db.match_requests.update_one(
            {'_id': ObjectId(request_id)},
            {'$set': {'status': 'declined'}}
        )

        return jsonify({'status': 'success'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

 @app.route('/chat/<receiver_id>')
 def chat(receiver_id):
    try:
        # Query the matched user using MongoDB
        matched_user = mongo.db.users.find_one({'_id': ObjectId(receiver_id)})

        if not matched_user:
            return jsonify({'error': 'Matched user not found'}), 404

        # Pass matched_user to the template
        return render_template('chat.html', matched_user=matched_user)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


 @socketio.on('send_message')
 
 def handle_message(data):
    receiver_id = data['receiverId']
    text = data['text']
    emit('new_message', {'text': text, 'senderId': session['user_id']}, room=receiver_id)

 @socketio.on('join')
 def on_join(user_id):
    join_room(user_id)

 @app.route('/logout', methods=['GET'])
 def logout():
    session.pop('user_id', None)
    return redirect('/login')

 if __name__ == '__main__':
    socketio.run(app, debug=True)
