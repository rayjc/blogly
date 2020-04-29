"""Blogly application."""
import datetime

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_debugtoolbar import DebugToolbarExtension

from models import Post, PostTag, Tag, User, connect_db, db
from sqlalchemy import exc

app = Flask(__name__)
# database setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SQLALCHEMY_ECHO'] = True
connect_db(app)
db.create_all()
# debug setup
# app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = "test"
app.debug = True
tool_bar = DebugToolbarExtension(app)

def isValid(text):
    return text.isalnum()

@app.template_filter('datetime')
def format_datetime(value):
    return datetime.datetime.strftime(value, '%a %b %d %Y, %I:%M %p')

@app.route('/')
def index_view():
    """
    Index page: /home, /users, /tags
    """
    return render_template(
        'index.html'
    )

@app.route('/home')
def home_view():
    """
    Home page; redirects to users page.
    """
    return render_template(
        'home.html', posts=Post.query.order_by(Post.created_at.desc())
    )


# User Views
@app.route('/users')
def users_view():
    """
    Show all users; links each user to detail page; includes a link to add user.
    """
    return render_template(
        'users.html',
        users=User.query.order_by(User.last_name, User.first_name).all()
    )


@app.route('/users/new', methods=['GET', 'POST'])
def new_user_view():
    """
    GET: Display form for adding a new user.
    POST:
        Create new user and commit to db; redirect to users_view if successful,
        else redirect to this page.
    """
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        url = request.form.get('image_url')
        if not isValid(first_name) or not isValid(last_name):
            flash(
                'Invalid characters detected! '
                'Please only use alphabetical letters or numbers.',
                'danger'
            )
            return redirect(url_for('new_user_view'))

        try:
            new_user = (
                User(first_name=first_name, last_name=last_name, image_url=url) if url
                else User(first_name=first_name, last_name=last_name)
            )
            db.session.add(new_user)
            db.session.commit()
            flash('Success: user created!', 'success')
        except exc.SQLAlchemyError:
            flash('Failed to add user', 'danger')
            return redirect(url_for('new_user_view'))
        return redirect(url_for('users_view'))

    return render_template('new_user.html')


@app.route('/users/<int:user_id>')
def user_detail_view(user_id):
    """
    Display user details (name, image) and buttons to edit or delete user.
    """
    user = User.query.get_or_404(user_id)
    return render_template(
        'user_detail.html', user=user,
        edit_url=url_for('edit_user_view', user_id=user_id),
        delete_url=url_for('delete_user', user_id=user_id),
        posts=user.posts, new_post_url=url_for('new_post_view', user_id=user_id)
    )


@app.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
def edit_user_view(user_id):
    """
    GET: Display form for editing a user.
    POST:
        Query and update user and commit to db;
        redirect to user_detail_view if successful,
        else redirect to this page.
    """
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        url = request.form.get('image_url')
        if not isValid(first_name) or not isValid(last_name):
            flash(
                'Invalid characters detected! '
                'Please only use alphabetical letters or numbers.',
                'danger'
            )
            return redirect(url_for('new_user_view'))

        try:
            user = User.query.get_or_404(user_id)
            user.first_name = first_name
            user.last_name = last_name
            if url:
                user.image_url = url
            db.session.add(user)
            db.session.commit()
            flash('Success: user updated!', 'success')
        except exc.SQLAlchemyError:
            flash('Failed to update user', 'danger')
            return redirect(url_for('edit_user_view', user_id=user_id))
        return redirect(url_for('user_detail_view', user_id=user_id))

    return render_template('edit_user.html', user=User.query.get(user_id))


