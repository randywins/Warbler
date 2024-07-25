"""test message model"""

#python -m unittest test_message_model.py 
#run test by using command above

import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows, Likes

#enviromental variable
os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

#import app
from app import app

#create our tables
db.create_all()

class UserModelTestCase(TestCase):
    """Test case for the Message model"""

    def setUp(self):
        """Set up the test client and add sample data"""
        db.drop_all()
        db.create_all()

        self.uid = 112693
        user = User.signup("test", "testing@test.com", "password", None)
        user.id = self.uid
        db.session.commit()

        self.user = User.query.get(self.uid)

        self.client = app.test_client()

    def tearDown(self):
        """Rollback session after each test"""
        res = super().tearDown()
        db.session.rollback()
        return res
    
    def test_message_model(self):
        """Test basic functionality of the message model"""

        msg = Message(
            text="a warble",
            user_id=self.uid
        )

        db.session.add(msg)
        db.session.commit()

        self.assertEqual(len(self.user.messages), 1)
        self.assertEqual(self.user.messages[0].text, "a warble")

    def test_message_likes(self):
        """Test the likes functionality for messages"""
        msg1 = Message(
            text="a warble",
            user_id=self.uid
        )

        msg2 = Message(
            text="a test warble", 
            user_id=self.uid
        )

        another_user = User.signup("anothertest", "test@email.com", "password", None)
        another_user.id = 777
       
        db.session.add_all([msg1, msg2, another_user])
        db.session.commit()

        another_user.likes.append(msg1)

        db.session.commit()

        likes = Likes.query.filter(Likes.user_id == another_user.id).all()
        self.assertEqual(len(likes), 1)
        self.assertEqual(likes[0].message_id, msg1.id)

