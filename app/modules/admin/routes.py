from flask import Flask, redirect, render_template, flash, request, url_for, Blueprint
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, current_user, login_user, logout_user, LoginManager, login_required
from sqlalchemy.exc import IntegrityError
from utilities.db import db
from ..auth.models import Users  # Import the Users model
from ..posts.models import Posts  # Import the Posts model

blueprint = Blueprint('admin', __name__, url_prefix='/admin')

# Admin home page with filtering for posts
@blueprint.route('/')
@login_required
def index():
    if current_user.username == 'zaki':  # Assuming 'zaki' is the admin
        users = Users.query.all()

        # Filtering logic for posts
        author_filter = request.args.get('author')
        date_filter = request.args.get('date')
        topic_filter = request.args.get('topic')

        posts_query = Posts.query

        if author_filter:
            posts_query = posts_query.filter(Posts.poster.has(Users.name == author_filter))
        if date_filter:
            posts_query = posts_query.filter(Posts.date_posted.like(f'{date_filter}%'))
        if topic_filter:
            posts_query = posts_query.filter(Posts.slug.ilike(f'%{topic_filter}%'))

        posts = posts_query.all()

        return render_template('admin/index.html', users=users, posts=posts, author_filter=author_filter, date_filter=date_filter, topic_filter=topic_filter)
    else:
        flash('You are not authorized to access this page.', 'danger')
        return redirect(url_for('dashboard.dashboard'))

# Route to delete users
@blueprint.route('/delete_users', methods=['POST'])
@login_required
def delete_users():
    if current_user.username == 'zaki':
        user_ids = request.form.getlist('user_ids')
        try:
            for user_id in user_ids:
                user = Users.query.get(user_id)
                if user:
                    db.session.delete(user)
            db.session.commit()
            flash('Selected users deleted successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while deleting users.', 'danger')
    return redirect(url_for('admin.index'))

# Route to delete posts
@blueprint.route('/delete_posts', methods=['POST'])
@login_required
def delete_posts():
    if current_user.username == 'zaki':
        post_ids = request.form.getlist('post_ids')
        try:
            for post_id in post_ids:
                post = Posts.query.get(post_id)
                if post:
                    db.session.delete(post)
            db.session.commit()
            flash('Selected posts deleted successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while deleting posts.', 'danger')
    return redirect(url_for('admin.index'))

# Route to delete a single user
@blueprint.route('/delete_user/<int:user_id>', methods=['GET'])
@login_required
def delete_user(user_id):
    if current_user.username == 'zaki':
        user = Users.query.get(user_id)
        if user:
            try:
                db.session.delete(user)
                db.session.commit()
                flash('User deleted successfully!', 'success')
            except Exception as e:
                db.session.rollback()
                flash('An error occurred while deleting the user.', 'danger')
        else:
            flash('User not found.', 'danger')
    return redirect(url_for('admin.manage_users'))

# Route to delete a single post
@blueprint.route('/delete_post/<int:post_id>', methods=['GET'])
@login_required
def delete_post(post_id):
    if current_user.username == 'zaki':
        post = Posts.query.get(post_id)
        if post:
            try:
                db.session.delete(post)
                db.session.commit()
                flash('Post deleted successfully!', 'success')
            except Exception as e:
                db.session.rollback()
                flash('An error occurred while deleting the post.', 'danger')
        else:
            flash('Post not found.', 'danger')
    return redirect(url_for('admin.manage_posts'))

@blueprint.route('/filter_posts')
@login_required
def filter_posts():
    if current_user.username == 'zaki':
        users = Users.query.all()
        author_filter = request.args.get('author')
        date_from_filter = request.args.get('date_from')
        date_to_filter = request.args.get('date_to')
        topic_filter = request.args.get('topic')

        posts_query = Posts.query
        if author_filter:
            posts_query = posts_query.filter(Posts.poster.has(Users.name == author_filter))
        if date_from_filter and date_to_filter:
            posts_query = posts_query.filter(Posts.date_posted.between(date_from_filter, date_to_filter))
        if topic_filter:
            posts_query = posts_query.filter(Posts.slug.ilike(f'%{topic_filter}%'))

        posts = posts_query.all()

        return render_template('admin/posts.html', users=users, posts=posts, author_filter=author_filter,
                               date_from_filter=date_from_filter, date_to_filter=date_to_filter, topic_filter=topic_filter)
    else:
        flash('You are not authorized to access this page.', 'danger')
        return redirect(url_for('dashboard.dashboard'))

@blueprint.route('/manage_users')
@login_required
def manage_users():
    if current_user.username == 'zaki':
        users = Users.query.all()
        return render_template('admin/users.html', users=users)
    else:
        flash('You are not authorized to access this page.', 'danger')
        return redirect(url_for('dashboard.dashboard'))

@blueprint.route('/manage_posts')
@login_required
def manage_posts():
    if current_user.username == 'zaki':
        posts = Posts.query.all()
        return render_template('admin/posts.html', posts=posts)
    else:
        flash('You are not authorized to access this page.', 'danger')
        return redirect(url_for('dashboard.dashboard'))


@blueprint.route('/filter_users')
@login_required
def filter_users():
    if current_user.username == 'zaki':
        name_filter = request.args.get('name')
        date_from_filter = request.args.get('date_from')
        date_to_filter = request.args.get('date_to')
        username_filter = request.args.get('username')
        email_filter = request.args.get('email')

        users_query = Users.query
        if name_filter:
            users_query = users_query.filter(Users.name.ilike(f'%{name_filter}%'))
        if date_from_filter and date_to_filter:
            users_query = users_query.filter(Users.date_added.between(date_from_filter, date_to_filter))
        if username_filter:
            users_query = users_query.filter(Users.username.ilike(f'%{username_filter}%'))
        if email_filter:
            users_query = users_query.filter(Users.email.ilike(f'%{email_filter}%'))

        users = users_query.all()

        return render_template('admin/users.html', users=users, name_filter=name_filter,
                               date_from_filter=date_from_filter, date_to_filter=date_to_filter,
                               username_filter=username_filter, email_filter=email_filter)
    else:
        flash('You are not authorized to access this page.', 'danger')
        return redirect(url_for('dashboard.dashboard'))
