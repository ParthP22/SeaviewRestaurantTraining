from flask import Flask

def create_app():
    app = Flask(__name__)

    # Import blueprints
    from .announcement.__init__ import announcement_bp
    from .auth.__init__ import session_handling_bp

    # Register blueprints
    app.register_blueprint(announcement_bp)
    app.register_blueprint(session_handling_bp)

    return app