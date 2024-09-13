from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from utilities.db import db
from flask_login import UserMixin
from ..posts.models import Posts
from datetime import datetime, timedelta
import pytz

class Users(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False, unique=True)
    about_author = db.Column(db.Text(1000), nullable=True)
    profile_pic = db.Column(db.String(2000), nullable=True, default='default.jpeg')
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    reset_token = db.Column(db.String(1500), nullable=True)
    last_activity = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    session_id = db.Column(db.String(255), nullable=True)
    password_hash = db.Column(db.String(1000))
    # posts = db.relationship('Posts', backref='poster', lazy=True)
    # comments = db.relationship('Comments', backref='commentor', lazy=True)


    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<Name {self.name}>'

        

    @staticmethod
    def convert_utc_to_local(utc_dt, tz_str):
        if utc_dt is None:
            print("UTC datetime is None")
            return None
        print(f"UTC datetime: {utc_dt}, Timezone: {tz_str}")
        local_tz = pytz.timezone(tz_str)
        utc_dt = utc_dt.replace(tzinfo=pytz.utc)  # Ensure the datetime is in UTC
        local_dt = utc_dt.astimezone(local_tz)
        return local_dt


    @staticmethod
    def users_online_now(user_timezone):
        five_minutes_ago = datetime.utcnow() - timedelta(minutes=5)
        users = Users.query.filter(Users.last_activity >= five_minutes_ago).all()
        for user in users:
            if user.last_activity:
                user.last_activity_local = Users.convert_utc_to_local(user.last_activity, user_timezone)
        return users


    @staticmethod
    def users_active_today(user_timezone):
        today = datetime.utcnow().date()
        users = Users.query.filter(db.func.date(Users.last_activity) == today).all()
        for user in users:
            user.last_activity_local = Users.convert_utc_to_local(user.last_activity, user_timezone)
        return users

    @staticmethod
    def users_active_this_week(user_timezone):
        week_start = datetime.utcnow() - timedelta(days=datetime.utcnow().weekday())
        users = Users.query.filter(Users.last_activity >= week_start).all()
        for user in users:
            user.last_activity_local = Users.convert_utc_to_local(user.last_activity, user_timezone)
        return users

    @staticmethod
    def users_active_this_month(user_timezone):
        month_start = datetime.utcnow().replace(day=1)
        users = Users.query.filter(Users.last_activity >= month_start).all()
        for user in users:
            user.last_activity_local = Users.convert_utc_to_local(user.last_activity, user_timezone)
        return users

    @staticmethod
    def users_active_this_year(user_timezone):
        year_start = datetime.utcnow().replace(month=1, day=1)
        users = Users.query.filter(Users.last_activity >= year_start).all()
        for user in users:
            user.last_activity_local = Users.convert_utc_to_local(user.last_activity, user_timezone)
        return users

    @staticmethod
    def users_who_posted_today(user_timezone):
        today = datetime.utcnow().date()
        users = db.session.query(Users).join(Posts).filter(db.func.date(Posts.date_posted) == today).all()
        for user in users:
            user.last_activity_local = Users.convert_utc_to_local(user.last_activity, user_timezone)
        return users

    @staticmethod
    def users_with_most_posts(user_timezone):
        top_users = db.session.query(Users, db.func.count(Posts.id).label('total_posts')) \
            .join(Posts) \
            .group_by(Users.id) \
            .order_by(db.desc('total_posts')) \
            .limit(10).all()
        for user, _ in top_users:
            user.last_activity_local = Users.convert_utc_to_local(user.last_activity, user_timezone)
        return top_users
    
