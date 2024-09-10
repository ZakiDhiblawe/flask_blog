from flask import render_template, redirect, url_for, flash, Blueprint
from flask_login import current_user, login_required
from utilities.db import db
from .models import Notification
from ..auth.models import Users
from .forms import AdminNotificationForm, UserNotificationForm

blueprint = Blueprint('notification', __name__, url_prefix='/notification')

@blueprint.route('/inbox', methods=['GET', 'POST'])
@login_required
def inbox():
    form = AdminNotificationForm() if current_user.username == 'zaki' else UserNotificationForm()
    
    if current_user.username == 'zaki':
        form.recipients.choices = [(user.id, user.username) for user in Users.query.all()]
        if form.validate_on_submit():
            recipients = Users.query.all() if form.select_all.data else Users.query.filter(Users.id.in_(form.recipients.data)).all()
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

    # Add a flag to indicate if the sender is the admin
    for notification in notifications:
        if notification.sender.username == 'zaki':
            notification.sender_name = 'System Admin'
            notification.sender_email = 'admin@noreply.admin'
        else:
            notification.sender_name = notification.sender.username
            notification.sender_email = notification.sender.email

    return render_template('inbox.html', form=form, notifications=notifications, is_admin=current_user.username == 'zaki', Users=Users)



@blueprint.route('/toggle_read_status/<int:notification_id>', methods=['POST'])
@login_required
def toggle_read_status(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    if notification.recipient_id == current_user.id or current_user.username == 'zaki':
        notification.read_unread = not notification.read_unread
        db.session.commit()
        return {'status': 'success'}, 200
    return {'status': 'error', 'message': 'Unauthorized'}, 403


@blueprint.route('/unread_count', methods=['GET'])
@login_required
def unread_count():
    count = Notification.query.filter_by(recipient_id=current_user.id, read_unread=False).count()
    return {'unread_count': count}

