from flask_sqlalchemy import SQLAlchemy 
from datetime import datetime
import re

from utilities.db import db

class Posts(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text(1000), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    slug = db.Column(db.String(500))
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    category = db.Column(db.String(100))
    image_uri = db.Column(db.String(1500))
    comments_count = db.Column(db.Integer, default=0)

    # Relationship with Users
    poster = db.relationship('Users', backref='user_posts', lazy=True)
    
    # Relationship with Comments (Updated backref name)
    comments = db.relationship('Comments', backref='post_comments', lazy=True)

def generate_slug(text):
    text = text.lower()
    text = re.sub(r'\s+', '-', text)
    return text
