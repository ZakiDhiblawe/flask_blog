from flask import Flask, redirect, render_template, flash, request, url_for
from flask_wtf import FlaskForm
from wtforms import EmailField, IntegerField, PasswordField, StringField, SubmitField, BooleanField, TextAreaField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.widgets import TextArea
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from dotenv import load_dotenv
import os
from werkzeug.security import generate_password_hash, check_password_hash


load_dotenv()

# create instance fro flask
app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SECRET_KEY'] = 'you secret key'


class Zaki(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Submit')


# create database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# create Module


class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(200), nullable=False, unique=True)
    fovarite_food = db.Column(db.String(200))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    password_hash = db.Column(db.String(1000))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<Name %r>' % self.name


class UsersForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
    fovarite_food = StringField('Fovarite Food', validators=[DataRequired()])
    password_hash=PasswordField('Password', validators=[DataRequired() ,EqualTo('password_hash2', message='password mismatch')])
    password_hash2=PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Submit')


@app.route('/')
def index():

    uname = "Zaki Dhiblaawe"
    massage = f"Welcome to my page  i am <strong>{uname}</strong>"
    fovarite_food = ["pizza", "burger", "chicken", "rice", "meat", 247]

    return render_template('index.html',
                           name=uname,
                           massage=massage,
                           food=fovarite_food)


@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)


@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UsersForm()
    # Ensure `our_users` is always defined
    our_users = Users.query.order_by(Users.date_added).all()

    if form.validate_on_submit():
        pw_hashed = generate_password_hash('form.password_hash.data', 'scrypt')
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            user = Users(name=form.name.data, age=form.age.data,
                         email=form.email.data, 
                         fovarite_food=form.fovarite_food.data,
                         password_hash=pw_hashed)
            db.session.add(user)
            db.session.commit()
            flash('User added successfully')
        else:
            flash('User email already exists', 'danger')
        name = form.name.data
        form.name.data = ''
        form.age.data = ''
        form.email.data = ''
        form.fovarite_food.data = ''
        form.password_hash.data = ''

        # Update `our_users` after adding a new user
        our_users = Users.query.order_by(Users.date_added).all()

        # Format dates before passing to the template
        for user in our_users:
            user.formatted_date = user.date_added.strftime('%Y-%m-%d %H:%M:%S')

    return render_template('add.html', form=form, name=name, our_users=our_users)



# delete user
@app.route('/delete/<int:id>')
def delete(id):
    user_to_delete = Users.query.get_or_404(id)
    name = None
    form = UsersForm()
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash('User deleted successfully')
        our_users = Users.query.order_by(Users.date_added).all()
 
        return redirect(url_for('add_user', name=name, our_users=our_users))
    except:
        flash('Whoops! There was a problem deleting user, try again...')
        return render_template('add.html', form=form, name=name, our_users=our_users)

@app.route('/name', methods=['GET', 'POST'])
def name():
    name = None
    form = Zaki()
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash('Form submitted successfully')

    return render_template('name.htm', name=name, form=form)



@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update_user(id):
    form = UsersForm()
    name_updating = Users.query.get_or_404(id)
    
    if request.method == 'POST':
        if form.validate_on_submit():
            name_updating.name = form.name.data
            name_updating.age = form.age.data
            name_updating.email = form.email.data
            name_updating.fovarite_food = form.fovarite_food.data
            name_updating.password_hash = form.password_hash.data

            
            db.session.commit()
            flash('User updated successfully', 'success')
            return redirect(url_for('add_user'))  # Redirect to user list page
    
    # Pre-populate form fields with existing user data
    form.name.data = name_updating.name
    form.age.data = name_updating.age
    form.email.data = name_updating.email
    form.fovarite_food.data = name_updating.fovarite_food
    
    return render_template('update.html',
                                   form=form,
                                   name_updating=name_updating,
                                   id = id)

            

class Posts(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(500), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(255), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    slug = db.Column(db.String(500))
    

class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    content = TextAreaField("Content", validators=[DataRequired()], widget=TextArea())
    author = StringField("Author", validators=[DataRequired()])
    slug = StringField("Slug", validators=[DataRequired()])
    submit = SubmitField("Submit")



# add post route page
@app.route('/add-post', methods=['GET', 'POST'])
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Posts(title=form.title.data, content=form.content.data, author=form.author.data, slug=form.slug.data)
        form.title.data = ''
        form.content.data = ''
        form.author.data = ''
        form.slug.data = ''

        db.session.add(post)
        db.session.commit()
        flash('Post added successfully')
    return render_template('add_post.html', form=form)


@app.route('/posts')
def posts():
    posts = Posts.query.order_by(Posts.date_posted)
    return render_template('posts.html', posts=posts)


@app.route('/posts/<int:id>')
def post(id):
    post = Posts.query.get_or_404(id)
    return render_template('post.html', post=post)



# create a custom error page

# invalid url
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# internal server error


@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500


if __name__ == "__main__":
    # with app.app_context():
    #     db.create_all()
    #     print("Database tables created successfully!")
    app.run()
