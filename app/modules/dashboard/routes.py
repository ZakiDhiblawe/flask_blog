import os
import hashlib
from flask import Blueprint, redirect, render_template, flash, request, url_for
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from sqlalchemy.exc import IntegrityError
from ..auth.models import Users
from utilities.db import db
from .forms import DashboardForm

blueprint = Blueprint('dashboard', __name__, url_prefix='/dashboard')

# Define a folder for profile pics
UPLOAD_FOLDER = 'app/static/images/profile_pics'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Helper function to check allowed extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Encrypt file name
def encrypt_filename(filename):
    file_extension = filename.rsplit('.', 1)[1].lower()
    # Encrypt using hashlib
    hash_object = hashlib.sha256(filename.encode())
    encrypted_filename = hash_object.hexdigest()
    return f"{encrypted_filename}.{file_extension}"

@blueprint.route('/', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = DashboardForm()
    id = current_user.id
    user = Users.query.get_or_404(id)

    if request.method == 'POST':
        if form.validate_on_submit():
            user_by_username = Users.query.filter_by(username=form.username.data).first()
            user_by_email = Users.query.filter_by(email=form.email.data).first()

            if user_by_username and user_by_username.id != id:
                flash('Username already exists', 'danger')
            elif user_by_email and user_by_email.id != id:
                flash('Email already exists', 'danger')
            else:
                try:
                    user.name = form.name.data
                    user.email = form.email.data
                    user.username = form.username.data
                    user.about_author = form.about_author.data

                    if form.profile_pic.data and allowed_file(form.profile_pic.data.filename):
                        file = form.profile_pic.data
                        filename = secure_filename(file.filename)
                        encrypted_filename = encrypt_filename(filename)
                        file_path = os.path.join(UPLOAD_FOLDER, encrypted_filename)

                        # Create directory if it does not exist
                        if not os.path.exists(UPLOAD_FOLDER):
                            os.makedirs(UPLOAD_FOLDER)

                        # Save the file
                        file.save(file_path)
                        user.profile_pic = encrypted_filename
                    else:
                        if form.profile_pic.data:  # Check if a file was provided but invalid
                            flash('Invalid file format', 'danger')

                    db.session.commit()
                    flash('User updated successfully', 'success')
                    return redirect(url_for('dashboard.dashboard'))
                except IntegrityError as e:
                    db.session.rollback()
                    flash('An error occurred while updating the user.', 'danger')
                    print(f"IntegrityError: {e}")
        else:
            flash('Form validation failed', 'danger')

    # Pre-populate the form with current data
    form.name.data = user.name
    form.email.data = user.email
    form.username.data = user.username
    form.about_author.data = user.about_author

    return render_template('dashboard.html', form=form, user=user, id=id)
