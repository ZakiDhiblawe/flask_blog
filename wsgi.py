from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
import os
from app.modules.auth.models import Users
from app import create_app  # Import the create_app function from app package
from utilities.db import db, init_db
# Import the error blueprint

load_dotenv()

# Create the app using the factory function
app = create_app()

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_secret_key')

# Initialize database and migrations
init_db(app)

# Register error blueprint


# Login manager setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Users, int(user_id))


if __name__ == "__main__":
    app.run()
