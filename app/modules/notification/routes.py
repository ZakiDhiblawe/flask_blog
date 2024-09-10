from flask import render_template, redirect, url_for, flash, Blueprint
from flask_login import current_user, login_required
from utilities.db import db
from .models import Notification
from ..auth.models import Users
from .forms import AdminNotificationForm, UserNotificationForm

blueprint = Blueprint('notification', __name__, url_prefix='/notification')

@blueprint.route('/notifications/send', methods=['GET', 'POST'])
@login_required
def send_notification():
    if current_user.username == 'zaki':  # Check if current user is admin
        form = AdminNotificationForm()
        form.recipients.choices = [(user.id, user.username) for user in Users.query.all()]
        if form.validate_on_submit():
            if form.select_all.data:
                recipients = Users.query.all()
            else:
                recipients = Users.query.filter(Users.id.in_(form.recipients.data)).all()
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
            return redirect(url_for('dashboard.dashboard'))
        return render_template('send_notification.html', form=form)
    else:  # Regular user
        form = UserNotificationForm()
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
            return redirect(url_for('dashboard.dashboard'))
        return render_template('send_notification.html', form=form)



@blueprint.route('/notifications')
@login_required
def receive_notifications():
    notifications = Notification.query.filter_by(recipient_id=current_user.id).all()
    admin = Users.query.filter_by(username='zaki').first()  # Replace 'zaki' with your admin's username or ID retrieval logic
    admin_id = admin.id if admin else None
    return render_template('receive_notifications.html', notifications=notifications, admin_id=admin_id)

