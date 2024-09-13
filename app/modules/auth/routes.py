import hashlib
from werkzeug.utils import secure_filename
import os
import secrets
from flask import session
import uuid
from datetime import datetime
from flask import redirect, render_template, flash, request, url_for, Blueprint
from app.modules.dashboard.forms import DashboardForm, PasswordChangeForm
from utilities.mail import mail  # Import mail from utilities.mail
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import current_user, login_user, logout_user, login_required
from utilities.decorators import session_protection_required
from utilities.decorators_activity import timezone_required, track_activity_and_auto_logout
from .forms import ForgotPasswordForm, LoginForm, ResetPassWwordForm, UsersForm
from .models import Users
from sqlalchemy.exc import IntegrityError
from utilities.db import db
from flask_mail import Message
import re


blueprint = Blueprint('auth', __name__, url_prefix='/auth')


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



@blueprint.route('/signup', methods=['GET', 'POST'])
def signup():
    form = UsersForm()
    if form.validate_on_submit():
        # Password mismatch check
        if form.password_hash.data != form.password_hash2.data:
            flash('Passwords do not match', 'danger')
            return render_template('private/body/signup.html', form=form)  # Return the same form with the error

        # Check password strength
        password = form.password_hash.data
        if not re.match(r'^(?=.*[0-9])(?=.*[a-zA-Z]).{6,}$', password):
            flash('Password must be at least 6 characters long, contain at least one number, and one letter.', 'danger')
            return render_template('private/body/signup.html', form=form)
        
        # Check if username or email already exists
        user_by_username = Users.query.filter_by(username=form.username.data).first()
        user_by_email = Users.query.filter_by(email=form.email.data).first()
        
        if user_by_username:
            flash('Username already exists', 'danger')
            return render_template('private/body/signup.html', form=form)
        if user_by_email:
            flash('Email already exists', 'danger')
            return render_template('private/body/signup.html', form=form)

        # Create new user if all conditions are met
        hashed_pw = generate_password_hash(password)
        user = Users(
            name=form.name.data,
            email=form.email.data,
            username=form.username.data,
            password_hash=hashed_pw
        )
        try:
            db.session.add(user)
            db.session.commit()
            flash("User added successfully", 'success')
            return redirect(url_for('auth.login'))
        except IntegrityError:
            db.session.rollback()
            flash('There was an issue adding the user.', 'danger')
            return render_template('private/body/signup.html', form=form)
    return render_template('private/body/signup.html', form=form)




@blueprint.route('/profile-update/<int:id>', methods=['GET', 'POST'])
@login_required
@track_activity_and_auto_logout
@timezone_required
@session_protection_required
def update_user(id):
    if id == current_user.id:
        user_form = DashboardForm()
        password_form = PasswordChangeForm()

        if request.method == 'POST':
            # User Info Form Processing
            if user_form.validate_on_submit():
                user_by_username = Users.query.filter_by(username=user_form.username.data).first()
                user_by_email = Users.query.filter_by(email=user_form.email.data).first()

                if user_by_username and user_by_username.id != id:
                    flash('Username already exists', 'danger')
                elif user_by_email and user_by_email.id != id:
                    flash('Email already exists', 'danger')
                else:
                    try:
                        current_user.name = user_form.name.data
                        current_user.email = user_form.email.data
                        current_user.username = user_form.username.data
                        current_user.about_author = user_form.about_author.data

                        if user_form.profile_pic.data and allowed_file(user_form.profile_pic.data.filename):
                            file = user_form.profile_pic.data
                            filename = secure_filename(file.filename)
                            encrypted_filename = encrypt_filename(filename)
                            file_path = os.path.join(UPLOAD_FOLDER, encrypted_filename)

                            if not os.path.exists(UPLOAD_FOLDER):
                                os.makedirs(UPLOAD_FOLDER)

                            file.save(file_path)
                            current_user.profile_pic = encrypted_filename

                        db.session.commit()
                        flash('Profile updated successfully', 'success')
                        return redirect(url_for('dashboard.dashboard'))
                    except IntegrityError as e:
                        db.session.rollback()
                        flash('An error occurred while updating the profile. Please try again.', 'danger')
                        print(f"IntegrityError: {e}")

            # Password Update Form Processing
            if password_form.validate_on_submit():
                current_password = password_form.current_password.data
                new_password = password_form.new_password.data
                confirm_password = password_form.confirm_password.data

                # Check current password
                if not check_password_hash(current_user.password_hash, current_password):
                    flash('Current password is incorrect', 'danger')
                # Check if new passwords match
                elif new_password != confirm_password:
                    flash('New passwords do not match', 'danger')
                # Check password strength
                elif not re.match(r'^(?=.*[0-9])(?=.*[a-zA-Z]).{6,}$', new_password):
                    flash('New password must be at least 6 characters long, contain at least one number, and one letter.', 'danger')
                else:
                    try:
                        current_user.password_hash = generate_password_hash(new_password, method='scrypt')
                        db.session.commit()
                        flash('Password changed successfully', 'success')
                    except IntegrityError as e:
                        db.session.rollback()
                        flash('An error occurred while changing the password. Please try again.', 'danger')
                        print(f"IntegrityError: {e}")

        # Pre-populate forms with existing user data
        user_form.name.data = current_user.name
        user_form.email.data = current_user.email
        user_form.username.data = current_user.username
        user_form.about_author.data = current_user.about_author
        
        return render_template('users/body/profile.html', user_form=user_form, password_form=password_form, id=id)

    else:
        flash('You can only update your own profile', 'danger')
        return redirect(url_for('auth.login'))





