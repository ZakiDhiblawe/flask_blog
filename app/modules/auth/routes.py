import os
from dotenv import load_dotenv
from flask import Flask, redirect, render_template, flash, request, url_for, Blueprint
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, current_user, login_user, logout_user, LoginManager, login_required, login_remembered
from .forms import LoginForm, UsersForm
from .models import Users
from sqlalchemy.exc import IntegrityError
from utilities.db import db




blueprint = Blueprint('auth', __name__, url_prefix='/auth')




@blueprint.route('/signup', methods=['GET', 'POST'])
def signup():
    name = None
    form = UsersForm()
    our_users = Users.query.order_by(Users.date_added).all()
    if form.validate_on_submit():
        pw_hashed = generate_password_hash(form.password_hash.data, method='scrypt')
        user_by_username = Users.query.filter_by(username=form.username.data).first()
        user_by_email = Users.query.filter_by(email=form.email.data).first()
        if user_by_username:
            flash('Username already exists', 'danger')
        elif user_by_email:
            flash('Email already exists', 'danger')
        else:
            try:
                user = Users(
                    name=form.name.data,
                    email=form.email.data,
                    password_hash=pw_hashed,
                    username=form.username.data
                )
                db.session.add(user)
                db.session.commit()
                flash('User added successfully')
                # Clear the form fields after successful submission
                form.name.data = ''
                form.email.data = ''
                form.username.data = ''
                form.password_hash.data = ''
                # Update `our_users` after adding a new user
                our_users = Users.query.order_by(Users.date_added).all()
            except IntegrityError as e:
                db.session.rollback()
                flash('An error occurred while adding the user. Please try again.', 'danger')
                print(f"IntegrityError: {e}")
    return render_template('signup.html', form=form, name=name, our_users=our_users)




@blueprint.route('/profile-update/<int:id>', methods=['GET', 'POST'])
@login_required
def update_user(id):
    if id == current_user.id:
        form = UsersForm()
        name_updating = Users.query.get_or_404(id)

        if request.method == 'POST':
            if form.validate_on_submit():
                # Check for duplicate username and email
                user_by_username = Users.query.filter_by(username=form.username.data).first()
                user_by_email = Users.query.filter_by(email=form.email.data).first()

                if user_by_username and user_by_username.id != id:
                    flash('Username already exists', 'danger')
                elif user_by_email and user_by_email.id != id:
                    flash('Email already exists', 'danger')
                else:
                    try:
                        name_updating.name = form.name.data
                        name_updating.email = form.email.data
                        name_updating.username = form.username.data
                        name_updating.password_hash = generate_password_hash(form.password_hash.data, method='scrypt')
                        db.session.commit()
                        flash('User updated successfully', 'success')
                        return redirect(url_for('dashboard.dashboard'))
                    except IntegrityError as e:
                        db.session.rollback()
                        flash('An error occurred while updating the user. Please try again.', 'danger')
                        print(f"IntegrityError: {e}")

        # Pre-populate form fields with existing user data
        form.name.data = name_updating.name
        form.email.data = name_updating.email
        form.username.data = name_updating.username
        return render_template('update-profile.html', form=form, name_updating=name_updating, id=id)

    else:
        flash('You can only update your own profile', 'danger')
        if current_user.is_authenticated:
            return redirect(url_for('auth.update_user', id=current_user.id))
        else:
            return redirect(url_for('auth.login'))  # Add return statement here







# delete user
@blueprint.route('/delete/<int:id>')
@login_required
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
def login():
    form = LoginForm()
    next_url = request.args.get('next')  # Get the next parameter from the URL

    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash('Login successful')

            # Redirect to the next URL if it exists, otherwise go to the dashboard
            return redirect(next_url or url_for('dashboard.dashboard'))

        else:
            flash('Invalid username or password')

    # If it's a GET request or form validation fails, render the login page
    return render_template('login.html', form=form)




@blueprint.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('auth.login'))
