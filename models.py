"""Models for Blogly."""
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
        return (f"<User: first_name={self.first_name} "
                f"last_name={self.last_name} "
                f"hasImage={'yes' if self.image_url else 'no'}>")