# Import Flask tools
from flask import (
    Blueprint,  # Allows organizing routes into modular groups
    abort,  # Sends predefined HTTP error codes
    redirect,  # Redirects user to another URL
    render_template,  # Renders HTML templates
    request,  # Gets form data from POST requests
    # flash                Shows temporary messages to the user !!!!!!!!!!!!!!!!!!!!!!!!!!!! Disabled because it's not yet implemented into the frontend !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    url_for,  # Generates URLs for routes
)

# Import login-related helpers from Flask-Login
from flask_login import (
    current_user,  # Represents the user currently logged in
    login_required,  # Decorator that blocks access unless logged in
)

# Import the database session for saving user changes
from . import db

# Import User model so admin routes can manage users
from .models import User

# Create Blueprint for general site routes
main = Blueprint("main", __name__)


# ------------ PUBLIC PAGES -------------#


@main.route("/")
def index():
    # Renders the homepage
    return render_template("welcome.html")


@main.route("/profile")
@login_required
def profile():
    # Shows the logged-in user's profile page
    return render_template("profile.html", name=current_user.name)


@main.route("/about")
def about():
    # Simple About page
    return render_template("about.html")


# ------------ ADMIN SYSTEM -------------#


def require_admin():
    # Helper function used in admin routes
    if not current_user.is_admin:
        abort(403)  # Deny access entirely


@main.route("/admin")
@login_required
def admin_dashboard():
    require_admin()  # Only admins may view this page

    # Query all users sorted by id
    users = User.query.order_by(User.id.asc()).all()

    # Number of users who are not yet approved
    pending_count = User.query.filter_by(is_approved=False).count()

    return render_template("admin.html", users=users, pending_count=pending_count)


@main.route("/admin/approve/<int:user_id>", methods=["POST"])
@login_required
def admin_approve(user_id):
    # Allows admin to approve a user
    require_admin()

    # Load user or show 404 if user doesn't exist
    user = User.query.get_or_404(user_id)

    user.is_approved = True  # Mark user as approved
    db.session.commit()  # Save to database

    # flash(f"Approved {user.email}")  # Show confirmation

    # Redirect back to where the admin came from
    return redirect(request.referrer or url_for("main.admin_dashboard"))


@main.route("/admin/revoke/<int:user_id>", methods=["POST"])
@login_required
def admin_revoke(user_id):
    # Revokes a user's access
    require_admin()

    user = User.query.get_or_404(user_id)

    # Prevent admin from accidentally revoking themselves
    if user.id == current_user.id:
        # flash("You can't revoke your own access.")
        return redirect(request.referrer or url_for("main.admin_dashboard"))

    user.is_approved = False
    db.session.commit()

    # flash(f"Revoked access for {user.email}")
    return redirect(request.referrer or url_for("main.admin_dashboard"))


@main.route("/admin/toggle-admin/<int:user_id>", methods=["POST"])
@login_required
def admin_toggle_admin(user_id):
    # Toggles a user's admin status
    require_admin()

    user = User.query.get_or_404(user_id)

    # Prevent admin from removing their own admin status
    if user.id == current_user.id:
        # flash("You can't remove your own admin.")
        return redirect(request.referrer or url_for("main.admin_dashboard"))

    user.is_admin = not user.is_admin  # Flip admin status
    db.session.commit()

    # flash(f"Admin status changed for {user.email}")
    return redirect(request.referrer or url_for("main.admin_dashboard"))


@main.route("/admin/edit/<int:user_id>", methods=["GET", "POST"])
@login_required
def admin_edit_user(user_id):
    # Page for editing user information
    require_admin()

    # Load user or show 404
    user = User.query.get_or_404(user_id)

    if request.method == "POST":
        # Update values only if provided otherwise keep old ones
        user.name = request.form.get("name", user.name)
        user.email = request.form.get("email", user.email)

        # Checkboxes return on if checked none if not
        user.is_approved = bool(request.form.get("is_approved"))
        user.is_admin = bool(request.form.get("is_admin"))

        db.session.commit()
        # flash("User updated.")

        return redirect(url_for("main.admin_dashboard"))

    # GET request to show edit form
    return render_template("admin_edit.html", user=user)
