from flask_wtf import FlaskForm
from wtforms import EmailField,  IntegerField, PasswordField, StringField, SubmitField, BooleanField, TextAreaField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.widgets import TextArea
from flask_wtf.file import FileField


class UsersForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    password_hash=PasswordField('Password', validators=[DataRequired() ,EqualTo('password_hash2', message='password mismatch')])
    password_hash2=PasswordField('Confirm Password', validators=[DataRequired()])
    profile_pic = FileField('Profile Pic')
    submit = SubmitField('Submit')


# create loging form 
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')


