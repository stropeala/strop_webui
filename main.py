from flask import (
    Blueprint,
    render_template,
    abort,
    redirect,
    url_for,
    request,
    flash,
)
from flask_login import (
    login_required,
    current_user,
)
from strop_webui.models import User
from strop_webui import db

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('welcome.html')

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)

@main.route('/about')
def about():
    return render_template('about.html')


# ===========================
#        ADMIN AREA
# ===========================

def require_admin():
    if not current_user.is_admin:
        abort(403)

@main.route('/admin')
@login_required
def admin_dashboard():
    require_admin()
    users = User.query.order_by(User.id.asc()).all()
    pending_count = User.query.filter_by(is_approved=False).count()
    return render_template('admin.html', users=users, pending_count=pending_count)

@main.route('/admin/pending')
@login_required
def admin_pending():
    require_admin()
    pending_users = User.query.filter_by(is_approved=False).all()
    return render_template('admin_pending.html', pending=pending_users)

@main.route('/admin/approve/<int:user_id>', methods=['POST'])
@login_required
def admin_approve(user_id):
    require_admin()
    user = User.query.get_or_404(user_id)
    user.is_approved = True
    db.session.commit()
    flash(f"Approved {user.email}")
    return redirect(request.referrer or url_for('main.admin_dashboard'))

@main.route('/admin/revoke/<int:user_id>', methods=['POST'])
@login_required
def admin_revoke(user_id):
    require_admin()
    user = User.query.get_or_404(user_id)

    # Don't let admin revoke themselves by accident
    if user.id == current_user.id:
        flash("You can't revoke your own access.")
        return redirect(request.referrer or url_for('main.admin_dashboard'))

    user.is_approved = False
    db.session.commit()
    flash(f"Revoked access for {user.email}")
    return redirect(request.referrer or url_for('main.admin_dashboard'))

@main.route('/admin/toggle-admin/<int:user_id>', methods=['POST'])
@login_required
def admin_toggle_admin(user_id):
    require_admin()
    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        flash("You can't remove your own admin.")
        return redirect(request.referrer or url_for('main.admin_dashboard'))

    user.is_admin = not user.is_admin
    db.session.commit()
    flash(f"Admin status changed for {user.email}")
    return redirect(request.referrer or url_for('main.admin_dashboard'))

@main.route('/admin/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_user(user_id):
    require_admin()
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        user.name = request.form.get('name', user.name)
        user.email = request.form.get('email', user.email)

        # optional checkboxes
        user.is_approved = bool(request.form.get('is_approved'))
        user.is_admin = bool(request.form.get('is_admin'))

        db.session.commit()
        flash("User updated.")
        return redirect(url_for('main.admin_dashboard'))

    return render_template('admin_edit.html', user=user)
