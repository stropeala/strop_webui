import os                                   # Gives access to OS functions
from flask import Flask                     # Flask class for creating the web application
from flask_sqlalchemy import SQLAlchemy     # SQLAlchemy extension for database handling
from flask_login import LoginManager        # Flask-Login extension for user session management
from dotenv import load_dotenv              # Loads environment variables from a .env file
load_dotenv()                               # Loads variables from .env into the system environment like SECRET_KEY

# Initialize SQLAlchemy instance
db = SQLAlchemy()

# This function creates and configures the Flask application
def create_app():

    # Build the path to the "instance" directory inside the package
    instance_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'instance'))

    # Ensure the instance directory actually exists or create if not
    os.makedirs(instance_path, exist_ok=True)

    # Create the Flask application object
    app = Flask(
        __name__,
        instance_path=instance_path,
        instance_relative_config=True,
        template_folder='templates',
        static_folder='static'
    )


#---------- Application Settings ----------#


    # Secret key is used for session security
    # Try to load it from .env otherwise use a default development key
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-69-420')


    # Setup database connection
    # Try environment variable DATABASE_URL otherwise default to a local SQLite file
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///db.sqlite')


    # Disable SQLAlchemy's event system because it isn't needed
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


    # Initialize SQLAlchemy with this app
    db.init_app(app)


    # Import models before creating database tables
    from .models import User


    # Create the database tables
    with app.app_context():
        db.create_all()


#----------- FLASK-LOGIN SETUP -----------#


    # Create LoginManager to handle login sessions
    login_manager = LoginManager()


    # If a user tries to access something requiring login redirect them to the auth.login route
    login_manager.login_view = 'auth.login'


    # Attach LoginManager to the app.
    login_manager.init_app(app)


    # Define how Flask-Login loads a user from the database using the user ID stored in their session
    @login_manager.user_loader
    def load_user(user_id):
        # Convert user_id string to integer and fetch user by primary key
        return User.query.get(int(user_id))


#------------- REGISTER BLUEPRINTS --------------#


    # Import and register the authentication blueprint
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)


    # Import and register general routes
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)


    # Import and register chat routes
    from .chat import chat as chat_blueprint
    app.register_blueprint(chat_blueprint)


    # Return the fully configured Flask app
    return app