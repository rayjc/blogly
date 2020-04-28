from unittest import TestCase
from app import app
from flask import session
from models import db, User

# Use test database and don't clutter tests with SQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly_test'
app.config['SQLALCHEMY_ECHO'] = False

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True

# This is a bit of hack, but don't use Flask DebugToolbar
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

db.drop_all()
db.create_all()


class FlaskUserTests(TestCase):

    def setUp(self):
        """Add sample user."""
        User.query.delete()

        self.user_first_name = "Test"
        self.user_last_name = "Stark"
        self.user_url = "https://upload.wikimedia.org/wikipedia/en/d/d5/Iron_Man_3_theatrical_poster.jpg"

        user = User(first_name=self.user_first_name, last_name=self.user_last_name,
                    image_url=self.user_url)
        db.session.add(user)
        db.session.commit()

        self.user_id = user.id

    def tearDown(self):
        """Clean up any fouled transaction."""

        db.session.rollback()

    def test_users_view(self):
        with app.test_client() as client:
            resp = client.get("/users")
            html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn(
            f'<a href="/users/{self.user_id}">',
            html
        )
    
    def test_get_new_user_view(self):
        with app.test_client() as client:
            resp = client.get("/users/new")
            html = resp.get_data(as_text=True)
        
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(
            all(f'<input type="text" class="form-control" id="{name}-input"' in html
                for name in {"firstname", "lastname"})
        )
        self.assertIn('<input type="url" class="form-control" id="img-url-input"', html)


    def test_post_new_user_view(self):
        with app.test_client() as client:
            resp = client.post(
                "/users/new",
                data={
                    "first_name": "Test",
                    "last_name": "User"
                }
            )
        
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, "http://localhost/users")
            self.assertTrue(
                User.query.filter_by(
                    first_name="Test", last_name="User"
                ).one()
            )

    def test_fail_post_new_user_view(self):
        with app.test_client() as client:
            resp = client.post(
                "/users/new",
                data={
                    "first_name": "Test",
                }
            )
        
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.location, "http://localhost/users/new")
    
    def test_user_detail_view(self):
        with app.test_client() as client:
            resp = client.get(f"/users/{self.user_id}")
            html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn(f'<img class="card-img-top" src="{self.user_url}"', html)
        self.assertIn(
            '<h2 class="card-title text-center">'
            f'{self.user_first_name} {self.user_last_name}</h2>', html
        )
        self.assertIn(f'<a href="/users/{self.user_id}/edit"', html)
        self.assertIn(f'<form action="/users/{self.user_id}/delete" method="POST">',
                      html)
    
    def test_get_edit_user_view(self):
        with app.test_client() as client:
            resp = client.get(f"/users/{self.user_id}/edit")
            html = resp.get_data(as_text=True)
        
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(
            all(f'<input type="text" class="form-control" id="{name}-input"' in html
                for name in {"firstname", "lastname"})
        )
        self.assertIn('<input type="url" class="form-control" id="img-url-input"', html)
        self.assertIn(
            f'<a href="/users/{self.user_id}" '
            'class="btn btn-outline-success btn-block">Cancel</a>', html
        )


    def test_post_new_user_view(self):
        with app.test_client() as client:
            resp = client.post(
                f"/users/{self.user_id}/edit",
                data={
                    "first_name": "Test",
                    "last_name": "User",
                    "image_url": "http://google.com"
                }
            )
        
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.location, f"http://localhost/users/{self.user_id}")
        self.assertTrue(
            User.query.filter_by(
                first_name="Test", last_name="User", image_url="http://google.com"
            ).one()
        )

    def test_fail_post_edit_user_view(self):
        with app.test_client() as client:
            resp = client.post(
                f"/users/{self.user_id}/edit",
                data={
                    "first_name": "Test",
                }
            )
        
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.location,
                         f"http://localhost/users/{self.user_id}/edit")

    def test_post_delete_user_view(self):
        with app.test_client() as client:
            resp = client.post(f"/users/{self.user_id}/delete")
        
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.location, f"http://localhost/users")
        self.assertFalse(User.query.get(self.user_id))

    def test_missing_post_delete_user_view(self):
        with app.test_client() as client:
            resp = client.post(f"/users/{self.user_id+100}/delete")
        
        self.assertEqual(resp.status_code, 404)
        self.assertFalse(User.query.get(self.user_id+100))
