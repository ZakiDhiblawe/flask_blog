from flask import Flask, render_template

# create instance fro flask
app = Flask(__name__)


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


# create a custom error page 

# invalid url 
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# internal server error
@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500
