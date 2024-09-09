from flask import Flask
from .modules.public import public
from .modules.auth import auth
from .modules.dashboard import dashboard
from .modules.posts import posts
from .modules.admin import admin
from utilities.error import error  
from flask_ckeditor import CKEditor

# Function to create the Flask app
def create_app():
    app = Flask(__name__)
    ckeditor =  CKEditor(app)

    # Register blueprints
    blueprint_list = [public, auth, dashboard, posts, admin]
    for bp in blueprint_list:
        app.register_blueprint(bp)
    
    app.register_blueprint(error)
    return app
