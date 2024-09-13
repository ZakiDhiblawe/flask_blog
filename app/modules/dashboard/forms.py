from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField
from flask_wtf.file import FileAllowed
from wtforms.validators import Optional, EqualTo




class DashboardForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    about_author = TextAreaField('About Author')
    profile_pic = FileField('Profile Pic', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!'), Optional()])
    submit = SubmitField('Update')




class PasswordChangeForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired()])
    submit = SubmitField('Change Password')


