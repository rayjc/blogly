"""Seed file to make sample data for blogly db."""
import datetime

from app import app
from models import Post, User, db, Tag

# Create all tables
db.drop_all()
db.create_all()

# If table isn't empty, empty it
User.query.delete()
# db.session.query(User).delete()

# Add users
stephen = User(first_name='Stephen', last_name="Strange",
                image_url="https://cnet2.cbsistatic.com/img/6tHYbHTMFnBTyrrGHsJuVLTGtw0=/940x0/2016/10/28/3809e66e-d3fe-46bb-963a-705d88f5a902/doctor-strange6.jpg")
bruce = User(first_name='Bruce', last_name="Wayne",
                image_url="https://www.dccomics.com/sites/default/files/BM_LKOE_gallery_5e8e64f68d9ce3.29516349.jpg")

# posts
p1 = Post(title="Dr. Strange's net worth",
          content="Estimated to be slightly less than Tony's...", user_id=1)
p2 = Post(title="Dr. Strange's ultimate sorcery",
          content="Time and space control: I can go anywhere in time or place instantly!",
          created_at=datetime.datetime(2018, 5, 10, 9, 50, 0, 0), user_id=1)
p3 = Post(title="Batman's ability", content="Batman is rich.",
          created_at=datetime.datetime(2016, 11, 10, 12, 30, 59, 0), user_id=2)

# tags
t1 = Tag(name='secret')
t1.posts.append(p2)
t1.posts.append(p3)
t2 = Tag(name='sorcery')
t2.posts.append(p2)
t3 = Tag(name='wealth')
t3.posts.append(p1)


# Add new objects to session, so they'll persist
db.session.add(stephen)
db.session.add(bruce)

db.session.add_all([p1, p2, p3])

db.session.add_all([t1, t2, t3])

# Commit--otherwise, this never gets saved!
db.session.commit()
