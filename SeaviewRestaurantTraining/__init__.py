from flask import Flask

def create_app():
    app = Flask(__name__)

    # Import blueprints
    from .announcement.__init__ import announcement_bp
    from .auth.__init__ import session_handling_bp
    from .employee.__init__ import employee_bp
    from .manager.__init__ import manager_bp
    from .quiz.__init__ import quiz_bp

    # Register blueprints
    app.register_blueprint(announcement_bp)
    app.register_blueprint(session_handling_bp)
    app.register_blueprint(employee_bp)
    app.register_blueprint(manager_bp)
    app.register_blueprint(quiz_bp)

    return app