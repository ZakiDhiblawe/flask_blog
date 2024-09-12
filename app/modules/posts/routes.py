from flask import redirect, render_template, flash, url_for, Blueprint
from flask_login import current_user, login_required
from app.modules.comments.forms import CommentForm
from utilities.decorators import session_protection_required
from utilities.decorators_activity import timezone_required, track_activity_and_auto_logout
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
    return render_template('add_post.html', form=form)

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
            return redirect(url_for('public.posts', slug=post.slug))
        form.title.data = post.title
        form.slug.data = post.slug
        form.description.data = post.description  # Pre-fill description
        form.content.data = post.content  # Pre-fill content
        form.category.data = post.category
        form.image_uri.data = post.image_uri
        return render_template('edit_post.html', form=form)
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

    recent_posts = Posts.query.order_by(Posts.date_posted.desc()).limit(3).all()
    return render_template('public/body/post.html', post=post, comments=comments, form=form, categories=categories, recent_posts=recent_posts)

