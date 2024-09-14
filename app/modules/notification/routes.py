from flask import current_app, render_template, redirect, url_for, flash, Blueprint, request, jsonify
from flask_login import current_user, login_required
import pytz
from utilities.db import db
from utilities.decorators_activity import timezone_required, track_activity_and_auto_logout
from utilities.timezone import get_user_timezone
from .models import Notification
from ..auth.models import Users
from .forms import AdminNotificationForm, UserNotificationForm

blueprint = Blueprint('notification', __name__, url_prefix='/notification')

@blueprint.route('/inbox', methods=['GET', 'POST'])
@login_required
@track_activity_and_auto_logout
@timezone_required
def inbox():
    form = AdminNotificationForm() if current_user.username == 'zaki' else UserNotificationForm()

    if current_user.username == 'zaki':
        form.recipients.choices = [(user.id, user.username) for user in Users.query.all()]
        if form.validate_on_submit():
            recipients = Users.query.all() if form.select_all.data else Users.query.filter(Users.id.in_(form.recipients.data)).all()
            user_tz = pytz.timezone(get_user_timezone()) if get_user_timezone() else pytz.utc

            for recipient in recipients:
                notification = Notification(
                    sender_id=current_user.id,
                    recipient_id=recipient.id,
                    subject=form.subject.data,
                    message=form.message.data,
                )
                db.session.add(notification)
            db.session.commit()
            flash('Notifications sent successfully!', 'success')
            return redirect(url_for('notification.inbox'))
        notifications = Notification.query.filter(
            (Notification.sender_id == current_user.id) | (Notification.recipient_id == current_user.id)
        ).all()
    else:
        if form.validate_on_submit():
            recipient = Users.query.filter_by(email=form.recipient_email.data).first()
            if recipient:
                notification = Notification(
                    sender_id=current_user.id,
                    recipient_id=recipient.id,
                    subject=form.subject.data,
                    message=form.message.data,
                )
                db.session.add(notification)
                db.session.commit()
                flash('Notification sent successfully!', 'success')
            else:
                flash('Recipient email not found!', 'danger')
            return redirect(url_for('notification.inbox'))
        notifications = Notification.query.filter(
            (Notification.sender_id == current_user.id) | (Notification.recipient_id == current_user.id)
        ).all()
        for notification in notifications:
            if notification.recipient_id == current_user.id:
                notification.read_unread = True
        db.session.commit()

    # Prepare local time for each notification
    user_tz = pytz.timezone(get_user_timezone()) if get_user_timezone() else pytz.utc
    for notification in notifications:
        if notification.timestamp.tzinfo is None:
            notification.timestamp = pytz.utc.localize(notification.timestamp)
        local_time = notification.timestamp.astimezone(user_tz)
        notification.local_time_formatted = local_time.strftime('%d %b, %Y %A at %H:%M')

    # Add sender info
    for notification in notifications:
        if notification.sender.username == 'zaki':
            notification.sender_name = 'System Admin'
            notification.sender_email = 'admin@noreply.admin'
        else:
            notification.sender_name = notification.sender.username
            notification.sender_email = notification.sender.email

    return render_template('users/body/inbox.html', form=form, notifications=notifications, is_admin=current_user.username == 'zaki', Users=Users)

@blueprint.route('/toggle_read_status/<int:notification_id>', methods=['POST'])
@login_required
@track_activity_and_auto_logout
def toggle_read_status(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    if notification.recipient_id == current_user.id or current_user.username == 'zaki':
        notification.read_unread = not notification.read_unread
        db.session.commit()
        return {'status': 'success'}, 200
    return {'status': 'error', 'message': 'Unauthorized'}, 403

@blueprint.route('/unread_count', methods=['GET'])
@login_required
@track_activity_and_auto_logout
@timezone_required
def unread_count():
    count = Notification.query.filter_by(recipient_id=current_user.id, read_unread=False).count()
    return jsonify({'unread_count': count})

@blueprint.route('/last_unread', methods=['GET'])
@login_required
def last_unread():
    # Get the last four unread messages for the current user
    unread_notifications = Notification.query.filter_by(recipient_id=current_user.id, read_unread=False).order_by(Notification.timestamp.desc()).limit(4).all()

    # Get user's timezone or default to UTC
    user_tz = pytz.timezone(get_user_timezone()) if get_user_timezone() else pytz.utc

    notifications_data = []
    for notification in unread_notifications:
        # Convert the timestamp to the user's local time
        if notification.timestamp.tzinfo is None:
            notification.timestamp = pytz.utc.localize(notification.timestamp)
        local_time = notification.timestamp.astimezone(user_tz)
        local_time_formatted = local_time.strftime('%d %b, %Y %H:%M')

        notifications_data.append({
            'subject': notification.subject,
            'message': notification.message,
            'local_time': local_time_formatted,
            'sender_name': notification.sender.username,
        })
    
    return jsonify(notifications_data), 200




@blueprint.route('/clear_notifications', methods=['POST'])
@login_required
@track_activity_and_auto_logout
def clear_notifications():
    unread_notifications = Notification.query.filter_by(recipient_id=current_user.id, read_unread=False).all()
    
    for notification in unread_notifications:
        notification.read_unread = True  # Mark all notifications as read
    
    db.session.commit()

    return jsonify({'status': 'success'}), 200

