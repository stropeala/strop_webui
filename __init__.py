import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


# Initialize SQLAlchemy instance
db = SQLAlchemy()


def create_app():
    # Path to instance folder *inside* package
    instance_path = os.path.join(os.path.dirname(__file__), "instance")

    # Ensure instance exists
    os.makedirs(instance_path, exist_ok=True)

    app = Flask(
        __name__,
        instance_path = instance_path,
        instance_relative_config = True,
        template_folder = 'templates',
        static_folder = 'static'
    )

    # Configuration
    app.config['SECRET_KEY'] = 'super-secret-key-69-420'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions with app
    db.init_app(app)

    # Import models BEFORE create_all()
    from strop_webui.models import User

    # Create database tables
    with app.app_context():
        db.create_all()

    # Configure Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    # User loader function for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from strop_webui.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from strop_webui.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from strop_webui.chat import chat as chat_blueprint
    app.register_blueprint(chat_blueprint)

    return app
