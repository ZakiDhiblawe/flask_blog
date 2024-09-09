from flask import Blueprint, render_template

error = Blueprint('error', __name__)

@error.app_errorhandler(404)  # Use app_errorhandler for handling errors globally
def page_not_found(e):
    return render_template('404.html'), 404

@error.app_errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500
