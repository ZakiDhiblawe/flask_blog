from flask import session

def get_user_timezone():
    return session.get('user_timezone')

def set_user_timezone(timezone):
    session['user_timezone'] = timezone