# delete user
@blueprint.route('/delete/<int:id>')
@login_required
@track_activity_and_auto_logout
@timezone_required
@session_protection_required
def delete(id):
    if current_user.id == id:
        user_to_delete = Users.query.get_or_404(id)
        name = None
        form = UsersForm()
        try:
            db.session.delete(user_to_delete)
            db.session.commit()
            flash('User deleted successfully')
            our_users = Users.query.order_by(Users.date_added).all()

            return redirect(url_for('auth.signup', name=name, our_users=our_users))
        except:
            flash('Whoops! There was a problem deleting user, try again...')
            return render_template('signup.html', form=form, name=name, our_users=our_users)

    else:
        flash('You can only delete your own profile', 'danger')
        if current_user.is_authenticated:
            return redirect(url_for('auth.delete', id=current_user.id))
        else:
            return redirect(url_for('auth.login'))  # Add return statement here


@blueprint.route('/login', methods=['GET', 'POST'])
@timezone_required
def login():
    form = LoginForm()
    next_url = request.args.get('next')

    if form.validate_on_submit():
        # Check if the user exists by username or email
        user = Users.query.filter(
            (Users.username == form.username.data) |
            (Users.email == form.username.data)
        ).first()

        if user and check_password_hash(user.password_hash, form.password.data):
            remember = True if form.remember.data else False  # Get the "Remember Me" value from the form
            login_user(user, remember=remember)  # Pass the remember parameter to login_user

            # Generate a unique session ID and store it in the database
            new_session_id = str(uuid.uuid4())
            user.session_id = new_session_id
            db.session.commit()

            # Store the session ID in the current session
            session['session_id'] = new_session_id

            user.last_login = datetime.utcnow()
            user.last_activity = datetime.utcnow()
            db.session.commit()

            flash('Login successful')
            return redirect(next_url or url_for('dashboard.dashboard'))
        else:
            flash('Invalid username or password')

    return render_template('private/body/login.html', form=form)



@blueprint.route('/logout', methods=['GET', 'POST'])
@login_required
@track_activity_and_auto_logout
@timezone_required
@session_protection_required
def logout():
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('auth.login'))



@blueprint.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()
    
    if form.validate_on_submit():
        email = form.email.data
        user = Users.query.filter_by(email=email).first()

        email_passed =form.email.data
        if user:
            # Generate a secure token
            token = secrets.token_urlsafe(50)
            user.reset_token = token
            db.session.commit()

            # Create a password reset link
            reset_link = url_for('auth.reset_password', token=token, _external=True)
            
            # Send an email with the reset link
            msg = Message('Password Reset Request',
                          sender='maarta17@gmail.com',
                          recipients=[user.email])
            msg.body = f'''To reset your password, visit the following link:
{reset_link}

If you did not make this request, simply ignore this email and no changes will be made.
'''
            mail.send(msg)
            email_passed =form.email.data
            flash('A password reset link has been sent to your email.', 'success')
            return redirect(url_for('auth.reset_password_success',  email=email_passed))
        else:
            flash('Email not found.', 'danger')
            return redirect(url_for('auth.forgot_password'))

    return render_template('private/body/forgot_password.html', form=form)


@blueprint.route('/reset-password-success/<email>')
def reset_password_success(email):
    return render_template('private/body/reset_password_success.html', email=email)




@blueprint.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = Users.query.filter_by(reset_token=token).first_or_404()
    form = ResetPassWwordForm()
    
    if form.validate_on_submit():
        new_password = form.password_hash.data
        confirm_password = form.password_hash2.data

        if new_password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('private/body/reset_password.html', form=form, token=token)

        # Check password strength
        if not re.match(r'^(?=.*[0-9])(?=.*[a-zA-Z]).{6,}$', new_password):
            flash('Password must be at least 6 characters long, contain at least one number, and one letter.', 'danger')
            return render_template('private/body/reset_password.html', form=form, token=token)

        # Update the password and clear the reset token
        user.password_hash = generate_password_hash(new_password)
        user.reset_token = None
        db.session.commit()
        flash('Your password has been updated. You can now log in with your new password.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('private/body/reset_password.html', form=form, token=token)
