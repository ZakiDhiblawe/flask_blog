from flask import jsonify, render_template, Blueprint, request, session

from utilities.decorators_activity import timezone_required, track_activity_and_auto_logout
from utilities.timezone import get_user_timezone
from ..posts.models import Posts
from .forms import SearchForm


blueprint = Blueprint('public', __name__)


@blueprint.route('/')
@track_activity_and_auto_logout
def index():

    uname = "Zaki Dhiblaawe"
    massage = f"Welcome to my page  i am <strong>{uname}</strong>"
    fovarite_food = ["pizza", "burger", "chicken", "rice", "meat", 247]

    return render_template('index.html',
                           name=uname,
                           massage=massage,
                           food=fovarite_food)



@blueprint.route('/posts')
@track_activity_and_auto_logout
def posts():
    posts = Posts.query.order_by(Posts.date_posted)
    return render_template('posts.html', posts=posts)


@blueprint.route('/posts/<int:id>')
@track_activity_and_auto_logout
def post(id):
    post = Posts.query.get_or_404(id)
    return render_template('post.html', post=post)



# pass staf to the navbar
@blueprint.app_context_processor
def base():
    form = SearchForm()
    return dict(form=form)



@blueprint.route('/search', methods=['GET', 'POST'])
@track_activity_and_auto_logout
def search():
    form = SearchForm()
    if form.validate_on_submit():
        searched = form.searched.data
        posts = Posts.query.filter(Posts.content.like('%' + searched + '%')).order_by(Posts.title).all()
        return render_template('search.html', form=form, searched=searched, posts=posts)
    else:
        # For GET requests or if form is not valid
        return render_template('search.html', form=form, searched=None, posts=[])
    


@blueprint.route('/set-timezone', methods=['POST'])
def set_timezone():
    data = request.get_json()
    timezone = data.get('timezone')
    if timezone:
        session['user_timezone'] = timezone
        print(f"Timezone set to: {timezone}")  # Debugging line
        return jsonify({'status': 'success'}), 200
    return jsonify({'status': 'error', 'message': 'No timezone provided'}), 400


@blueprint.route('/check_timezone')
@timezone_required
def check_timezone():
    timezone = get_user_timezone()
    print(f"Timezone in session: {timezone}")  # Debugging line
    return f"Timezone in session: {timezone}"
