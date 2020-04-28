import subprocess
from unittest import TestCase


from flask import escape

from app import app
from models import Post, User, db

# Use test database and don't clutter tests with SQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly_test'
app.config['SQLALCHEMY_ECHO'] = False

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True

# This is a bit of hack, but don't use Flask DebugToolbar
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']


class FlaskPostTests(TestCase):

    @classmethod
    def setUpClass(cls):
        db.drop_all()
        db.create_all()
        # populate test database
        with open('seed.py', "r") as f:
            exec(f.read())

    @classmethod
    def tearDownClass(cls):
        db.drop_all()

    def setUp(self):
        """Add sample post."""
        self.post_title = "Dr. Strange's Experiment"
        self.post_content = "Playing with fire"
        self.user_id = 1

        self.post = Post(title=self.post_title, content=self.post_content,
                    user_id=self.user_id)
        db.session.add(self.post)
        db.session.commit()

        self.post_id = self.post.id

    def tearDown(self):
        """Clean up any fouled transaction."""

        db.session.rollback()

    def test_user_detail_view(self):
        with app.test_client() as client:
            resp = client.get(f"/users/{self.user_id}")
            html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn(f'<a href="/posts/{self.post_id}">', html)

    def test_get_new_post_view(self):
        with app.test_client() as client:
            resp = client.get(f"/users/{self.user_id}/posts/new")
            html = resp.get_data(as_text=True)
        
        self.assertEqual(resp.status_code, 200)
        self.assertIn('<input type="text" class="form-control" id="title-input"', html)
        self.assertIn('<textarea class="form-control" rows="5" id="content-input"', html)

    def test_post_new_post_view(self):
        with app.test_client() as client:
            resp = client.post(
                f"/users/{self.user_id}/posts/new",
                data={
                    "title": "Test title",
                    "content": "test content"
                }
            )
        
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.location, f"http://localhost/users/{self.user_id}")
        self.assertTrue(Post.query.get(self.post_id))
        self.assertEqual(Post.query.get(self.post_id).user_id, self.user_id)

    def test_fail_post_new_user_view(self):
        with app.test_client() as client:
            resp = client.post(
                f"/users/{self.user_id}/posts/new",
                data={
                    "title": "Test title",
                }
            )
        
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.location, f"http://localhost/users/{self.user_id}/posts/new")

    def test_post_detail_view(self):
        with app.test_client() as client:
            resp = client.get(f"/posts/{self.post_id}")
            html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn(f'<h3 class="card-title text-center">{escape(self.post_title)}</h3>', html)
        self.assertIn(f'<p class="card-text">{escape(self.post_content)}</p>', html)
        self.assertIn(f'<h6 class="card-subtitle my-2 text-muted text-right">by {escape(self.post.user.full_name)}', html)
        self.assertIn(f'<a href="/users/{self.user_id}" class="btn btn-outline-primary">',
                      html)
        self.assertIn(f'<a href="/posts/{self.post_id}/edit" class="btn btn-primary btn-block">Edit</a>', html)
        self.assertIn(f'<button class="btn btn-danger btn-block">Delete</button>', html)

    def test_get_edit_post_view(self):
        with app.test_client() as client:
            resp = client.get(f"/posts/{self.post_id}/edit")
            html = resp.get_data(as_text=True)
        
        self.assertEqual(resp.status_code, 200)
        self.assertIn('<input type="text" class="form-control" id="title-input"', html)
        self.assertIn('<textarea class="form-control" rows="5" id="content-input"', html)
        self.assertIn(
            f'<a href="/posts/{self.post_id}" '
            'class="btn btn-outline-success btn-block">Cancel</a>', html
        )

    def test_post_edit_post_view(self):
        with app.test_client() as client:
            resp = client.post(
                f"/posts/{self.post_id}/edit",
                data={
                    "title": "Test title",
                    "content": "test content"
                }
            )
        
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.location, f"http://localhost/posts/{self.post_id}")
        self.assertTrue(Post.query.get(self.post_id))
        self.assertEqual(Post.query.get(self.post_id).user_id, self.user_id)
        self.assertEqual(Post.query.get(self.post_id).title, "Test title")
        self.assertEqual(Post.query.get(self.post_id).content, "test content")

    def test_fail_post_edit_user_view(self):
        with app.test_client() as client:
            resp = client.post(
                f"/posts/{self.post_id}/edit",
                data={
                    "title": "Test title",
                }
            )
        
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.location, f"http://localhost/posts/{self.post_id}/edit")

    def test_post_delete_post_view(self):
        with app.test_client() as client:
            resp = client.post(f"/posts/{self.post_id}/delete")
        
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.location, f"http://localhost/users/{self.user_id}")
        self.assertFalse(Post.query.get(self.post_id))

    def test_missing_post_delete_user_view(self):
        invalid_id = self.post_id + 100
        with app.test_client() as client:
            resp = client.post(f"/posts/{invalid_id}/delete")
        
        self.assertEqual(resp.status_code, 404)
        self.assertFalse(Post.query.get(invalid_id))
