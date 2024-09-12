from datetime import datetime
from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from utilities.db import db

class Comments(db.Model):
    id = Column(Integer, primary_key=True)
    commentor_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    comment = Column(Text, nullable=False)
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False)
    date_commented = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relationship with Users
    commentor = db.relationship('Users', backref='comments')
    
    # Remove the redundant relationship definition for Posts
    # The relationship is defined in the Posts model with a different backref name.
