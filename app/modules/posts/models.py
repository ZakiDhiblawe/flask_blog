from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import re

from utilities.db import db

class Posts(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(500), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    slug = db.Column(db.String(500))
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))

def generate_slug(text):
    # Convert to lowercase
    text = text.lower()
    # Replace spaces with hyphens
    text = re.sub(r'\s+', '-', text)
    
    return text
