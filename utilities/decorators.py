from functools import wraps
from flask import flash, redirect, session, url_for
from flask_login import current_user, logout_user



def session_protection_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from app.modules.auth.models import Users
        if current_user.is_authenticated:
            current_session_id = session.get('session_id')
            user = Users.query.filter_by(id=current_user.id).first()
            if not user or user.session_id != current_session_id:
                logout_user()
                flash('You have been logged out because your session is invalid or you logged in from another device.')
                return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function
