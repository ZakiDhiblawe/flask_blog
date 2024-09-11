from flask import Flask, session, request
from utilities.timezone import get_user_timezone, set_user_timezone

app = Flask(__name__)
app.secret_key = 'supersecretkey'

@app.route('/set_timezone/<timezone>')
def set_timezone(timezone):
    set_user_timezone(timezone)
    return f"Timezone set to: {get_user_timezone()}"

@app.route('/get_timezone')
def show_timezone():
    return f"Current timezone is: {get_user_timezone()}"

if __name__ == '__main__':
    app.run(debug=True, port=5001)
