# Import the shared database instance created in __init__.py
from strop_webui import db

# Import UserMixin, which adds helpful default behaviors for user accounts
# such as `is_authenticated`, `is_active`, `get_id()`, etc.
from flask_login import UserMixin


#------------ USER MODEL -------------#


# This class represents a row in the user database table.
# Each attribute is a column in the table.
class User(UserMixin, db.Model):
    # Primary Key: unique ID for each user
    id = db.Column(db.Integer, primary_key=True)


    # Email column: must be unique and cannot be empty
    email = db.Column(db.String(100), unique=True, nullable=False)


    # Password column: stores the hashed password
    password = db.Column(db.String(300), nullable=False)


    # Name column: just storing the user's display name
    name = db.Column(db.String(1000))


    # Boolean: whether the user has admin privileges
    is_admin = db.Column(db.Boolean, default=False)


    # Boolean: whether the user's account is approved by an admin
    is_approved = db.Column(db.Boolean, default=False)