"""Blogly application."""

from flask import Flask, redirect, render_template, url_for, request
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy import exc

from models import User, connect_db, db

app = Flask(__name__)
# database setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
connect_db(app)
db.create_all()
# debug setup
# app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = "test"
app.debug = True
tool_bar = DebugToolbarExtension(app)


@app.route('/')
def home_view():
    """
    Home page; redirects to users page.
    """
    return redirect(url_for('users_view'))


@app.route('/users')
def users_view():
    """
    Show all users; links each user to detail page; includes a link to add user.
    """
    return render_template('users.html', users=User.query.all())


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
        try:
            new_user = (
                User(first_name=first_name, last_name=last_name, image_url=url) if url
                else User(first_name=first_name, last_name=last_name)
            )
            db.session.add(new_user)
            db.session.commit()
        except exc.SQLAlchemyError:
            return redirect('new_user_view')
        return redirect(url_for('users_view'))

    return render_template('new_user.html')


@app.route('/users/<int:user_id>')
def user_detail_view(user_id):
    """
    Display user details (name, image) and buttons to edit or delete user.
    """
    return render_template(
        'user_detail.html', user=User.query.get(user_id),
        edit_url=url_for('edit_user_view', user_id=user_id),
        delete_url=url_for('delete_user', user_id=user_id)
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
        try:
            user = User.query.get(user_id)
            user.first_name = first_name
            user.last_name = last_name
            if url:
                user.image_url = url
            db.session.add(user)
            db.session.commit()
        except exc.SQLAlchemyError:
            return redirect(url_for('edit_user_view'))
        return redirect(url_for('user_detail_view', user_id=user_id))

    return render_template('edit_user.html', user=User.query.get(user_id))


@app.route('/users/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    """
    Query and delete user from db; redirect to users_view if succesful
    else redirect back to this page.
    """
    try:
        db.session.delete(User.query.get(user_id))
        db.session.commit()
    except exc.SQLAlchemyError:
        return redirect(url_for('user_detail_view', user_id=user_id))
    return redirect(url_for('users_view'))
