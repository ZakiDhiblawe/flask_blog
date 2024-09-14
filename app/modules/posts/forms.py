from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from wtforms import EmailField, StringField, SubmitField, TextAreaField
from flask_ckeditor import CKEditorField

class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    description = TextAreaField('About The Post') # New description field
    content = CKEditorField("Content", validators=[DataRequired()])
    slug = StringField("Slug", validators=[DataRequired()])
    category = StringField("Category")  # Category field
    image_uri = StringField("Image URI")  # Image URI field
    submit = SubmitField("Publish")
