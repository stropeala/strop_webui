# Import Flask tools
from flask import (
    Blueprint,  # Used to split the app into separate route modules
    redirect,  # Redirects the user to another URL
    render_template,  # Renders HTML templates
    request,  # Reads form data
    url_for,  # Generates URLs for routes
    # flash                Displays temporary messages to the user !!!!!!!!!!!!!!!!!!!!!!!!!!!! Disabled because it's not yet implemented into the frontend !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
)

# Import Flask-Login tools for managing sessions and authentication
from flask_login import (
    login_required,  # Blocks routes unless the user is logged in
    login_user,  # Logs in the user
    logout_user,  # Logs out the user
)

# Import the database session so we can add new users
from . import db

# Import our User model
from .models import User

# Password hashing (argon2) for secure password storage
from .security import pwd_context

# Create a Blueprint named auth
auth = Blueprint("auth", __name__)


# ------------ LOGIN PAGE -------------#


@auth.route("/login")
def login():
    # Show the login HTML page
    return render_template("login.html")


@auth.route("/login", methods=["POST"])
def login_post():
    # Get the values typed into the login form
    email = request.form.get("email")
    password = request.form.get("password")

    # Checkbox Remember me returns True if checked otherwise False
    # remember = True if request.form.get('remember') else False

    # Look for a user in the database with the same email
    user = User.query.filter_by(email=email).first()

    # If user does not exist show error and send them back to login page
    if not user:
        # flash("No such user.")
        return redirect(url_for("auth.login"))

    # Check password using argon2 hashing
    if not pwd_context.verify(password, user.password):  # type: ignore[attr-defined]
        # flash("Incorrect password.")
        return redirect(url_for("auth.login"))

    # Check if user has been approved by an admin
    if not user.is_approved:
        # flash("Your account is pending approval.")
        return redirect(url_for("auth.login"))

    # Credentials are correct  log in user and create session
    login_user(user)  # , remember=remember)

    # Redirect to user’s profile page after login
    return redirect(url_for("main.profile"))


# ------------ SIGNUP PAGE -------------#


@auth.route("/signup")
def signup():
    # Render the HTML signup form
    return render_template("signup.html")


@auth.route("/signup", methods=["POST"])
def signup_post():
    # Read form fields from signup form
    email = request.form.get("email")
    name = request.form.get("name")
    password = request.form.get("password")

    # Check if a user with this email already exists
    user = User.query.filter_by(email=email).first()

    # If it exists show error and reload signup page
    if user:
        # flash('Email address already exists.')
        return redirect(url_for("auth.signup"))

    # Hash the password using Argon2
    hashed_pw = pwd_context.hash(password)  # type: ignore[attr-defined]

    # See if this is the first user ever created
    # First user becomes admin automatically
    is_first = User.query.count() == 0

    # Create a new user object with provided info
    new_user = User(
        email=email,  # type: ignore[attr-defined]
        name=name,  # type: ignore[attr-defined]
        password=hashed_pw,
        is_admin=is_first,  # First user gets admin privilege
        is_approved=is_first,  # First user is auto-approved
    )

    # Add user to DB session and save it
    db.session.add(new_user)
    db.session.commit()

    # After signup send them to login page
    return redirect(url_for("auth.login"))


# ------------ LOGOUT -------------#


@auth.route("/logout")
@login_required  # Only logged-in users can log out
def logout():
    logout_user()  # Remove user session
    return redirect(url_for("main.index"))  # Go back to homepage
