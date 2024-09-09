from flask_wtf import FlaskForm
from wtforms import EmailField, IntegerField, PasswordField, StringField, SubmitField, BooleanField, TextAreaField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.widgets import TextArea
from flask_wtf.file import FileField
from flask_wtf.file import FileAllowed
from wtforms.validators import Optional




class DashboardForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    about_author = TextAreaField('About Author')
    profile_pic = FileField('Profile Pic', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!'), Optional()])
    submit = SubmitField('Update')


