from flask import Flask, redirect, render_template, flash
from flask_wtf import FlaskForm
from wtforms import EmailField, IntegerField, StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# create instance fro flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = 'you secret key'


class Zaki(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Submit')


# create database
db = SQLAlchemy(app)

# create Module


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(200), nullable=False, unique=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Name %r>' % self.name


class UsersForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
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
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            user = Users(name=form.name.data, age=form.age.data,
                         email=form.email.data)
            db.session.add(user)
            db.session.commit()
            flash('User added successfully')
        else:
            flash('User email already exists', 'danger')
        name = form.name.data
        form.name.data = ''
        form.age.data = ''
        form.email.data = ''

        # Update `our_users` after adding a new user
        our_users = Users.query.order_by(Users.date_added).all()

        # Format dates before passing to the template
        for user in our_users:
            user.formatted_date = user.date_added.strftime('%Y-%m-%d %H:%M:%S')

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


# create a custom error page

# invalid url
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# internal server error


@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500


# if __name__ == "__main__":
#     with app.app_context():
#         db.create_all()
#         print("Database tables created successfully!")
