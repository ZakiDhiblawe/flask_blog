import os
from dotenv import load_dotenv
from flask import Flask, redirect, render_template, flash, request, url_for, Blueprint
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, current_user, login_user, logout_user, LoginManager, login_required, login_remembered
from .forms import PostForm
from .models import Posts
from sqlalchemy.exc import IntegrityError
from utilities.db import db


blueprint = Blueprint('posts', __name__, url_prefix='/posts')





# add post route page
@blueprint.route('/add-post', methods=['GET', 'POST'])
@login_required
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        poster = current_user.id
        post = Posts(title=form.title.data, content=form.content.data, poster_id=poster ,slug=form.slug.data)
        form.title.data = ''
        form.content.data = ''

        form.slug.data = ''

        db.session.add(post)
        db.session.commit()
        flash('Post added successfully')
    return render_template('add_post.html', form=form)


@blueprint.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()
    id = current_user.id
    if id == post.poster_id:
        if form.validate_on_submit():
            post.title = form.title.data
            post.content = form.content.data
            post.slug = form.slug.data
            db.session.add(post)
            db.session.commit()
            flash('Post updated successfully')
            return redirect(url_for('public.post', id=post.id))
        form.title.data = post.title
        form.slug.data = post.slug
        form.content.data = post.content
        return render_template('edit_post.html', form=form)
    else:
        flash('You can only edit your own posts!')
        return redirect(url_for('public.posts'))



@blueprint.route('/posts/delete/<int:id>')
@login_required
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)
    id = current_user.id
    if id == post_to_delete.poster_id or current_user.username =='zaki':
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
    
    

