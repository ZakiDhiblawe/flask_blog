from datetime import datetime, timedelta
from flask import jsonify, request, session, redirect, url_for, flash,g
from flask_login import current_user, logout_user




from .db import db
from functools import wraps
from utilities.timezone import set_user_timezone, get_user_timezone
from functools import wraps
from flask import session, redirect, url_for, flash
from flask_login import current_user, logout_user



def timezone_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        timezone = get_user_timezone()
        print(f"Timezone fetched from session: {timezone}")  # Debugging line
        if timezone != 'UTC':
            print(f"Timezone used in decorator: {timezone}")
        return f(*args, **kwargs)
    return decorated_function





def track_activity_and_auto_logout(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if current_user.is_authenticated:
            from app.modules.auth.models import Users
            user = Users.query.filter_by(id=current_user.id).first()
            if user:
                user.last_activity = datetime.utcnow()
                db.session.commit()
                print(f"Updated last_activity for user {user.id}: {user.last_activity}")
        return f(*args, **kwargs)

    return wrapper