@app.route('/users/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    """
    Query and delete user from db; redirect to users_view if succesful
    else redirect back to this page.
    """
    try:
        db.session.delete(User.query.get_or_404(user_id))
        db.session.commit()
        flash('Success: user deleted', 'success')
    except exc.SQLAlchemyError:
        flash('Failed to delete user', 'danger')
        return redirect(url_for('users_view'))
    return redirect(url_for('users_view'))


# Post Views
@app.route('/users/<int:user_id>/posts/new', methods=['GET', 'POST'])
def new_post_view(user_id):
    """
    GET: Display form for adding a new post.
    POST:
        Create new post and commit to db; redirect to user_detail_view if successful,
        else redirect to this page.
    """
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        tag_ids = request.form.getlist('tags')

        try:
            new_post = Post(title=title, content=content, user_id=user_id)
            new_post.posttags.extend([
                PostTag(post_id=new_post.id, tag_id=tag_id)
                for tag_id in tag_ids
            ])

            db.session.add(new_post)
            db.session.commit()
            flash('Success: post created!', 'success')
        except exc.SQLAlchemyError:
            flash('Failed to create post', 'danger')
            return redirect(url_for('new_post_view', user_id=user_id))
        
        return redirect(url_for('user_detail_view', user_id=user_id))

    return render_template(
        'new_post.html',
        user_name=User.query.get_or_404(user_id).full_name,
        tags=Tag.query.order_by(Tag.name).all()
    )


@app.route('/posts/<int:post_id>')
def post_detail_view(post_id):
    """
    Display post details (title, content, author) and buttons to edit or delete post.
    """
    post = Post.query.get_or_404(post_id)
    return render_template(
        'post_detail.html', post=post,
        user_url=url_for('user_detail_view', user_id=post.user_id),
        edit_url=url_for('edit_post_view', post_id=post_id),
        delete_url=url_for('delete_post', post_id=post_id)
    )


@app.route('/posts/<int:post_id>/edit', methods=['GET', 'POST'])
def edit_post_view(post_id):
    """
    GET: Display form for editing the post.
    POST:
        Query and update post and commit to db;
        redirect to post_detail_view if successful,
        else redirect to this page.
    """
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        tag_ids = set(map(lambda item: int(item), request.form.getlist('tags')))

        try:
            post = Post.query.get_or_404(post_id)
            post.title = title
            post.content = content
            old_tag_ids = set(map(lambda item: item.tag_id, post.posttags))
            # associate post with new tags
            post.posttags.extend([
                PostTag(post_id=post.id, tag_id=tag_id)
                for tag_id in (tag_ids - old_tag_ids)
            ])
            db.session.add(post)
            db.session.commit()

            # dissociate post with removed tags
            db.session.query(PostTag).filter(
                PostTag.tag_id.in_(old_tag_ids - tag_ids)
            ).delete(synchronize_session='fetch')
            db.session.commit()
            flash('Success: post updated!', 'success')
        except exc.SQLAlchemyError:
            flash('Failed to update post', 'danger')
            return redirect(url_for('edit_post_view', post_id=post_id))
        
        return redirect(url_for('post_detail_view', post_id=post_id))

    return render_template(
        'edit_post.html', post=Post.query.get(post_id),
        tags=Tag.query.order_by(Tag.name).all()
    )


@app.route('/posts/<int:post_id>/delete', methods=['POST'])
def delete_post(post_id):
    """
    Query and delete post from db; redirect to post_detail_view if succesful
    else redirect back to this page.
    """
    try:
        post = Post.query.get_or_404(post_id)
        db.session.delete(post)
        db.session.commit()
        flash('Success: post deleted!', 'success')
    except exc.SQLAlchemyError:
        flash('Failed to delete post', 'danger')
        return redirect(url_for('post_detail_view', post_id=post_id))
    return redirect(url_for('user_detail_view', user_id=post.user_id))


# Tag views
@app.route('/tags')
def tags_view():
    """
    Show all tags; links each tag to detail page; includes a link to add tag.
    """
    return render_template(
        'tags.html',
        tags=Tag.query.order_by(Tag.name).all()
    )


@app.route('/tags/<int:tag_id>')
def tag_detail_view(tag_id):
    """
    Display tag details (title, content, author) and buttons to edit or delete tag.
    """
    tag = Tag.query.get_or_404(tag_id)
    return render_template(
        'tag_detail.html', tag=tag, posts=tag.posts,
        tags_url=url_for('tags_view'),
        edit_url=url_for('edit_tag_view', tag_id=tag_id),
        delete_url=url_for('delete_tag', tag_id=tag_id)
    )


@app.route('/tags/new', methods=['GET', 'POST'])
def new_tag_view():
    """
    GET: Display form for adding a new tag.
    POST:
        Create new tag and commit to db; redirect to user_detail_view if successful,
        else redirect to this page.
    """
    if request.method == 'POST':
        name = request.form.get('name')
        post_ids = request.form.getlist('posts')
        try:
            new_tag = Tag(name=name)
            new_tag.posttags.extend([
                PostTag(post_id=post_id, tag_id=new_tag.id)
                for post_id in post_ids
            ])
            db.session.add(new_tag)
            db.session.commit()
            flash('Success: tag created!', 'success')
        except exc.SQLAlchemyError:
            flash('Failed to create tag', 'danger')
            return redirect(url_for('new_tag_view'))
        return redirect(url_for('tags_view'))

    return render_template(
        'new_tag.html',
        posts=Post.query.order_by(Post.title).all()
    )

@app.route('/tags/<int:tag_id>/edit', methods=['GET', 'POST'])
def edit_tag_view(tag_id):
    """
    GET: Display form for editing the tag.
    POST:
        Query and update tag and commit to db;
        redirect to tag_detail_view if successful,
        else redirect to this page.
    """
    if request.method == 'POST':
        name = request.form.get('name')
        post_ids = request.form.getlist('posts')

        try:
            tag = Tag.query.get_or_404(tag_id)
            tag.name = name

            # remove all rows in posts_tags under this tag
            db.session.query(PostTag).filter(
                PostTag.tag_id == tag.id
            ).delete(synchronize_session='fetch')
            db.session.commit()

            # add all checked posts to posts_tags
            tag.posttags.extend([
                PostTag(post_id=post_id, tag_id=tag.id)
                for post_id in post_ids
            ])
            db.session.add(tag)
            db.session.commit()

            flash('Success: tag updated!', 'success')
        except exc.SQLAlchemyError:
            flash('Failed to update tag', 'danger')
            return redirect(url_for('edit_tag_view', tag_id=tag_id))
        return redirect(url_for('tag_detail_view', tag_id=tag_id))
    
    tag = Tag.query.get(tag_id)
    # extract list of posts under this tag
    existing_post_ids = list(map(lambda item: item.id, tag.posts))
    return render_template(
        'edit_tag.html', tag=tag,
        posts=Post.query.order_by(Post.title).all(),
        checked_post_ids=existing_post_ids
    )


@app.route('/tags/<int:tag_id>/delete', methods=['POST'])
def delete_tag(tag_id):
    """
    Query and delete tag from db; redirect to tag_detail_view if succesful
    else redirect back to this page.
    """
    try:
        tag = Tag.query.get_or_404(tag_id)
        db.session.delete(tag)
        db.session.commit()
        flash('Success: tag deleted!', 'success')
    except exc.SQLAlchemyError:
        flash('Failed to delete tag', 'danger')
        return redirect(url_for('tag_detail_view', tag_id=tag_id))
    return redirect(url_for('tags_view'))
