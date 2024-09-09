import os
from dotenv import load_dotenv
from flask import Flask, redirect, render_template, flash, request, url_for, Blueprint
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, current_user, login_user, logout_user, LoginManager, login_required, login_remembered
from sqlalchemy.exc import IntegrityError
from utilities.db import db




blueprint = Blueprint('admin', __name__, url_prefix='/admin')


# craete basic admin page
@blueprint.route('/')
@login_required
def index():
    id = current_user.id
    if id == 35:
        return render_template('admin/index.html')
    else:
        flash('You are not authorized to access this page.')
        return redirect(url_for('dashboard.dashboard'))
