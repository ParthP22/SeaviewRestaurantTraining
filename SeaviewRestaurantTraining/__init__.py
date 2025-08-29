import secrets
from flask import Flask

def create_secret_key(length=32):
    return secrets.token_hex(length)

def create_app():
    
    app = Flask(__name__)
    
    app.secret_key = create_secret_key()

    # Import blueprints
    from .homepage import welcome_bp
    from .announcement import announcement_bp
    from .auth import auth_bp
    from .employee import employee_bp
    from .manager import manager_bp
    from .quiz import quiz_bp

    # Register blueprints
    app.register_blueprint(welcome_bp)
    app.register_blueprint(announcement_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(employee_bp)
    app.register_blueprint(manager_bp)
    app.register_blueprint(quiz_bp)

    return app