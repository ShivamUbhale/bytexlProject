import os

class Config:
    """
    General configuration class for the Flask application.
    """
    # Flask Secret Key for session management
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key')  # Make sure to set this in your environment
    # MongoDB URI for database connection
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/musicmatch')  # Replace with your MongoDB URI
    # Enable or disable debugging in Flask
    DEBUG = os.environ.get('DEBUG', True)
    
    # SocketIO configurations
    SOCKETIO_LOGGING = True
    SOCKETIO_MESSAGE_QUEUE = os.environ.get('SOCKETIO_MESSAGE_QUEUE', None)  # Set if using a message queue like Redis
    
    # Application-wide configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Limit file uploads to 16MB (adjust as needed)
    UPLOAD_FOLDER = './uploads'  # Folder to store uploaded files (photos)
    
    # Optional: Email configuration for sending emails (e.g., for account verification or password reset)
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = os.environ.get('MAIL_PORT', 587)
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@musicmatch.com')

class DevelopmentConfig(Config):
    """
    Development-specific configuration.
    """
    ENV = 'development'
    DEBUG = True
    TESTING = True

class ProductionConfig(Config):
    """
    Production-specific configuration.
    """
    ENV = 'production'
    DEBUG = False
    TESTING = False
    # Consider using a more secure SECRET_KEY in production
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secure-prod-key')

class TestingConfig(Config):
    """
    Testing-specific configuration.
    """
    ENV = 'testing'
    DEBUG = True
    TESTING = True
    MONGO_URI = 'mongodb://localhost:27017/musicmatch_test'  # Use a separate test database
