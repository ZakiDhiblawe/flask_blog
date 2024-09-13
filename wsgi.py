from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
import os
from app.modules.auth.models import Users
from app import create_app  # Import the create_app function from app package
from utilities.db import db, init_db
from utilities.mail import init_mail
# Import the error blueprint

load_dotenv()

# Create the app using the factory function
app = create_app()

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'd98fe0facb0c6762cedgjfumsdopnvohrweuoe vtrgywegry0cf3e21b6fbdea6c94dc27152589420286212ade8474a9cd7c3aae958e5967d8e0a2013f43efd278c8f82ed7d3131201775e6a6e562bd5')

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587  # For TLS
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME')

# Initialize database and migrations
init_db(app)
init_mail(app)
# Register error blueprint


# Login manager setup
login_manager = LoginManager()
login_manager.session_protection = 'strong'  # Ensures each session is unique
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Users, int(user_id))


if __name__ == '__main__':
    # with app.app_context():
    #     db.create_all()
    #     print("Database tables created successfully!")
    app.run(debug=True)


