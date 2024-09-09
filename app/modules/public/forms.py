from flask_wtf import FlaskForm
from wtforms import EmailField, IntegerField, PasswordField, StringField, SubmitField, BooleanField, TextAreaField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.widgets import TextArea



class SearchForm(FlaskForm):
    searched = StringField("Search", validators=[DataRequired()])
    submit = SubmitField("Submit")