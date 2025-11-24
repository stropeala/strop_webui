from flask import(
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)
from flask_login import (
    login_user,
    logout_user,
    login_required
)
from strop_webui.models import User
from strop_webui import db
from strop_webui.security import pwd_context


auth = Blueprint('auth',__name__)


@auth.route('/login')
def login():
    return render_template('login.html')


@auth.route('/login', methods = ['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email = email).first()

    if not user:
        flash("No such user.")
        return redirect(url_for("auth.login"))

    if not pwd_context.verify(password, user.password):
        flash("Incorrect password.")
        return redirect(url_for("auth.login"))

    if not user.is_approved:
        flash("Your account is pending approval.")
        return redirect(url_for("auth.login"))

    login_user(user, remember = remember)
    return redirect(url_for('main.profile'))


@auth.route('/signup')
def signup():
    return render_template('signup.html')


@auth.route('/signup', methods = ['POST'])
def signup_post():
    #code to validate and add user to database goes here
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    # If this returns a user, then the email already exists in database
    user = User.query.filter_by(email = email).first()

    # If a user is found, we want to redirect back to signup page so user can try again
    if user:
        flash('Email address already exists.')
        return redirect(url_for('auth.signup'))

    # Hash the password so the plaintext version is not saved
    hashed_pw = pwd_context.hash(password)

    is_first = User.query.count() == 0

    # Create a new user with the form data
    new_user = User(
        email = email,
        name = name,
        password = hashed_pw,
        is_admin = is_first,  # First user becomes admin
        is_approved = is_first  # Admin is auto-approved
    )

    # Add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('auth.login'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))