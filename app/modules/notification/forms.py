from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectMultipleField, BooleanField
from wtforms.validators import DataRequired, Email

class AdminNotificationForm(FlaskForm):
    select_all = BooleanField('Select All Users')
    recipients = SelectMultipleField('Recipients', coerce=int)
    subject = StringField('Subject', validators=[DataRequired()])
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send Notification')

class UserNotificationForm(FlaskForm):
    recipient_email = StringField('Recipient Email', validators=[DataRequired(), Email()])
    subject = StringField('Subject', validators=[DataRequired()])
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send Notification')
