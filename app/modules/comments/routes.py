from flask import redirect, render_template, flash, url_for, Blueprint
from flask_login import current_user, login_required
from utilities.db import db
from .models import Comments
from .forms import CommentForm
from ..posts.models import Posts

blueprint = Blueprint('comments', __name__, url_prefix='/comments')

@blueprint.route('/add-comment/<int:post_id>', methods=['POST'])
@login_required
def add_comment(post_id):
    form = CommentForm()
    if form.validate_on_submit():
        post = Posts.query.get_or_404(post_id)
        comment = Comments(
            commentor_id=current_user.id,
            comment=form.comment.data,
            post_id=post_id
        )
        db.session.add(comment)
        post.comments_count += 1  # Increment comment count
        db.session.commit()
        flash('Comment added successfully!')
    else:
        flash('Comment could not be added. Please try again.')
    return redirect(url_for('posts.post', slug=post.slug))

@blueprint.route('/delete-comment/<int:comment_id>', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comments.query.get_or_404(comment_id)
    post = Posts.query.get_or_404(comment.post_id)
    if current_user.id == comment.commentor_id or current_user.username == 'zaki':
        try:
            db.session.delete(comment)
            post.comments_count -= 1  # Decrement comment count
            db.session.commit()
            flash('Comment deleted successfully!')
        except:
            flash('There was a problem deleting the comment. Please try again.')
    else:
        flash('You can only delete your own comments!')
    return redirect(url_for('posts.post', slug=post.slug))
