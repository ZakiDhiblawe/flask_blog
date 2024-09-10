from flask_wtf import FlaskForm
from wtforms import SubmitField

class DeleteUserForm(FlaskForm):
    submit = SubmitField('Delete User')

class DeletePostForm(FlaskForm):
    submit = SubmitField('Delete Post')
