import os
from flask import Flask
from flask_pymongo import PyMongo
from flask_socketio import SocketIO

# Initialize Flask application
app = Flask(__name__)

# Set up the application configuration
app.config['MONGO_URI'] = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/musicmatch')  # MongoDB URI
app.secret_key = os.environ.get('SECRET_KEY', 'supersecretkey')  # Secret key

# Define the folder for file uploads (make sure this happens BEFORE importing routes)
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')

# Ensure that the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Initialize PyMongo for database interactions
mongo = PyMongo(app)

# Initialize SocketIO for real-time chat functionality
socketio = SocketIO(app)

# Import routes and models after initializing app to avoid circular imports
from app import routes, models

