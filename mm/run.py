from app import app, socketio
from config import DevelopmentConfig, ProductionConfig, TestingConfig
import os

def run():
    # Load configuration based on environment variable
    app_env = os.environ.get('FLASK_ENV', 'development').lower()

    if app_env == 'production':
        app.config.from_object(ProductionConfig)
    elif app_env == 'testing':
        app.config.from_object(TestingConfig)
    else:
        app.config.from_object(DevelopmentConfig)

    print(f"Running Flask in {app_env} mode")

    # Run the app with SocketIO (for real-time features like chat)
    socketio.run(app, host='0.0.0.0', port=5000, debug=app.config['DEBUG'])
from app.routes import initialize_routes
initialize_routes(app) 
if __name__ == "__main__":
    socketio.run(app, debug=True)
