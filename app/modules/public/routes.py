from flask import jsonify, render_template, Blueprint, request, session
import pytz

from utilities.decorators_activity import timezone_required, track_activity_and_auto_logout
from utilities.timezone import get_user_timezone
from ..posts.models import Posts
from .forms import SearchForm
from pytz import timezone



blueprint = Blueprint('public', __name__)


# @blueprint.route('/')
# def index():

#     uname = "Zaki Dhiblaawe"
#     massage = f"Welcome to my page  i am <strong>{uname}</strong>"
#     fovarite_food = ["pizza", "burger", "chicken", "rice", "meat", 247]

#     return render_template('public/body/index.html',
#                            name=uname,
#                            massage=massage,
#                            food=fovarite_food)



@blueprint.route('/')
def posts():
    page = request.args.get('page', 1, type=int)
    posts = Posts.query.order_by(Posts.date_posted.desc()).paginate(page=page, per_page=6)


    user_tz = pytz.timezone(get_user_timezone()) if get_user_timezone() else pytz.utc
    for post in posts.items:
        if post.date_posted.tzinfo is None:
            post.date_posted = pytz.utc.localize(post.date_posted)
        local_time = post.date_posted.astimezone(user_tz)
        post.local_time_formatted = local_time.strftime('%d %b, %Y %A at %H:%M')
        

    return render_template('public/body/index.html', posts=posts, page=page)



@blueprint.route('/posts/<slug>')
def post(slug):
    post = Posts.query.filter_by(slug=slug).first_or_404()
    return render_template('post.html', post=post)




# pass staf to the navbar
@blueprint.app_context_processor
def base():
    form = SearchForm()
    return dict(form=form)



@blueprint.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    if form.validate_on_submit():
        searched = form.searched.data
        page = request.args.get('page', 1, type=int)
        posts = Posts.query.filter(Posts.content.like('%' + searched + '%')).order_by(Posts.title).paginate(page=page, per_page=6)
        
        
        user_tz = pytz.timezone(get_user_timezone()) if get_user_timezone() else pytz.utc
        for post in posts.items:
            if post.date_posted.tzinfo is None:
                post.date_posted = pytz.utc.localize(post.date_posted)
            local_time = post.date_posted.astimezone(user_tz)
            post.local_time_formatted = local_time.strftime('%d %b, %Y %A at %H:%M')
        return render_template('public/body/search.html', form=form, searched=searched, posts=posts, page=page)
    else:
        # For GET requests or if form is not valid
        return render_template('public/body/search.html', form=form, searched=None, posts=[])
    


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


@blueprint.route('/about')
@timezone_required
def about():
    return render_template('public/body/about.html')
