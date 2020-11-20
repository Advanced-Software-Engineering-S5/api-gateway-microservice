import unittest, os, requests
from ..app import create_app
from ..classes.user import User
from datetime import datetime
from flask import Flask, session, request

User.BASE_URL = f"http://{os.environ.get('GOS_USER')}"


class TestLogin(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user_list = [{
            'email': "user1@test.com",
            'firstname': "user1",
            'lastname': "user1",
            'fiscal_code': "Fake1",
            'password': "user1",
            'dateofbirth': datetime(year=1996, month=1, day=2)
        }, {
            'email': "user2@test.com",
            'firstname': "user2",
            'lastname': "user2",
            'fiscal_code': "Fake2",
            'password': "user12",
            'dateofbirth': datetime(year=1996, month=1, day=3)
        }, {
            'email': "user3@test.com",
            'firstname': "user3",
            'lastname': "user3",
            'fiscal_code': "Fake3",
            'password': "user3",
            'dateofbirth': datetime(year=1996, month=1, day=4)
        }, {
            'email': "user4@test.com",
            'firstname': "user4",
            'lastname': "user4",
            'fiscal_code': "Fake4",
            'password': "user4",
            'dateofbirth': datetime(year=1996, month=1, day=5)
        }]

        cls.app = create_app('sqlite:///:memory:')

        for user in cls.user_list:
            User.create(**user)

    def test_login(self):
        with TestLogin.app.test_client() as client:
            for user in TestLogin.user_list:
                self.assertEqual(
                    client.post("/login",
                                content_type="application/x-www-form-urlencoded",
                                data=dict(email=user['email'], password=user['password'])).status_code, 200)
                #Now fail
                self.assertEqual(
                    client.post("/login",
                                content_type="application/x-www-form-urlencoded",
                                data=dict(email=user['email'], password=user['password'] + '1')).status_code, 401)
