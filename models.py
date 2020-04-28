"""Models for Blogly."""
import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def connect_db(app):
    """Connect to database."""
    db.app = app
    db.init_app(app)


class User(db.Model):
    """User"""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(32), nullable=False)
    last_name = db.Column(db.String(32), nullable=False)
    image_url = db.Column(db.Text)

    __table_args__ = (
        db.CheckConstraint("image_url LIKE 'http%'"),
        # db.UniqueConstraint('first_name', 'last_name', name='unique_person'),
    )

    def __repr__(self):
        return (f"<User: first_name='{self.first_name}' "
                f"last_name='{self.last_name}' "
                f"hasImage={'yes' if self.image_url else 'no'}>")

    @property
    def full_name(self):
        """
        Return full name: first_name + last_name
        """
        return f"{self.first_name} {self.last_name}"


class Post(db.Model):
    """Post"""

    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(128), nullable=False, default="No Title")
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.Date, nullable=False, default=datetime.datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))

    user = db.relationship('User', backref=db.backref('posts', passive_deletes=True))

    def __repr__(self):
        return (f"<Post: id={self.id} "
                f"title='{self.title}' "
                f"created_at={self.created_at} "
                f"hasContent={'yes' if self.content else 'no'}>")