"""Seed file to make sample data for blogly db."""

from models import User, db
from app import app

# Create all tables
db.drop_all()
db.create_all()

# If table isn't empty, empty it
User.query.delete()

# Add pets
stephen = User(first_name='Stephen', last_name="Strange",
                image_url="https://cnet2.cbsistatic.com/img/6tHYbHTMFnBTyrrGHsJuVLTGtw0=/940x0/2016/10/28/3809e66e-d3fe-46bb-963a-705d88f5a902/doctor-strange6.jpg")
bruce = User(first_name='Bruce', last_name="Wayne",
                image_url="https://www.dccomics.com/sites/default/files/BM_LKOE_gallery_5e8e64f68d9ce3.29516349.jpg")

# Add new objects to session, so they'll persist
db.session.add(stephen)
db.session.add(bruce)

# Commit--otherwise, this never gets saved!
db.session.commit()
