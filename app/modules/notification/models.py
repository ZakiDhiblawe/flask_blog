from utilities.db import db
from datetime import datetime

class Notification(db.Model):
    __tablename__ = 'notification'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subject = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    read_unread = db.Column(db.Boolean, default=False)
    seen = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)

    # Relationship with Users model
    sender = db.relationship('Users', foreign_keys=[sender_id], backref='sent_notifications')
    recipient = db.relationship('Users', foreign_keys=[recipient_id], backref='received_notifications')

    def __repr__(self):
        return f'<Notification {self.subject}>'
