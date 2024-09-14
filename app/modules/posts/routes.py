from flask import redirect, render_template, flash, request, url_for, Blueprint
from flask_login import current_user, login_required
import pytz
from app.modules.comments.forms import CommentForm
from utilities.decorators import session_protection_required
from utilities.decorators_activity import timezone_required, track_activity_and_auto_logout
from utilities.timezone import get_user_timezone
from .forms import PostForm
from .models import Posts, generate_slug
from utilities.db import db
from ..comments.models import Comments

blueprint = Blueprint('posts', __name__, url_prefix='/posts')

@blueprint.route('/add-post', methods=['GET', 'POST'])
@login_required
@session_protection_required
@track_activity_and_auto_logout
@timezone_required
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        poster = current_user.id
        slug = generate_slug(form.slug.data)
        post = Posts(
            title=form.title.data,
            description=form.description.data,  # Use description instead of content
            content = form.content.data,
            poster_id=poster,
            slug=slug,
            category=form.category.data,
            image_uri=form.image_uri.data
        )
        db.session.add(post)
        db.session.commit()
        flash('Post added successfully')
        return redirect(url_for('public.posts'))
    return render_template('users/body/add_post.html', form=form)

@blueprint.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@track_activity_and_auto_logout
@session_protection_required
@timezone_required
def edit_post(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()
    if current_user.id == post.poster_id:
        if form.validate_on_submit():
            post.title = form.title.data
            post.description = form.description.data  # Update description
            post.content = form.content.data  # Update content
            post.slug = generate_slug(form.slug.data)
            post.category = form.category.data
            post.image_uri = form.image_uri.data
            db.session.commit()
            flash('Post updated successfully')
            return redirect(url_for('posts.post', slug=post.slug))
        form.title.data = post.title
        form.slug.data = post.slug
        form.description.data = post.description  # Pre-fill description
        form.content.data = post.content  # Pre-fill content
        form.category.data = post.category
        form.image_uri.data = post.image_uri
        return render_template('users/body/edit_post.html', form=form)
    else:
        flash('You can only edit your own posts!')
        return redirect(url_for('public.posts'))

@blueprint.route('/posts/delete/<int:id>')
@login_required
@session_protection_required
@track_activity_and_auto_logout
@timezone_required
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)
    user_id = current_user.id
    if user_id == post_to_delete.poster_id or current_user.username == 'zaki':
        try:
            db.session.delete(post_to_delete)
            db.session.commit()
            flash('Post deleted successfully')
            return redirect(url_for('public.posts'))
        except:
            flash('Whoops! There was a problem deleting post, try again...')
            return redirect(url_for('public.posts'))
    else:
        flash('You can only delete your own posts!')
        return redirect(url_for('public.posts'))




@blueprint.route('/posts/<slug>', methods=['GET', 'POST'])
def post(slug):
    post = Posts.query.filter_by(slug=slug).first_or_404()
    form = CommentForm()
    comments = Comments.query.filter_by(post_id=post.id).all()
    

    if form.validate_on_submit():
        comment = Comments(
            commentor_id=current_user.id,
            comment=form.comment.data,
            post_id=post.id
        )
        db.session.add(comment)
        post.comments_count += 1  # Increment comment count
        db.session.commit()
        flash('Comment added successfully!')
        return redirect(url_for('posts.post', slug=post.slug))
    
    categories = [category[0] for category in Posts.query.with_entities(Posts.category).distinct().limit(6).all()]
    
    user_tz = pytz.timezone(get_user_timezone()) if get_user_timezone() else pytz.utc
    for comment in comments:
        if comment.date_commented.tzinfo is None:
            comment.date_commented = pytz.utc.localize(comment.date_commented)
            local_time = comment.date_commented.astimezone(user_tz)
            comment.local_time_formatted = local_time.strftime('%d %b, %Y %A at %H:%M')
    recent_posts = Posts.query.order_by(Posts.date_posted.desc()).limit(3).all()
    return render_template('public/body/post.html', post=post, comments=comments, form=form, categories=categories, recent_posts=recent_posts)


@blueprint.route('/my-posts', methods=['GET'])
@login_required
@session_protection_required
@track_activity_and_auto_logout
@timezone_required
def my_posts():
    page = request.args.get('page', 1, type=int)
    
    # Paginate the user's posts
    user_posts = Posts.query.filter_by(poster_id=current_user.id).order_by(Posts.date_posted.desc()).paginate(page=page, per_page=6)
    
    user_tz = pytz.timezone(get_user_timezone()) if get_user_timezone() else pytz.utc
    for post in user_posts.items:
        # Convert the post's date_posted to the user's timezone
        if post.date_posted.tzinfo is None:
            post.date_posted = pytz.utc.localize(post.date_posted)
        local_time = post.date_posted.astimezone(user_tz)
        post.local_time_formatted = local_time.strftime('%d %b, %Y %A at %H:%M')
    
    return render_template('users/body/my_posts.html', posts=user_posts)
