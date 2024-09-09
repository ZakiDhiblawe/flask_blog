from flask import render_template, Blueprint
from ..posts.models import Posts
from .forms import SearchForm


blueprint = Blueprint('public', __name__)


@blueprint.route('/')
def index():

    uname = "Zaki Dhiblaawe"
    massage = f"Welcome to my page  i am <strong>{uname}</strong>"
    fovarite_food = ["pizza", "burger", "chicken", "rice", "meat", 247]

    return render_template('index.html',
                           name=uname,
                           massage=massage,
                           food=fovarite_food)



@blueprint.route('/posts')
def posts():
    posts = Posts.query.order_by(Posts.date_posted)
    return render_template('posts.html', posts=posts)


@blueprint.route('/posts/<int:id>')
def post(id):
    post = Posts.query.get_or_404(id)
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
        posts = Posts.query.filter(Posts.content.like('%' + searched + '%')).order_by(Posts.title).all()
        return render_template('search.html', form=form, searched=searched, posts=posts)
    else:
        # For GET requests or if form is not valid
        return render_template('search.html', form=form, searched=None, posts=[])
