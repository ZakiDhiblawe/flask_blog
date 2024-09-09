import os
from dotenv import load_dotenv
from flask import Flask, redirect, render_template, flash, request, url_for, Blueprint
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, current_user, login_user, logout_user, LoginManager, login_required, login_remembered
from .forms import DashboardForm
from sqlalchemy.exc import IntegrityError
from ..auth.models import Users
from utilities.db import db




blueprint = Blueprint('dashboard', __name__, url_prefix='/dashboard')




@blueprint.route('/', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = DashboardForm()
    id = current_user.id
    name_updating = Users.query.get_or_404(id)

    if request.method == 'POST':
        if form.validate_on_submit():
            user_by_username = Users.query.filter_by(username=form.username.data).first()
            user_by_email = Users.query.filter_by(email=form.email.data).first()

            # Prevent duplication of username or email
            if user_by_username and user_by_username.id != id:
                flash('Username already exists', 'danger')
            elif user_by_email and user_by_email.id != id:
                flash('Email already exists', 'danger')
            else:
                try:
                    name_updating.name = form.name.data
                    name_updating.email = form.email.data
                    name_updating.username = form.username.data
                    db.session.commit()
                    flash('User updated successfully', 'success')
                    return redirect(url_for('dashboard.dashboard')) # Stay on dashboard after updating
                except IntegrityError as e:
                    db.session.rollback()
                    flash('An error occurred while updating the user.', 'danger')
                    print(f"IntegrityError: {e}")
        else:
            flash('Form validation failed', 'danger')

    # Pre-populate the form with current data
    form.name.data = name_updating.name
    form.email.data = name_updating.email
    form.username.data = name_updating.username

    return render_template('dashboard.html', form=form, name_updating=name_updating, id=id)



