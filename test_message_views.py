"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        self.testuser_id = 1717
        self.testuser.id = self.testuser_id

        db.session.commit()

    def tearDown(self):
        """Rollback session after each test"""

        res = super().tearDown()
        db.session.rollback()
        return res

    def login_test_user(self):
        """Log in the test user"""
        
        with self.client.session_transaction() as sess:
            sess[CURR_USER_KEY] = self.testuser.id

    def test_add_message(self):
        """Can a logged-in user add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        self.login_test_user()

        with self.client as c:
            resp = c.post("/messages/new", data={"text": "Hello"})
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

    def test_add_no_session(self):
        """Is adding a message unauthorized without a session?"""
        with self.client as c:
            resp = c.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

    def test_add_invalid_user(self):
        """Is adding a message unauthorized with an invalid user?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 88332232 

        resp = c.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Access unauthorized", str(resp.data))

    def test_message_show(self):
        """Can a logged-in user view a message?"""
        m = Message(
            id = 1234,
            text="a test message",
            user_id=self.testuser_id
        )

        db.session.add(m)
        db.session.commit()

        self.login_test_user()
        with self.client as c:
            resp = c.get(f'/messages/{m.id}')
            self.assertEqual(resp.status_code, 200)
            self.assertIn(m.text, str(resp.data))
           
    def test_invalid_message_show(self):
        """Does viewing an invalid message return 404?"""
        self.login_test_user()
        with self.client as c:
            resp = c.get('/messages/777777777')

            self.assertEqual(resp.status_code, 404)

    def test_message_delete(self):
        """Can a logged-in user delete their own message?"""
        m = Message(
            id=1234, 
            text="a test message",
            user_id=self.testuser_id
        )
        db.session.add(m)
        db.session.commit()

        self.login_test_user()
        with self.client as c:
            resp = c.post("/messages/1234/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            m = Message.query.get(1234)
            self.assertIsNone(m)

    def test_unauthorized_message_delete(self):
        """Is deleting a message unauthorized for another user?"""
        unauthorized_user = User.signup(username="unauthorized-user", 
                        email="test@test.com",
                        password="password",
                        image_url=None)
        unauthorized_user.id= 32983

        m = Message(
            id=1234,
            text="a test message", 
            user_id=self.testuser_id
        )
        db.session.add_all([unauthorized_user, m])
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 32983

        resp = c.post("/messages/1234/delete", follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Access unauthorized", str(resp.data))

        m = Message.query.get(1234)
        self.assertIsNotNone(m)

    def test_message_delete_no_authentication(self):
        """Is deleting a message unauthorized without authentication?"""
        m = Message(
            id=1234,
            text="a test message",
            user_id=self.testuser_id
        )
        db.session.add(m)
        db.session.commit()

        with self.client as c:
            resp = c.post("/messages/1234/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

            m = Message.query.get(1234)
            self.assertIsNotNone(m)

            

        




        
