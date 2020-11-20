import os, requests
from flask import session, request, make_response
from ..classes.user import User
from datetime import datetime

User.BASE_URL = f"http://{os.environ.get('GOS_USER')}"


def login():
    response = requests.post(f"{User.BASE_URL}/user/auth",
                             json=dict(email=request.form['email'], password=request.form['password']))
    resp = make_response()
    if response.status_code == 200:
        resp.set_cookie('gooutsafe_jwt_token', str(response.json()))
        resp.status_code = 200
        return resp
    else:
        resp.status_code = 401
        return resp