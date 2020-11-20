import os, requests
from flask import session, request, make_response
from ..classes.user import User
from datetime import datetime
from flask_jwt_extended import set_access_cookies, decode_token
from api_gateway.auth import currently_logged_in

def login():
    # TODO: Must work with login form
    jwt_token = requests.post(f"{User.BASE_URL}/user/auth",
                              json=dict(email=request.form['email'], password=request.form['password']))
    resp = make_response()
    if jwt_token.status_code == 200:
        user_id = decode_token(jwt_token.json())['identity']
        user = User.get(id=user_id)
        user.is_authorized = True
        set_access_cookies(resp, jwt_token.json())
        resp.status_code = 200
    else:
        resp.status_code = 401
    return resp


def logout():
    # TODO: Add cookie removal and remove from currently_logged_in.
    pass