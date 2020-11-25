import unittest, os, requests
from api_gateway.app import create_app
from api_gateway.classes.user import User
from datetime import datetime
from flask import Flask, session, request, make_response
from flask_wtf.csrf import generate_csrf
from api_gateway.auth import *
from api_gateway.forms import LoginForm

User.BASE_URL = f"http://{os.environ.get('GOS_USER')}"

# Some fake test endpoints


@login_required
def login_required_test():
    response = make_response()
    response.status_code = 200
    return response


@admin_required
def admin_required_test():
    response = make_response()
    response.status_code = 200
    return response


@operator_required
def operator_required_test():
    response = make_response()
    response.status_code = 200
    return response


test_endpoints = dict(login_required_test=login_required_test,
                      admin_required_test=admin_required_test,
                      operator_required_test=operator_required_test)


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
            'is_admin': True,
            'password': "user12",
            'dateofbirth': datetime(year=1996, month=1, day=3)
        }, {
            'email': "user3@test.com",
            'firstname': "user3",
            'lastname': "user3",
            'fiscal_code': "Fake3",
            'password': "user3",
            'restaurant_id': 2,
            'dateofbirth': datetime(year=1996, month=1, day=4)
        }, {
            'email': "user4@test.com",
            'firstname': "user4",
            'lastname': "user4",
            'fiscal_code': "Fake4",
            'password': "user4",
            'dateofbirth': datetime(year=1996, month=1, day=5)
        }]

        cls.app = create_app()

        for user in cls.user_list:
            User.create(**user)

        for endpoint, endpoint_func in test_endpoints.items():
            cls.app.add_url_rule(f"/{endpoint}", endpoint, endpoint_func)

    def test_login(self):
        with TestLogin.app.test_client() as client:
            for user in TestLogin.user_list:
                self.assertEqual(
                    client.post("/login",
                                content_type="application/x-www-form-urlencoded",
                                data=dict(email=user['email'], password=user['password'])).status_code, 301)
                #Now fail
                self.assertEqual(
                    client.post("/login",
                                content_type="application/x-www-form-urlencoded",
                                data=dict(email=user['email'], password=user['password'] + '1')).status_code, 401)

    def test_login_endpoint(self):
        with TestLogin.app.test_client() as client:
            resp = client.post("/login",
                               content_type="application/x-www-form-urlencoded",
                               data=dict(email=TestLogin.user_list[0]['email'],
                                         password=TestLogin.user_list[0]['password']))

            self.assertEqual(client.get("/login_required_test").status_code, 200)
        with TestLogin.app.test_client() as client:
            # New client, no cookies stored
            self.assertEqual(client.get("/login_required_test").status_code, 401)

    def test_admin_endpoint(self):
        with TestLogin.app.test_client() as client:
            #Health administrator login
            resp = client.post("/login",
                               content_type="application/x-www-form-urlencoded",
                               data=dict(email=TestLogin.user_list[1]['email'],
                                         password=TestLogin.user_list[1]['password']))

            self.assertEqual(client.get("/admin_required_test").status_code, 200)
        with TestLogin.app.test_client() as client:
            # New client, no cookies stored
            self.assertEqual(client.get("/admin_required_test").status_code, 401)
        with TestLogin.app.test_client() as client:
            # New client, login as normal user
            resp = client.post("/login",
                               content_type="application/x-www-form-urlencoded",
                               data=dict(email=TestLogin.user_list[0]['email'],
                                         password=TestLogin.user_list[0]['password']))

            self.assertEqual(client.get("/admin_required_test").status_code, 401)

    def test_operator_endpoint(self):
        with TestLogin.app.test_client() as client:
            #Operator login
            resp = client.post("/login",
                               content_type="application/x-www-form-urlencoded",
                               data=dict(email=TestLogin.user_list[2]['email'],
                                         password=TestLogin.user_list[2]['password']))

            self.assertEqual(client.get("/operator_required_test").status_code, 200)
        with TestLogin.app.test_client() as client:
            # New client, no cookies stored
            self.assertEqual(client.get("/operator_required_test").status_code, 401)
        with TestLogin.app.test_client() as client:
            # New client, login as normal user
            resp = client.post("/login",
                               content_type="application/x-www-form-urlencoded",
                               data=dict(email=TestLogin.user_list[0]['email'],
                                         password=TestLogin.user_list[0]['password']))

            self.assertEqual(client.get("/operator_required_test").status_code, 401)
