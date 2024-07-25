"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        user1 = User.signup("test1", "email1@email.com", "password", None)
        user1.id = 1111
        

        user2 = User.signup("test2", "email2@email.com", "password", None)
        user2.id = 2222
        

        db.session.commit()

        self.user1 = User.query.get(user1.id)
        self.user2 = User.query.get(user2.id)
        self.client = app.test_client()

    def tearDown(self):
        """Rollback session after each test"""
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    #following tests

    def test_user_follows(self):
        """Test the following functionality"""
        self.user1.following.append(self.user2)
        db.session.commit()

        self.assertEqual(len(self.user2.following), 0)
        self.assertEqual(len(self.user2.followers), 1)
        self.assertEqual(len(self.user1.following), 0)
        self.assertEqual(len(self.user1.followers), 1)

        self.assertEqual(self.user2.followers[0].id, self.user1.id)
        self.assertEqual(self.user1.following[0].id, self.user2.id)

    def test_is_following(self):
        """test is_following method"""
        self.user1.following.append(self.user2)
        db.session.commit()

        self.assertTrue(self.user1.is_following(self.user2))
        self.assertFalse(self.user2.is_following(self.user1))

    def test_is_followed_by(self):
        """Test is_followed_by method"""
        self.user1.following.append(self.user2)
        db.session.commit()

        self.assertTrue(self.user2.is_followed_by(self.user1))
        self.assertFalse(self.user1.is_followed_by(self.user2))

#signup tests
    def test_valid_signup(self):
        """test valid user signup"""
        user_test = User.signup("testtesttest", "testtest@test.com", "password", None)
        user_test.id = 99999
        db.session.commit()

        user_test = User.query.get(user_test.id)
        self.assertIsNotNone(user_test)
        self.assertEqual(user_test.username, "testtesttest")
        self.assertEqual(user_test.email, "testtest@test.com")
        self.assertNotEqual(user_test.password, "password")

        self.assertTrue(user_test.password.startswith("$2b$"))

    def test_invalid_username_signup(self):
        """test signup with invalid username"""
        invalid = User.signup(None, "test@test.com", "password", None)
        invalid.id = 123456789
        
        with self.assertRaises(exc.IntegrityError):
            db.session.commit()

    def test_invalid_email_signup(self):
        """test signup with invalid email"""
        invalid = User.signup("testtest", None, "password", None)
        invalid.id = 123098
        
        with self.assertRaises(exc.IntegrityError):
            db.session.commit()

    def test_invalid_password_signup(self):
        """test signup with invalid password"""
        with self.assertRaises(ValueError):
            User.signup("testtest", "email@email.com", "", None)

        with self.assertRaises(ValueError):
            User.signup("testtest", "email@email.com", None, None)

#Authentication Tests

    def test_valid_authentication(self):
        """test valid user authentication"""
        user = User.authenticate(self.user1.username, "password")
        self.assertIsNotNone(user)
        self.assertEqual(user.id, self.user1.id)

    def test_invalid_username(self):
        """test authentication with wrong username"""
        self.assertFalse(User.authenticate("badusername", "password"))

    def test_wrong_password(self):
        """test authentication with wrong password"""
        self.assertFalse(User.authenticate(self.user1.username, "badpassword"))


        
