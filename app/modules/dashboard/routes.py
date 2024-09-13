import os
import hashlib
from flask import Blueprint, redirect, render_template, flash, request, url_for
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from sqlalchemy.exc import IntegrityError
from app.modules.comments.models import Comments
from app.modules.notification.models import Notification
from app.modules.posts.models import Posts
from utilities.decorators import session_protection_required
from utilities.decorators_activity import timezone_required, track_activity_and_auto_logout
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
@session_protection_required
@track_activity_and_auto_logout
@timezone_required
def dashboard():
    form = DashboardForm()
    id = current_user.id
    user = Users.query.get_or_404(id)

    # Query data
    total_posts = Posts.query.count()
    user_posts_count = Posts.query.filter_by(poster_id=id).count()

    total_comments = Comments.query.count()
    user_posts_comments_count = Comments.query.join(Posts, Posts.id == Comments.post_id).filter(Posts.poster_id == id).count()
    user_comments_count = Comments.query.filter_by(commentor_id=id).count()

    total_notifications_received = Notification.query.filter_by(recipient_id=id).count()
    total_notifications_sent = Notification.query.filter_by(sender_id=id).count()

    total_notifications = Notification.query.count()

    # User with the most notifications sent to the current user
    top_notification_recipient = Users.query \
        .join(Notification, Users.id == Notification.sender_id) \
        .filter(Notification.recipient_id == current_user.id) \
        .group_by(Users.id) \
        .order_by(db.func.count(Notification.id).desc()) \
        .first()

    # User who received the most notifications from the current user
    top_notification_sender = Users.query \
        .join(Notification, Users.id == Notification.recipient_id) \
        .filter(Notification.sender_id == current_user.id) \
        .group_by(Users.id) \
        .order_by(db.func.count(Notification.id).desc()) \
        .first()

    # Calculate percentages
    posts_percentage = (user_posts_count / total_posts * 100) if total_posts > 0 else 0
    comments_on_user_posts_percentage = (user_posts_comments_count / total_comments * 100) if total_comments > 0 else 0
    user_comments_percentage = (user_comments_count / total_comments * 100) if total_comments > 0 else 0
    notifications_received_percentage = (total_notifications_received / total_notifications * 100) if total_notifications > 0 else 0
    notifications_sent_percentage = (total_notifications_sent / total_notifications * 100) if total_notifications > 0 else 0

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

                        if not os.path.exists(UPLOAD_FOLDER):
                            os.makedirs(UPLOAD_FOLDER)

                        file.save(file_path)
                        user.profile_pic = encrypted_filename
                    else:
                        if form.profile_pic.data:
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

    form.name.data = user.name
    form.email.data = user.email
    form.username.data = user.username
    form.about_author.data = user.about_author

    return render_template('users/body/dashboard.html', form=form, user=user, id=id,
                           user_posts_count=user_posts_count,
                           posts_percentage=posts_percentage,
                           user_posts_comments_count=user_posts_comments_count,
                           comments_on_user_posts_percentage=comments_on_user_posts_percentage,
                           user_comments_count=user_comments_count,
                           user_comments_percentage=user_comments_percentage,
                           total_notifications_received=total_notifications_received,
                           notifications_received_percentage=notifications_received_percentage,
                           total_notifications_sent=total_notifications_sent,
                           notifications_sent_percentage=notifications_sent_percentage,
                           top_notification_recipient=top_notification_recipient,
                           top_notification_sender=top_notification_sender)
