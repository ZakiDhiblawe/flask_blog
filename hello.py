from flask import Flask, redirect, render_template, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

# create instance fro flask
app = Flask(__name__)
app.config['SECRET_KEY']= 'you secret key'

class Zaki(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
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
